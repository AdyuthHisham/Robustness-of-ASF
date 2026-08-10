# frame_deletion vs loss_complete — Mechanical, Semantic, and Downstream-Signal Comparison

**Date:** 2026-07-30
**Scope:** `radar_frame_deletion` vs `radar_loss_complete`, `lidar_frame_deletion` vs `lidar_loss_complete`, `camera_frame_deletion` vs `camera_loss_complete`, plus `NoiseInjector._apply_list()` / `should_skip()` dispatch, in `repos/K-Radar/datasets/effects/noise_injection.py`.
**Method:** Direct reading of the current on-disk implementation (line numbers cited below). Cross-checked against `noise-injection-design.md` (Rev 2 taxonomy, §1.4), `noise-injection-taxonomy-revision-report.md`, `frame-deletion-verification-report.md`, `frame-deletion-rng-desync-fix-report.md`, and the R3vR4-Distinct / camera-identity findings in `noise-injection-param-sweep-report.md`.

**This report is about a different pair than the existing loss_partial-vs-loss_complete comparison.** That comparison (documented in the param-sweep report and design §1.4) is about *within-modality partial vs total* loss. This report is about *frame_deletion vs loss_complete* — two effects that can both zero out a modality's data entirely, but via different trigger mechanisms and (the design doc claims) different semantic intent. Do not conflate the two.

---

## 1. Quoted implementations

### 1.1 Radar

```python
# noise_injection.py:112-125
_RADAR_FRAME_DELETION_KEYS = ["rdr_sparse", "rdr_polar_3d"]

def radar_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """R1 — Radar frame deletion (deterministic or random).

    When fired, sets ``rdr_sparse`` and ``rdr_polar_3d`` to None.
    Frame index read from ``dict_item['meta']['idx']['rdr']`` for deterministic mode.
    """
    frame_index = _get_modality_idx(dict_item, "rdr")
    if _frame_deletion_check(params, rng, frame_index):
        _set_none(dict_item, _RADAR_FRAME_DELETION_KEYS)
    return dict_item
```

```python
# noise_injection.py:213-223
def radar_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """R4 — Full radar data blackout for this frame.

    Sets ``rdr_sparse`` and ``rdr_polar_3d`` to None.
    Semantically distinct from ``loss_partial(fraction=1.0)`` — this
    represents a total sensor blackout, not extreme sampling.

    Parameters: (none required)
    """
    _set_none(dict_item, ["rdr_sparse", "rdr_polar_3d"])
    return dict_item
```

### 1.2 LiDAR

```python
# noise_injection.py:113, 231-240
_LIDAR_FRAME_DELETION_KEYS = ["ldr64"]

def lidar_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """L1 — LiDAR frame deletion.

    When fired, sets ``ldr64`` to None.
    Frame index read from ``dict_item['meta']['idx']['ldr']``.
    """
    frame_index = _get_modality_idx(dict_item, "ldr")
    if _frame_deletion_check(params, rng, frame_index):
        _set_none(dict_item, _LIDAR_FRAME_DELETION_KEYS)
    return dict_item
```

```python
# noise_injection.py:307-315
def lidar_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """L4 — Full LiDAR blackout.

    Sets ``ldr64`` to None.

    Parameters: (none required)
    """
    _set_none(dict_item, ["ldr64"])
    return dict_item
```

### 1.3 Camera

```python
# noise_injection.py:360-371
def camera_frame_deletion(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """C1 — Camera frame deletion.

    When fired, all camera-image keys are replaced with a zero-filled
    normalized tensor (black frame). Frame index read from
    ``dict_item['meta']['idx']['cam']``.
    """
    frame_index = _get_modality_idx(dict_item, "cam")
    if _frame_deletion_check(params, rng, frame_index):
        for k in _camera_keys(dict_item):
            dict_item[k] = _zero_camera_tensor(dict_item[k])
    return dict_item
```

```python
# noise_injection.py:439-448
def camera_loss_complete(dict_item: dict, params: dict, rng: np.random.Generator) -> dict:
    """C4 — Full image blackout.

    Replaces all camera-image tensors with zero-filled normalized tensors.

    Parameters: (none required)
    """
    for k in _camera_keys(dict_item):
        dict_item[k] = _zero_camera_tensor(dict_item[k])
    return dict_item
```

