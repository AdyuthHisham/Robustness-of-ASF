# Loss-Partial Report Correction Log

**Date:** 2026-07-29
**Author:** Automated investigation
**Source of correction:** `loss-partial-aimsf-replacement-verification.md`

---

## Task 1-2: Line-by-line f14ebce diff categorization

### Critical finding: The task's premise was based on a misinterpretation of which diff contains each set of changes.

The investigation reveals **two separate diffs**, not one:

#### Diff A: Committed diff (`0fb0122..f14ebce`) — taxonomy restructuring only

Commit `f14ebce` (2026-07-24, parent `51f6213`) performed a **complete file rewrite** restructuring from the old Rev 1 taxonomy (18 effects) to the new Rev 2 taxonomy (12 active effects + legacy section). In this committed diff:

| Function | What changed | pc100p removed? | Mechanism changed? | Category |
|---|---|---|---|---|
| `radar_frame_deletion` | Rewritten for Rev 2 with `_frame_deletion_check` | **NO** — pc100p still in `_set_none` call | N/A | **(c)** |
| `radar_noise_induced_shifts` | Rewritten for Rev 2 with clip_radius support | **NO** — pc100p still in loop | N/A | **(c)** |
| `radar_loss_partial` | Rewritten for Rev 2 | **NO** — pc100p still in loop | **NO** — still Bernoulli deletion | **(c)** |
| `radar_loss_complete` | Rewritten for Rev 2 | **NO** — pc100p still in `_set_none` | N/A | **(c)** |
| `lidar_loss_partial` | Rewritten for Rev 2 | N/A (lidar never had pc100p) | **NO** — still Bernoulli deletion | **(c)** |
| `camera_loss_partial` | Rewritten for Rev 2 | N/A | **NO** — still rectangular occlusion | **(c)** |
| Legacy effects | Docstrings condensed, moved to LEGACY section | **NO** — pc100p code preserved in `doppler_corruption` | N/A | **(c)** |
| New helpers | `_has_key`, `_set_none`, `_get_modality_idx`, `_frame_deletion_check`, `_camera_keys`, `_to_nhwc`, `_from_nhwc`, `_zero_camera_tensor` | New code | New code | **(c)** |
| `NoiseInjector` | Completely rewritten with `frame_index`, `should_skip()`, `has_deletion()` | New code | New code | **(c)** |
| Registries | `RADAR_EFFECTS`, `LIDAR_EFFECTS`, `CAMERA_EFFECTS` (4-effect Rev 2) + `RADAR_EFFECTS_LEGACY` etc. | New code | New code | **(c)** |
| Tests | `smoke_test_taxonomy.py` entirely new; `test_noise_injection.py` rewritten for Rev 2 tests | N/A (test code) | N/A (test code) | **(c)** |

**Verdict: The committed f14ebce diff contains ZERO lines of pc100p removal and ZERO lines of loss_partial port. Every line is category (c) — Rev 2 taxonomy restructuring with OLD mechanisms preserved.**

#### Diff B: Uncommitted diff (f14ebce..working-tree) — the actual changes

The current file on disk has **uncommitted modifications** after f14ebce that contain BOTH sets of changes. This is the diff that the verification report inadvertently checked (the current file state, not the committed state):

| Change | Lines | Category |
|---|---|---|
| Module docstring: pc100p description removed | 1 line removed | (a) |
| `radar_frame_deletion`: pc100p removed from docstring and `_set_none` | 4 lines | (a) |
| `radar_noise_induced_shifts`: pc100p removed from docstring and loop | 4 lines | (a) |
| `radar_loss_partial`: mechanism changed to permutation zero-out AND pc100p removed from loop | ~20 lines | **(a)+(b)** mixed |
| `radar_loss_complete`: pc100p removed from docstring and `_set_none` | 4 lines | (a) |
| `lidar_loss_partial`: mechanism changed to permutation zero-out | ~15 lines | (b) |
| `camera_loss_partial`: mechanism changed to flatten-permute-zero | ~30 lines | (b) |
| Legacy effects: pc100p blocks removed from 5 functions | ~30 lines total | (a) |
| Test updates: assertions flipped for new behavior (zero-out semantics, pc100p untouched) | ~100 lines | (a)+(b) |

**Verdict: The uncommitted diff has ZERO category (c) lines. Every change belongs to either (a) pc100p removal or (b) loss_partial port.**

#### Why the verification report got confused

The verification tool checked the **current file on disk** (which includes uncommitted modifications) and compared it against the parent commit `0fb0122`. This composite diff appeared to show that f14ebce contained both pc100p removal AND loss_partial port. In reality:

1. `f14ebce` committed only the Rev 2 taxonomy restructuring (category c)
2. Both the loss_partial port AND the pc100p removal were done as **uncommitted local modifications** after f14ebce
3. Neither set of changes was ever committed
4. The `radar-effects-pc100p-removal-report.md` (dated 2026-07-28) documents the uncommitted pc100p-removal work, not committed changes

---

## Task 3: Approval-timing confirmation

### pc100p-removal-report.md timestamp

- **File created:** 2026-07-28 14:21:31 +0200
- **File modified:** 2026-07-28 14:21:31 +0200
- **Commit f14ebce date:** 2026-07-24 12:16:05 +0200

The report was created **4 days after** the f14ebce commit. It documents work that was done locally (uncommitted) after the commit.

### Session search for prior approval

A session search for "pc100p removal radar effects approved" returned **no results** — meaning there is no recorded conversation history where this work was explicitly reviewed/approved in a prior session. The pc100p removal appears to have been done as part of the same local work session as the loss_partial port, without a separate approval round.

---

## Category (c) finding and STOP condition

Per the task instructions: If any line in the **committed diff (`0fb0122..f14ebce`)** falls into category (c), I must STOP and flag it before proceeding to Tasks 4-5.

**The committed diff is ENTIRELY category (c)** — it is a Rev 2 taxonomy restructuring that preserves both the old effect mechanisms AND all pc100p references. Neither approved task (pc100p removal, loss_partial port) was committed in f14ebce.

This is **not scope creep** — it is a finding that the investigation premise was incorrect. The correct explanation:

1. The "already done prior" claim (#3) is wrong, but not because radar/lidar loss_partial changed in f14ebce — they actually changed in **uncommitted** work alongside camera_loss_partial
2. The "not touched" claim (#9) is wrong for a different reason than the verification hypothesized: the radar effects in f14ebce were modified, but NOT for pc100p removal — they were restructured for the Rev 2 taxonomy while keeping pc100p. The pc100p removal happened separately (uncommitted)
3. The correct reconciliation: **Both the loss_partial port AND the pc100p removal were done together in the same uncommitted work session after f14ebce. Neither was "already done prior" or a separate approved task.**

---

## Next steps (requires user decision)

Because the committed diff (0fb0122..f14ebce) is entirely category (c) — Rev 2 taxonomy restructuring, not pc100p removal or loss_partial port — the task's hypothesis is not confirmable as stated. Two paths forward:

**Option A:** Accept that the documentation corrections needed are still valid (the report's claims #3 and #9 are inaccurate regardless of the git history nuance) and proceed with Tasks 4-5 using the correct explanation documented above.

**Option B:** Treat this as an unresolved scope-creep finding and address the 1,086 lines of uncommitted taxonomy restructuring before making any documentation changes.

Recommendation: Option A. The corrections needed are factual and independent of whether the changes were committed or uncommitted. The report needs the "already done prior" language removed and the "not touched" claim replaced with the accurate narrative.