# Frame Deletion — RNG Desync Fix Report

**Date:** 2026-07-30
**Fixes:** Discrepancy #2 (High) and Discrepancy #1 (Medium) from `frame-deletion-verification-report.md` §6.
**File changed:** `repos/K-Radar/datasets/effects/noise_injection.py`
**Doc changed:** `docs/vAIlt/noise-injection-design.md` (§2.2, `__call__` docstring)
**Tests changed:** `repos/K-Radar/datasets/effects/test_noise_injection.py`

---

## 1. Bug recap (Discrepancy #2)

`NoiseInjector.should_skip()` and `NoiseInjector.__call__()`/`_apply_list()` both consulted `_frame_deletion_check()` for random-mode `frame_deletion`, but each call drew from the *same* persistent per-effect `sub_rng` independently — two draws per invocation (outer per-effect `p`-gate + inner random-mode `p`). Calling `should_skip(i, "radar")` immediately before `injector(d, frame_index=i)` for the same `i` (the design doc's own recommended usage) consumed 4 draws for what should have been one logical decision, so the two call sites silently disagreed. Verification report §3.3 reproduced 5/30 mismatches at seed=7, `p=0.2`.

## 2. Fix implementation

Added a decision cache to `NoiseInjector`, keyed by `(modality, frame_index)`:

- **`should_skip()`** now computes its decision exactly as before (same draw pattern, same result), but additionally stores the boolean result in `self._skip_cache[(modality, frame_index)]` before returning. Guarded so a modality with no configured `frame_deletion` effect never gets a cache entry written (nothing would ever consume it).
- **`_apply_list()`** now takes an additional `modality` argument. For a `frame_deletion` entry, it checks `self._skip_cache` for `(modality, frame_index)` *before* touching `sub_rng`. On a hit, it pops the entry and replays the cached decision directly — via a new `NoiseInjector._apply_cached_frame_deletion()` static helper that clears the same keys as `radar_frame_deletion`/`lidar_frame_deletion`/`camera_frame_deletion` (reusing shared `_RADAR_FRAME_DELETION_KEYS` / `_LIDAR_FRAME_DELETION_KEYS` constants and the existing `_camera_keys`/`_zero_camera_tensor` helpers) — without drawing any rng at all. On a miss (the pre-fix, and still the default, path), behavior is byte-for-byte unchanged: gate draw, then `fn(d, params, sub_rng)`.
- Added `NoiseInjector.clear_skip_cache()` as an explicit reset escape hatch (see §3).

This guarantees: if `should_skip(i, modality)` is called for a frame and `__call__(d, frame_index=i)` is later invoked for that same frame, `__call__` replays the *exact* decision `should_skip` already made — no independent draw, so no possibility of disagreement. Multiple `frame_deletion` effects configured on the same modality (not used anywhere in the current codebase/configs) still share the pre-existing limitation that `should_skip()`'s early-return-on-first-True doesn't individually track every entry; this is unchanged from before the fix and out of scope (no config in the repo does this).

## 3. Cache lifecycle decision

**Persists for the injector's lifetime**, mirroring the per-effect `sub_rng` streams (also never reset mid-lifetime, by existing design). Rationale:

- The normal `should_skip()` → `__call__()` sequence self-cleans: each cache entry is popped the moment `__call__()` consumes it, so under the documented "check then maybe call" pattern, the cache never holds more than a handful of live entries at once.
- The cache only accumulates when `should_skip()` returns `True` and the caller — following the design doc's own recommendation — deliberately never calls `__call__()` for that frame (skips loading entirely). That's an intentional, sanctioned usage pattern, not a bug, and its growth is bounded by `frames_visited x deletion_rate` (e.g. a full-dataset single pass at `p=0.1-0.2` leaves a cache on the order of 10-20% of the dataset size in entries, each a `(str, int) -> bool` tuple — negligible, kilobytes even for large datasets).
- Since RNG state itself is already a single continuous stream for the injector's whole life (not reset per-epoch/per-sequence by any existing code), giving the cache the same lifetime avoids inventing a new, inconsistent reset semantic.
- For callers that revisit the same frame indices many times without ever calling `__call__` (e.g. an unusual training-loop-style repeated `should_skip`-only pass), `clear_skip_cache()` is provided as an explicit, opt-in reset — not called automatically anywhere, since there's no epoch/sequence boundary the class can observe on its own.

## 4. Discrepancy #1 resolution (dead `frame_index` kwarg)

Chose to **correct the design doc** rather than wire the kwarg into the deterministic decision path. Rationale:

- Making effect functions read `params["_caller_frame_index"]` would change the deterministic frame-deletion decision path (currently driven solely by `dict_item['meta']['idx'][modality]`), which the verification report confirmed is correct and exercised by the existing 103+96 passing tests. Any change there is exactly the kind of "verified working" code the task explicitly says not to touch.
- The kwarg is genuinely unused today only for the effect-application path; `should_skip()` already uses its own `frame_index` argument directly, and the new cache-key plumbing in `__call__`/`_apply_list` now gives `frame_index` a real (if narrower) purpose — keying the should_skip/`__call__` consistency cache — so it's not entirely vestigial post-fix.
- Updated `docs/vAIlt/noise-injection-design.md` §2.2's `__call__` docstring to state plainly that deterministic frame_deletion reads `dict_item['meta']['idx'][modality]`, not the `frame_index` argument, and to note the argument's actual current role (cache key).

## 5. Test coverage added

`test_noise_injection.py`, three new checks in the injector-integration section:

1. **`test_injector_should_skip_then_call_random_mode_consistency`** — the exact §3.3 reproduction: radar `frame_deletion`, `mode=random, p=0.2`, seed=7, 30 frames, `should_skip(i, "radar")` immediately followed by `injector(d, frame_index=i)` for every `i`. Asserts 0/30 mismatches. Verified this test fails (caught 7/30 mismatches at seed=7 in this environment's numpy version — RNG-implementation-dependent exact count, but nonzero) when the fix is reverted, confirming it actually detects the bug.
2. **`test_injector_should_skip_cache_does_not_leak_across_frame_indices`** — cached decisions are per-`(modality, frame_index)`, not global.
3. **`test_injector_call_only_unaffected_by_skip_cache`** — two fresh injectors with identical config/seed that only ever use `__call__()` (never `should_skip()`) produce identical decisions across 20 frames, and the skip cache stays empty — confirms the fix is a strict no-op for the existing tested path.

All three appended to the `__main__` runner list so they run under both `python test_noise_injection.py` and ad hoc `pytest` collection (pytest collection requires the `datasets/__init__.py`/`datasets/effects/__init__.py` package-import chain to be bypassed in this sandboxed environment due to missing `open3d`/`scipy`/`tqdm`/`matplotlib`/`easydict`; the tests themselves have no such dependency and pass identically under direct script execution, which is this module's own designed invocation mode per its docstring).

## 6. Before/after results

| Suite | Before (pre-existing) | After |
|---|---|---|
| `test_noise_injection.py` | 113 checks, all PASS | **120 checks, all PASS** (+7 new) |
| `smoke_test_taxonomy.py` | 96 checks, all PASS | 96 checks, all PASS (unchanged — no `should_skip`+`__call__` interleaving in this suite) |
| `scripts/smoke_test_integration.py` | 38 checks, all PASS | 38 checks, all PASS (unchanged) |
| §3.3 reproduction (seed=7, p=0.2, 30 frames, interleaved) | 5-7/30 mismatches (RNG-impl-dependent) | **0/30 mismatches** |

Zero regressions across all three suites (247 pre-existing checks all still pass); the fix is additive.

## 7. Files touched

- `repos/K-Radar/datasets/effects/noise_injection.py` — `NoiseInjector.__init__` (added `self._skip_cache`), `NoiseInjector.clear_skip_cache()` (new), `NoiseInjector._apply_cached_frame_deletion()` (new), `NoiseInjector._apply_list()` (cache consult + `modality` param), `NoiseInjector.__call__()` (passes modality strings), `NoiseInjector.should_skip()` (writes cache), plus two new module-level constants `_RADAR_FRAME_DELETION_KEYS`/`_LIDAR_FRAME_DELETION_KEYS` shared between `radar_frame_deletion`/`lidar_frame_deletion` and the new cached-replay path.
- `repos/K-Radar/datasets/effects/test_noise_injection.py` — 3 new test functions + `__main__` registration.
- `docs/vAIlt/noise-injection-design.md` — `__call__` docstring corrected (§2.2).

Not touched, per task scope: deterministic mode's own decision logic, per-modality data-clearing key sets (only referenced via new shared constants, not changed), `loss_partial`, `loss_complete`, `gaussian_noise`, `noise_induced_shifts`, and all training-path code.