### 1.4 Shared trigger logic (`frame_deletion` only)

```python
# noise_injection.py:73-101
def _frame_deletion_check(params: dict, rng: np.random.Generator,
                           frame_index: int | None = None) -> bool:
    mode = params.get("mode", "random")
    if mode == "deterministic":
        index_list = params.get("index_list", None)
        if index_list is not None:
            if frame_index is None:
                return False
            return int(frame_index) in index_list
        else:
            interval = params.get("interval", 10)
            if frame_index is None:
                return False
            return int(frame_index) % interval == 0
    else:  # 'random'
        p = params.get("p", 0.1)
        return rng.uniform() < p
```

`loss_complete` has no equivalent function. It has no `params` fields at all ("Parameters: (none required)" in both the docstrings and design doc §1.1/1.2/1.3) and calls `_set_none`/`_zero_camera_tensor` unconditionally, every time it is invoked (subject only to the outer per-effect `p` gate applied by `NoiseInjector._apply_list`, identical to how every other effect is gated — see §3 below).

---

## 2. Trigger condition — verified directly

| | `frame_deletion` | `loss_complete` |
|---|---|---|
| Decision function | `_frame_deletion_check()` — reads `params["mode"]`, and either `index_list`, `interval`, or `p` | none — no per-effect decision function exists |
| Inputs it depends on | `dict_item['meta']['idx'][modality]` (deterministic modes) or the effect's dedicated `sub_rng` (random mode) | nothing — the function body has no conditional at all |
| Can decline to fire (given the outer `p`-gate passes)? | Yes — `_frame_deletion_check` can return `False` (e.g. frame not in `index_list`, `frame_index % interval != 0`, or `rng.uniform() >= p`) | No — once the function executes, the clear is unconditional |
| Confirmed by | direct code read above; also confirmed empirically in `noise-injection-param-sweep-report.md`: *"`loss_complete` is confirmed to have no meaningful severity axis (garbage/ignored params don't change its always-full-clear behavior)."* | same |

One caveat, confirmed by re-reading `NoiseInjector._apply_list` (`noise_injection.py:619-633`): **every** configured effect, `loss_complete` included, is still subject to the per-effect outer probability gate `Effect.p` (`if sub_rng.uniform() < p`) before its function is even called — this is generic to all 12 effects, not specific to `frame_deletion`. So "unconditional" means unconditional *given the effect fires at all* — i.e., once `Effect.p` passes and `loss_complete`'s function body runs, there is no further internal check that could cause it to no-op, unlike `frame_deletion` whose function body can still evaluate to "don't delete" after being invoked. This is the precise distinction: `frame_deletion`'s conditionality lives *inside* the effect function (`_frame_deletion_check`); `loss_complete` has no internal conditionality at all — only the same generic outer `Effect.p` gate shared by every effect in the taxonomy.

---

## 3. Cleared keys and output signal — per modality

| Modality | Keys touched by `frame_deletion` | Keys touched by `loss_complete` | Same set? | Output sentinel |
|---|---|---|---|---|
| Radar | `rdr_sparse`, `rdr_polar_3d` (`_RADAR_FRAME_DELETION_KEYS`) | `rdr_sparse`, `rdr_polar_3d` (inline list, same two names) | **Yes, identical set** | Both → `None` via `_set_none()` |
| LiDAR | `ldr64` (`_LIDAR_FRAME_DELETION_KEYS`) | `ldr64` (inline list, same name) | **Yes, identical set** | Both → `None` via `_set_none()` |
| Camera | all keys from `_camera_keys(dict_item)` (dynamic — whichever of `front0/front1/left0/left1/right0/right1/rear0/rear1` are present as `torch.Tensor`) | same `_camera_keys(dict_item)` call | **Yes, identical set** | Both → key **stays present**, replaced by `_zero_camera_tensor()` (constant tensor ≈ `(0-mean)/std` per channel, never `None`) |

