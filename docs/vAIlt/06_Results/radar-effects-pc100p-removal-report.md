# Radar Effects: pc100p Removal Report

**Date:** 2026-07-28  
**Justification:** See [`rdr_sparse-vs-pc100p-explainer.md`](rdr_sparse-vs-pc100p-explainer.md) for the full evidence chain demonstrating that pc100p has zero downstream consumers and no code cross-references it against rdr_sparse.

## Summary

All radar effect functions in `noise_injection.py` (both active Rev 2 taxonomy and legacy) were simplified to operate **only** on `rdr_sparse` (and `rdr_polar_3d` where already separately handled). Every `pc100p` branch was removed. The `pc100p` key is still loaded and available in `dict_item` from the dataset loaders — it is simply no longer modified by noise effects.

## Functions Changed

### Active (Rev 2) Effects — 4 functions

| Function | Change |
|----------|--------|
| `radar_frame_deletion` | Removed `"pc100p"` from `_set_none()` call. Docstring updated. |
| `radar_noise_induced_shifts` | Removed `"pc100p"` from `for key in [...]` loop. Docstring updated. |
| `radar_loss_partial` | Removed `"pc100p"` from `for key in [...]` loop. Docstring updated. |
| `radar_loss_complete` | Removed `"pc100p"` from `_set_none()` call. Docstring updated. |

### Legacy Effects — 5 functions

| Function | Change |
|----------|--------|
| `power_gaussian_noise` | Removed 5-line `pc100p` block (power noise injection). |
| `sparse_point_dropout` | Removed 4-line `pc100p` block (Bernoulli dropout). |
| `range_attenuation` | Removed 5-line `pc100p` block (range-based power attenuation). |
| `doppler_corruption` | Removed 9-line `pc100p` block (doppler channel corruption). |
| `power_saturation` | Removed 2-line `pc100p` block (power clip). |

### Module docstring
- Removed `pc100p` line from data-structure conventions section.

## grep Verification: No Downstream Code Reads pc100p

Full repo grep for `dict_item["pc100p"]` and `dict_item.get("pc100p")` found **zero hits outside**:
- Dataset loaders (which **set** the key, not read it):
  - `datasets/kradar_fusion_v1_0_calib_change.py` (lines 1010, 1059)
  - `datasets/kradar_fusion_v1_0.py` (lines 986, 1035)
  - `datasets/kradar_odometry_v1_0.py` (lines 625, 674)
  - `datasets/kradar_detection_v2_1.py` (lines 704, 753)
- `noise_injection.py` — this module (now clean)
- Test files — updated accordingly
- `scripts/smoke_test_integration.py` — updated accordingly

No model code (`models/`), no evaluation scripts (`scripts/main_fusion_eval_0.py`), no loss functions, and no metric code reads `dict_item["pc100p"]`. The grep confirmation was independent of the explainer's analysis.

## Files Modified

| File | Changes |
|------|---------|
| `datasets/effects/noise_injection.py` | 4 active effects + 5 legacy effects + module docstring — all pc100p branches removed |
| `datasets/effects/test_noise_injection.py` | 3 pc100p assertions flipped from `is None` → `is not None` |
| `datasets/effects/smoke_test_taxonomy.py` | 4 pc100p assertions flipped to verify untouched + report template updated |
| `scripts/smoke_test_integration.py` | 1 pc100p assertion flipped |
| `docs/vAIlt/noise-injection-design.md` | Changelog entry added + 4 table entries updated |

## Test Results

| Test Suite | Before | After | Status |
|------------|--------|-------|--------|
| `test_noise_injection.py` | — | **103/103 PASS** | ✅ All pass |
| `smoke_test_taxonomy.py` | — | **89/89 PASS** | ✅ All pass |
| `smoke_test_integration.py` | — | **37/37 PASS** | ✅ All pass |

No regressions. All new assertions that verify `pc100p` is untouched pass correctly.

## Design Doc Update

A changelog entry was added to `noise-injection-design.md`:
- 2026-07-28: Simplified all radar effects to operate ONLY on `rdr_sparse` (+ `rdr_polar_3d`). Removed all `pc100p` branches. Links to `rdr_sparse-vs-pc100p-explainer.md` as justification.

## Constraints Upheld

- ✅ LiDAR effects: **not touched**
- ✅ Camera effects: **not touched**
- ✅ Training code path: **not touched**
- ✅ `pc100p` key still loaded in dataset loaders: **preserved**
- ✅ `rdr_polar_3d` preserved as separate key: **confirmed distinct from pc100p, NOT removed**