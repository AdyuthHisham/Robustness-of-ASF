# Frame Deletion — Independent Verification Report

**Date:** 2026-07-30
**Scope:** `radar_frame_deletion`, `lidar_frame_deletion`, `camera_frame_deletion`, `_frame_deletion_check`, `NoiseInjector.should_skip`, `NoiseInjector.__call__` in `repos/K-Radar/datasets/effects/noise_injection.py`
**Method:** Independent standalone test script (`/tmp/verify_frame_deletion.py`, not committed) run against the current on-disk code via `repos/K-Radar/.venv/bin/python`. Not derived from `test_noise_injection.py` or `smoke_test_taxonomy.py` — built from scratch by reading the source directly.

---

## Summary verdict

| Item | Verdict |
|---|---|
| Deterministic mode — interval sub-mode (radar/lidar/camera) | **PASS** |
| Deterministic mode — index_list sub-mode | **PASS** |
| Deterministic mode — off-by-one at frame 0 / frame 29 | **PASS** |
| Deterministic mode — out-of-range index in `index_list` | **PASS** (silently ignored, no crash) |
| Random mode — rate plausibility, reproducibility, seed divergence | **PASS** |
| Per-modality data clearing (radar `rdr_sparse`/`rdr_polar_3d`→None, lidar `ldr64`→None, camera zero-tensor, `pc100p` untouched) | **PASS** |
| `should_skip()` / `__call__()` single source of truth | **FAIL** — see below |
| `__call__(frame_index=...)` kwarg actually drives deletion | **FAIL** — dead parameter for the effect-application path |
| Test coverage: does existing suite test the should_skip-then-call sequence that the design doc recommends? | **GAP** — not covered, and it's the combination that breaks |

**Overall: frame_deletion's core per-function mechanics are correct and match the design doc's parameter semantics. However, the `should_skip()` pre-check is NOT interchangeable with the actual `__call__()` decision under the documented "call should_skip before loading" usage pattern for random mode — they silently diverge. This is a real correctness bug, not a documentation nit.**

---

## 1. Deterministic mode

### 1.1 Parameter names and format (quoted, `noise_injection.py:73-101`)

```python
def _frame_deletion_check(params: dict, rng: np.random.Generator,
                           frame_index: int | None = None) -> bool:
    """Return True if this frame should be deleted (decider shared by all modalities).

    Parameters (from params dict):
        mode : str — 'deterministic' or 'random' (default: 'random')
        interval : int — delete every Nth frame (mode='deterministic', no index_list)
        index_list : list[int] — explicit indices to delete (mode='deterministic')
        p : float — per-frame deletion probability (mode='random', default: 0.1)
        frame_index : int | None — caller-provided frame index for deterministic mode
    """
    mode = params.get("mode", "random")
    if mode == "deterministic":
        index_list = params.get("index_list", None)
        if index_list is not None:
            # index_list mode: delete if frame_index is in the list
            if frame_index is None:
                # Can't check list without frame_index — don't delete (graceful skip)
                return False
            return int(frame_index) in index_list
        else:
            # interval mode: delete every Nth frame
            interval = params.get("interval", 10)
            if frame_index is None:
                return False  # no frame index available — don't delete
            return int(frame_index) % interval == 0
    else:  # 'random'
        p = params.get("p", 0.1)
        return rng.uniform() < p
```

- **Mode selector:** `params["mode"]`, values `"deterministic"` or `"random"`, default `"random"`.
- **Deterministic sub-mode selector:** `index_list` presence wins over `interval`. If `params.get("index_list")` is not `None`, interval is ignored entirely — the code never checks both.
- **`interval`:** int, every Nth frame, `frame_index % interval == 0`. Default 10 if omitted.
- **`index_list`:** `list[int]`, explicit indices, checked via Python `in` (membership test, not a range/set lookup).

### 1.2 index_list semantics (established from code + empirical test)