`_set_none` and `_zero_camera_tensor` are the exact same shared helper functions in both effect paths — there is no separate radar/lidar/camera "loss_complete-specific" clearing routine. `NoiseInjector._apply_cached_frame_deletion` (`noise_injection.py:581-597`) independently re-confirms this by construction: its docstring states it "Mirrors the clearing behaviour of radar_frame_deletion / lidar_frame_deletion / camera_frame_deletion exactly (same keys)" — i.e. the codebase itself treats "the keys frame_deletion clears" as a single canonical fact reused elsewhere, and that fact is line-for-line identical to what `loss_complete` clears.

`pc100p` is untouched by either effect for radar (confirmed in `frame-deletion-verification-report.md` §4 for `frame_deletion`; `radar_loss_complete`'s code above shows the same — it only ever names `rdr_sparse`/`rdr_polar_3d`, never `pc100p`).

---

## 4. Semantic intent per the design doc — confirmed, not assumed

Design doc language, quoted directly (`noise-injection-design.md`):

> R1 Frame deletion: "Skip entire radar frame... Random mode: delete each frame with independent probability p." (§1.1)
> R4 Loss complete: "Full radar data blackout for this frame... Semantic marker: this frame experienced a total sensor blackout (as opposed to 'every point happened to be dropped')." (§1.1)
> §1.4 Design Decision (written for loss_partial vs loss_complete, not frame_deletion vs loss_complete): "`loss_partial` models a stochastic data-loss process... `loss_complete` models a deterministic total sensor blackout."

The design doc does **not** contain an explicit frame_deletion-vs-loss_complete semantic contrast section — §1.4 is scoped to loss_partial vs loss_complete only, and the change log (line 16) frames `frame_deletion` as answering "New requirement: deterministic (interval or index-list) or random (per-frame probability) frame skip," a data-transport framing (frame arrives/doesn't arrive), distinct from R4's "total sensor blackout" framing (frame arrives, sensor inside it failed).

So the intended distinction the task hypothesized — **"frame never captured/transmitted" (frame_deletion) vs "sensor data present but corrupted/unusable" (loss_complete)** — is supported by the doc's own wording ("frame skip" vs "sensor blackout **for this frame**"), but it is an inference from word choice across two separate sections, not a directly stated head-to-head contrast. It is the correct reading, just not one the doc states in a single sentence the way it does for loss_partial vs loss_complete.

**Critically, this semantic distinction is intent-only — the code does not encode or enforce it.** There is no metadata field, no separate sentinel value, and no difference in cleared keys that reflects "frame never existed" vs "frame existed but sensor failed." Both effects call the identical `_set_none`/`_zero_camera_tensor` helpers on the identical key sets. The only place the distinction survives at all is in `dict_item['meta']['noise_injection']`, which records **which effect names were configured** (`_metadata()`, `noise_injection.py:707-714`) — not which one actually fired for a given frame, and not a name of the modality-clearing behavior itself.

---

## 5. NoiseInjector dispatch/composition — can both run on the same modality?

Yes. `RADAR_EFFECTS`/`LIDAR_EFFECTS`/`CAMERA_EFFECTS` register `frame_deletion` and `loss_complete` as independent named effects, and `EffectConfig`/`_resolve()` (`noise_injection.py:560-579`) impose no mutual-exclusion — a user config can list both for the same modality. The documented default ordering (`DEFAULT_ORDER_RADAR` etc., `noise_injection.py:485-504`) explicitly plans for this:

```python
DEFAULT_ORDER_RADAR = [
    "frame_deletion",       # R1 — first, so other effects skip if frame gone
    "noise_induced_shifts", # R2
    "loss_partial",         # R3
    "loss_complete",        # R4 — last (unconditional blackout)
]
```

Traced through `_apply_list()` (`noise_injection.py:599-633`): effects run **in the configured list order**, sequentially, each independently gated by its own `Effect.p` and consuming its own dedicated `sub_rng`. If `frame_deletion` fires first and clears the keys, `loss_complete` running afterward is not skipped by any special-case logic — it simply re-executes `_set_none`/`_zero_camera_tensor` on keys that are already `None`/already zero-tensors. For radar/LiDAR this is a genuine no-op (`_set_none` iterating over already-`None` keys does nothing observable). For camera it is *not* a no-op in the sense of "avoided work" — `_zero_camera_tensor` recomputes and reassigns the same constant tensor again, functionally idempotent but not literally skipped.

Neither effect calls `_has_key()` to check "has this modality already been zeroed by an earlier effect in the list and should I skip." That guard exists generically for *later* effects reading data (e.g. `radar_noise_induced_shifts`, `radar_loss_partial` both check `_has_key` before touching `rdr_sparse`) — but `loss_complete`, having no data-dependent logic at all, has nothing to gate on `_has_key` for; it unconditionally sets, whether or not the input was already `None`.

**So: if both are configured on the same modality and both fire (independent probability gates), the observable end state is identical to `loss_complete` alone having fired** — `frame_deletion` firing first makes `loss_complete`'s subsequent execution redundant (same output, wasted cycles) but not incorrect or stacking in any additive sense. There is no way for the two to "conflict" or produce a state different from either firing alone, because both target the exact same key set with the exact same sentinel.

---

## 6. `should_skip()` — frame_deletion only, no loss_complete equivalent

Quoted directly (`noise_injection.py:666-705`):

```python
def should_skip(self, frame_index: int, modality: str) -> bool:
    effect_list = {...}.get(modality, [])
    if not any(name == "frame_deletion" for name, *_ in effect_list):
        return False
    result = False
    for name, fn, p, params, sub_rng in effect_list:
        if name == "frame_deletion" and sub_rng.uniform() < p:
            if _frame_deletion_check(params, sub_rng, frame_index):
                result = True
                break
    self._skip_cache[(modality, frame_index)] = result
    return result
```

The guard `if not any(name == "frame_deletion" for name, *_ in effect_list): return False` is explicit: `should_skip()` only ever inspects effects literally named `"frame_deletion"`. `loss_complete` entries in the same `effect_list` are invisible to this method entirely — even if a modality is configured with `loss_complete` only (no `frame_deletion`), `should_skip()` returns `False` unconditionally for every frame, meaning the eval script's pre-check-before-loading optimization (§3, design doc) never fires for `loss_complete`-only configs, even though `loss_complete` *always* clears the data once loaded. There is no `should_skip`-equivalent pre-check mechanism for `loss_complete` anywhere in the file — it is only ever evaluated inside `__call__()` → `_apply_list()`, after the frame's sensor data has already been loaded into `dict_item`. This is a real asymmetry: `loss_complete` is strictly *more* predictable (always fires, no RNG, no config needed) than `frame_deletion`'s random mode, yet has *zero* pre-load skip-ahead capability, while `frame_deletion` — whose random-mode pre-check is documented to have RNG-desync bugs against `__call__()` (`frame-deletion-verification-report.md` §3) — is the one method that gets an (imperfect) skip-ahead path.

---

## 7. Task 8 — are the two distinguishable from `dict_item`'s final state alone?

**No, for all three modalities, under the same conditions established by the loss_partial-vs-loss_complete precedent in `noise-injection-param-sweep-report.md`'s R3vR4-Distinct section — but for a different reason than that precedent.**

- **Radar/LiDAR:** both effects set the exact same keys to the exact same sentinel (`None`) via the exact same helper (`_set_none`). Inspecting the post-effect `dict_item` gives `rdr_sparse=None, rdr_polar_3d=None` (or `ldr64=None`) in both cases — **byte-for-byte identical, unconditionally, at every invocation**, not just at an edge-case parameter value. This is a stronger identity than the loss_partial-vs-loss_complete case, where partial-vs-complete were only identical at the `fraction=1.0` edge and type-distinguishable (`ndarray` vs `None`) everywhere else. Here, `frame_deletion` and `loss_complete` are *always* type- and value-identical on output whenever both fire — there is no parameter that could make them diverge, because neither effect's output depends on any parameter (`loss_complete` takes none; `frame_deletion`'s params affect only *whether* it fires, never *what* it sets when it does).
- **Camera:** identical situation — both replace every key in `_camera_keys(dict_item)` with `_zero_camera_tensor()`'s output, the same constant per-channel value. Numerically indistinguishable, matching the param-sweep report's confirmed camera finding that `loss_complete` and (edge-case) `loss_partial` outputs are "numerically identical... only distinguishable by which effect executed."
- **The only place the two are distinguishable at all is `dict_item['meta']['noise_injection']`**, which records the effect *names configured* on the injector (`_metadata()`), not which one *fired* for this specific frame — so even that provides only "frame_deletion and/or loss_complete were configured for this modality," never "frame_deletion is what caused this frame's None/zero-tensor state as opposed to loss_complete." If both are configured and only one actually fires for a given frame (e.g. `frame_deletion`'s random gate misses but `loss_complete`'s outer `p` gate hits, or vice versa), nothing in `dict_item` records which one actually executed.

**Conclusion for task 8: given only the output `dict_item`, you cannot tell frame_deletion from loss_complete apart for any modality.** This is a stronger and simpler result than the loss_partial-vs-loss_complete case (which was only non-distinguishable at one edge value); here it holds unconditionally.

---

## 8. Comparison table

| | **frame_deletion** | **loss_complete** |
|---|---|---|
| Trigger condition | Conditional: `_frame_deletion_check()` — deterministic (`index_list` membership or `frame_index % interval == 0`) or random (`rng.uniform() < p`); can decline to fire even once invoked | Unconditional: no internal decision logic; always executes its clear once the function body runs (subject only to the same generic outer `Effect.p` gate every effect shares) |
| Cleared keys — radar | `rdr_sparse`, `rdr_polar_3d` | `rdr_sparse`, `rdr_polar_3d` — **identical set** |
| Cleared keys — LiDAR | `ldr64` | `ldr64` — **identical set** |
| Cleared keys — camera | all `_camera_keys(dict_item)` | all `_camera_keys(dict_item)` — **identical set** |
| Output sentinel — radar/LiDAR | `None` (`_set_none`) | `None` (`_set_none`) — **identical** |
| Output sentinel — camera | zero-filled normalized tensor, key stays present (`_zero_camera_tensor`) | zero-filled normalized tensor, key stays present — **identical** |
| `should_skip()` pre-check support | Yes (though documented as RNG-desynced against `__call__()` in random mode per `frame-deletion-verification-report.md`) | **No** — `should_skip()` explicitly filters to `name == "frame_deletion"` only; `loss_complete` has no skip-ahead path at all |
| Composable on same modality? | Yes | Yes — both can be configured together; if both fire, output is identical to either firing alone (redundant re-clear, not additive/conflicting) |
| Semantic intent (design doc) | "Frame skip" — models a frame that was never captured/transmitted, decision independent of any per-point data content | "Total sensor blackout for this frame" — models the frame arriving but the sensor's data for it being entirely unusable |
| Semantic intent actually enforced by code? | **No** — no metadata, sentinel, or key-set difference distinguishes the two; the distinction exists only in effect *naming* and design-doc prose, not in any runtime-observable signal |
| Distinguishable from output `dict_item` alone? | **No, for all 3 modalities** — always byte-for-byte identical output when both fire, stronger than the loss_partial-vs-loss_complete case (which only collided at `fraction=1.0`) |

---

## 9. Bottom line

`frame_deletion` and `loss_complete` are **functionally redundant for all three modalities** in terms of *what they do to the data* — same keys, same sentinel, same helper functions, every time. The only functional difference between them is **whether they fire**: `frame_deletion` is a conditional, parameterized, sometimes-RNG-driven decision; `loss_complete` is unconditional given the effect runs at all. The design doc's semantic framing ("frame skip" vs "sensor blackout") is a real and defensible distinction in *intent* — one is meant to model a missing frame, the other a corrupted-but-present one — but the current implementation gives that distinction zero runtime representation. Downstream code inspecting `dict_item` cannot recover which effect caused a given `None`/zero-tensor state; only the injector's own config (not stored per-frame) knows which effects were even active, and not which one actually executed for a specific frame when both are configured together. If per-failure-mode analysis (the stated rationale in design §1.4 for keeping loss_partial/loss_complete distinct) is meant to extend to frame_deletion vs loss_complete as well, the current code does not support it — `dict_item['meta']['noise_injection']` would need to record which specific effect fired per frame, not just which effects were configured on the injector.