- **0-indexed, global.** The frame index comes from `dict_item['meta']['idx'][modality]` (see `_get_modality_idx`, `noise_injection.py:61-65`), which the K-Radar dataset populates as a plain integer per-frame counter — there is no re-basing to 1-indexed or per-subsequence-relative values anywhere in `noise_injection.py`. (I did not find dataset-loader code that resets this counter per sub-sequence; if such re-basing exists upstream in `dataset.__getitem__`, it is outside this module and outside the scope of what `_frame_deletion_check` can control — it simply consumes whatever integer it's given.)
- **Sort-independence confirmed empirically.** `index_list=[29, 5, 0, 13]` (unsorted) produced identical deleted-frame set `[0, 5, 13, 29]` as the sorted equivalent — the code performs `int(frame_index) in index_list`, an unordered membership test. The list is never sorted internally, but it doesn't need to be.
- **Out-of-range handling: silently ignored, no error.** `index_list=[5, 100, 29]` against a 30-frame sequence produced deleted frames `[5, 29]` — index 100 simply never matched any real `frame_index` and caused no crash, no warning, no log message. This is permissive-by-omission, not validated.

### 1.3 Empirical results (30-frame simulated sequence, direct function calls, no injector)

```
radar_frame_deletion interval=10 -> deleted frames: [0, 10, 20]
  frame 0 in deleted=True, frame 29 in deleted=False

lidar_frame_deletion index_list=[0, 5, 13, 29] -> deleted frames: [0, 5, 13, 29]   (exact match)
lidar_frame_deletion index_list=[29, 5, 0, 13] (unsorted) -> deleted frames: [0, 5, 13, 29]  (exact match)
lidar_frame_deletion index_list=[5, 100, 29]  -> deleted frames: [5, 29]   (100 silently ignored)

camera_frame_deletion interval=7 -> deleted (blacked) frames: [0, 7, 14, 21, 28]

interval=1 (should delete every frame) -> deleted frames: [0..29] (all 30, exact match)
```

No off-by-one error: `frame_index % interval == 0` correctly includes frame 0 (index 0 is always "the 0th multiple") and correctly excludes frame 29 when `interval=10` (29 % 10 = 9 ≠ 0). At `interval=1`, all 30 frames including 0 and 29 are deleted, confirming the modulo boundary logic is sound at both ends.

**Test-detection note:** my first pass at detecting a "deleted" camera frame used `tensor.min() < -1.5`, which is unreliable — a clean `torch.randn(3,8,8)` frame has ~192 standard-normal samples and will spuriously dip below -1.5 by chance. Corrected to check that each of the 3 channels has exactly zero variance (a genuine all-constant zero-tensor signature), which eliminated the false positives. Flagging this because it's the kind of test-methodology bug that could produce a false PASS/FAIL in any ad hoc verification of this effect — worth keeping in mind if `smoke_test_taxonomy.py`'s camera checks ever use a similar threshold (its actual checks use `min < -1.5` too, per the smoke test report table — see §6 gap note).

---

## 2. Random mode

### 2.1 Parameter format

`params["mode"] = "random"` (or omitted, since `"random"` is the default), `params["p"]` (float, per-frame deletion probability, default 0.1). Decision: `rng.uniform() < p`, where `rng` is the effect's dedicated sub-generator (see §4).

### 2.2 Methodology

30-frame simulated sequence, `p=0.2`, `NoiseInjector` configured with `Effect("frame_deletion", p=1.0, params={"mode": "random", "p": 0.2})` on radar, seeds 0–4. Binomial std dev for n=30, p=0.2 is √(30·0.2·0.8) ≈ 2.19, giving a 2-sigma band of roughly 1.6–10.4 deletions.

### 2.3 Actual results (all 5 seeds)

```
seed=0: deleted=[7, 8, 10, 14, 25, 27]        count=6  rate=0.200
seed=1: deleted=[0, 1, 3, 8, 23, 25]          count=6  rate=0.200
seed=2: deleted=[5, 7, 9, 10, 11, 21, 29]     count=7  rate=0.233
seed=3: deleted=[3, 9, 16, 17, 20, 24]        count=6  rate=0.200
seed=4: deleted=[6, 7, 16, 20, 24, 25]        count=6  rate=0.200
```

All 5 seeds land at count 6 or 7 (rate 0.20–0.233), comfortably inside the 2-sigma band (1.6–10.4). Plausible.

Reproducibility: two independently-constructed `NoiseInjector(EffectConfig(seed=0, ...))` instances produced **identical** deleted-frame lists (`[7, 8, 10, 14, 25, 27]` both times). Different seeds produced different sets (confirmed — no two of the 5 seed-sets above are identical). Both properties **PASS**.

---

## 3. `should_skip()` / `__call__()` — NOT a single source of truth in practice

### 3.1 The dispatch code (quoted)

```python
def should_skip(self, frame_index: int, modality: str) -> bool:
    effect_list = {
        "radar": self._radar_effects,
        "lidar": self._lidar_effects,
        "camera": self._camera_effects,
    }.get(modality, [])
    for name, fn, p, params, sub_rng in effect_list:
        if name == "frame_deletion" and sub_rng.uniform() < p:
            if _frame_deletion_check(params, sub_rng, frame_index):
                return True
    return False
```

```python
def _apply_list(self, d, effects, frame_index=None):
    for name, fn, p, params, sub_rng in effects:
        if sub_rng.uniform() < p:
            if name == "frame_deletion":
                params = dict(params)
                params["_caller_frame_index"] = frame_index
            d = fn(d, params, sub_rng)
    return d
```

Both paths call `_frame_deletion_check` — that half of "single source of truth" holds: there is exactly one deletion-decision function, no duplicated logic. **But** both paths draw from the **same stored `sub_rng` object** (`self._radar_effects[i][4]`, one persistent generator per configured effect, created once in `_resolve()` and never reset). For random mode, each of `should_skip()` and `_apply_list()`/`fn()` consumes **two** draws from that shared generator per invocation (one for the outer per-effect `p`-gate, one inside `_frame_deletion_check` for the inner random-mode `p`). Calling `should_skip()` and then later `__call__()` for the *same logical frame* does not re-use the same draw — it consumes two *more*, independent, draws. The two calls are therefore asking the same RNG two different, sequential questions, not the same question twice.

### 3.2 Confirmed bug: dead `frame_index` kwarg for `__call__`

```python
if name == "frame_deletion":
    params = dict(params)
    params["_caller_frame_index"] = frame_index
d = fn(d, params, sub_rng)
```

`_caller_frame_index` is injected into `params` but **no function in the file ever reads that key** — `_frame_deletion_check` only reads `params["mode"]`, `params["index_list"]`, `params["interval"]`, `params["p"]`. Meanwhile `radar_frame_deletion` (etc.) independently computes its own `frame_index` via `_get_modality_idx(dict_item, "rdr")`, reading `dict_item['meta']['idx']['rdr']` — **not** the `frame_index` argument passed into `NoiseInjector.__call__(dict_item, frame_index=idx)` at all.

Empirical confirmation (`/tmp/verify_frame_deletion.py`, Task 3b):

```
Case A: meta idx=3, __call__(frame_index=3)   -> ldr64 is None: True   (both agree, no signal)
Case B: meta idx=3 (in list), __call__(frame_index=999, NOT in list) -> ldr64 is None: True
Case C: meta idx=999 (not in list), __call__(frame_index=3, in list)  -> ldr64 is None: False
```

Case B and C prove the `frame_index` kwarg to `NoiseInjector.__call__` is **entirely unused** by the deterministic effect-application path — deletion is driven solely by `dict_item['meta']['idx'][modality]`, which must be populated correctly by the caller/dataset independently of whatever is passed to `__call__(frame_index=...)`. The existing test `test_injector_frame_deletion_index_list` in `test_noise_injection.py` (lines 886–905) does not catch this because it always sets `ldr_frame_idx` in the dict AND passes the matching `frame_index` to `__call__` — the two never disagree in that test, so the dead parameter is invisible there.

**This is a real discrepancy from the design doc**, which states (`noise-injection-design.md` §2.2, `__call__` docstring): *"If frame_index is provided, deterministic frame_deletion (interval / index_list) can use it."* In the current implementation it is not used at all for the actual deletion decision — only `should_skip()` uses its `frame_index` argument directly.

### 3.3 Confirmed bug: should_skip pre-check diverges from actual `__call__` outcome (random mode)

Simulated the exact recommended usage pattern from `noise-injection-design.md` §3 ("Frame deletion integration": *"the eval script SHOULD call `injector.should_skip(idx, modality)` before loading each frame"*) — calling `should_skip(i, "radar")` immediately before `injector(dict_item, frame_index=i)` for every `i` in a 30-frame sequence, radar `frame_deletion` configured with `mode="random", p=0.2`, seed=7:

```
frame 10: should_skip=True   actually_deleted=False  MISMATCH
frame 18: should_skip=True   actually_deleted=False  MISMATCH
frame 19: should_skip=True   actually_deleted=False  MISMATCH
frame 21: should_skip=True   actually_deleted=False  MISMATCH
frame 29: should_skip=True   actually_deleted=False  MISMATCH

Total mismatches: 5/30
```

Every mismatch is the same direction: `should_skip()` said "delete" but `__call__()` did not delete. (The reverse — `should_skip=False` but `__call__` deletes anyway — is also possible in general, just didn't occur in this particular 30-draw run; the mechanism is symmetric.) This is because each `should_skip()` call burns 2 draws from the shared per-effect `sub_rng`, so the RNG state that `__call__` later sees for "the same" frame index is not the state `should_skip` evaluated — it's whatever state is left after `should_skip` was called for every earlier frame too.

**Practical impact:** any eval script that follows the design doc's own recommendation (call `should_skip` first to skip loading, otherwise proceed to `__call__`) will get **silently incorrect** behavior in random mode: frames the pre-check said were safe to load can still get deleted by `__call__`, and — more seriously — if the script actually skips loading based on `should_skip()`, the frames it thinks were "deleted" per the pre-check were never verified against what `__call__` would have done, because `__call__` is never invoked for skipped frames to check agreement. This is invisible in tests that call `should_skip()` and `__call__()` independently (as the existing suite does) rather than interleaved in the documented sequence.

Deterministic mode does **not** have this problem: `_frame_deletion_check`'s deterministic branch doesn't consume `rng` at all (it's pure arithmetic on `frame_index`), so repeated calls are idempotent regardless of RNG state — only the outer per-effect `p`-gate draw is consumed, and since `Effect.p` is typically `1.0` for frame_deletion in every example config found, that gate always passes and consumes exactly one draw per call, which doesn't matter for a deterministic decision. **The bug is specific to random-mode frame_deletion combined with should_skip pre-checking.**

---

## 4. Per-modality data clearing — re-verified against current code

Quoted directly from the current file (matches what's already documented, and confirms the pc100p removal referenced in the recent uncommitted-work docs is real and current):

```python
def radar_frame_deletion(dict_item, params, rng):
    frame_index = _get_modality_idx(dict_item, "rdr")
    if _frame_deletion_check(params, rng, frame_index):
        _set_none(dict_item, ["rdr_sparse", "rdr_polar_3d"])
    return dict_item

def lidar_frame_deletion(dict_item, params, rng):
    frame_index = _get_modality_idx(dict_item, "ldr")
    if _frame_deletion_check(params, rng, frame_index):
        _set_none(dict_item, ["ldr64"])
    return dict_item

def camera_frame_deletion(dict_item, params, rng):
    frame_index = _get_modality_idx(dict_item, "cam")
    if _frame_deletion_check(params, rng, frame_index):
        for k in _camera_keys(dict_item):
            dict_item[k] = _zero_camera_tensor(dict_item[k])
    return dict_item
```

Empirical confirmation:

```
radar_frame_deletion clears: rdr_sparse=None, rdr_polar_3d=None
pc100p touched by radar_frame_deletion: False   (pc100p present, unmodified)
lidar_frame_deletion clears: ldr64=None
camera_frame_deletion: front0 per_channel_std=[0.0, 0.0, 0.0]  (uniform per channel -> zero-tensor, key stays present, not None)
```

**Design Decision #3 still holds, current code, post pc100p-removal:** radar clears exactly `rdr_sparse` + `rdr_polar_3d` (no longer `pc100p` — confirmed absent from `_set_none` calls, consistent with `docs/vAIlt/loss-partial-report-correction-log.md`'s finding that the pc100p removal was real, if uncommitted, work). LiDAR clears `ldr64` only. Camera replaces image tensors with a zero-filled normalized tensor (key stays present, set to a constant-per-channel value, never `None`) — this asymmetry (radar/lidar → `None`, camera → zero-tensor, never `None`) is intentional per the design doc and confirmed unchanged in the current code.

---

## 5. Test coverage gap analysis

`smoke_test_taxonomy.py` and `test_noise_injection.py` both exercise:
- Deterministic interval mode (radar, lidar, camera)
- Deterministic index_list mode (radar, lidar — **not explicitly listed for camera** in the smoke report's R1/L1/C1 rows, though `camera_frame_deletion` shares the same `_frame_deletion_check`)
- Random mode at `p=1.0` and `p=0.0` (boundary values only — not a mid-range `p` with a rate check across multiple seeds)
- `should_skip()` in isolation, at fixed frame indices (0, 5, 10), never interleaved with `__call__()` on the same injector instance

**Gaps found:**
1. **No test anywhere calls `should_skip()` and `__call__()` in sequence on the same `NoiseInjector` for the same set of frame indices** — which is exactly the usage pattern the design doc recommends, and exactly the combination that produces the divergence documented in §3.3. This is the most consequential gap: the existing 103+96 "all PASS" test counts do not cover the failure mode found here at all.
2. **No test constructs a scenario where `dict_item['meta']['idx'][modality]` and the `frame_index` argument to `__call__()` disagree** — which is what exposed the dead `_caller_frame_index` parameter in §3.2. Every existing test keeps them in sync, so the dead code path is untested and unnoticed.
3. Random mode is only tested at `p ∈ {0.0, 1.0}` — no mid-range statistical-rate test across multiple seeds exists in the repo's own suite (this report's §2 fills that gap independently, but it isn't in `test_noise_injection.py`/`smoke_test_taxonomy.py` itself).
4. No test exercises an out-of-range `index_list` entry (this report's §1.2 out-of-range case is new coverage).

None of the existing "12 effects, 96/103 checks, all PASS" claims in `noise-injection-smoke-test-report.md` or `noise-injection-taxonomy-revision-report.md` are wrong for what they actually test — but they don't test the should_skip+call interaction, so their "all PASS" status does not extend to the bug found in §3.3.

---

## 6. Discrepancies found (documented, NOT fixed)

| # | Discrepancy | Location | Severity |
|---|---|---|---|
| 1 | `NoiseInjector.__call__`'s `frame_index` kwarg is injected into `params["_caller_frame_index"]` but never read by any function — dead parameter. Deterministic frame_deletion via `__call__` is driven solely by `dict_item['meta']['idx'][modality]`, contradicting the design doc's claim that the `frame_index` argument "can use it." | `noise_injection.py:566-568` (`_apply_list`), design doc §2.2 | Medium — misleading API, works today only because callers happen to keep the two in sync |
| 2 | `should_skip()` and the actual `__call__()`/effect-function path share one persistent per-effect `sub_rng`, and each consumes 2 draws (outer p-gate + inner random check) per invocation. Calling `should_skip()` before `__call__()` for every frame (the documented recommended pattern) desynchronizes the RNG state between the pre-check and the real decision, causing genuine mismatches in random mode (5/30 in the reproduced run). | `noise_injection.py:598-621` (`should_skip`), `noise_injection.py:551-569` (`_apply_list`) | **High** — silent incorrect behavior under the officially recommended usage pattern for random-mode frame_deletion |
| 3 | Out-of-range `index_list` entries are silently ignored (no validation, no warning) — acceptable behavior but undocumented as a design choice anywhere in the design doc's parameter table. | `noise_injection.py:86-93` | Low — works as one would hope, just unstated |

Item 2 is the significant finding of this verification. It does not manifest in the existing test suite because no test interleaves `should_skip()` and `__call__()` calls on a shared injector across a frame sequence — every existing test either uses only `should_skip()` or only direct function calls / a single `__call__()`, never both against a running sequence.

---

## Files referenced

- `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/noise_injection.py`
- `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/config.py`
- `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/test_noise_injection.py`
- `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/smoke_test_taxonomy.py`
- `/home/adhish/Productivity/AMSCUP/repos/K-Radar/configs/noise_injection_smoke_test.yml`
- `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-design.md`
- `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-taxonomy-revision-report.md`
- `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-injection-smoke-test-report.md`
- `/home/adhish/Productivity/AMSCUP/docs/vAIlt/loss-partial-report-correction-log.md`
- `/home/adhish/Productivity/AMSCUP/docs/vAIlt/loss-partial-zeroout-visibility-diagnostic.md`
- Standalone test script (not committed): `/tmp/verify_frame_deletion.py`
