# K-Radar Sensor Effects System Audit

**Date:** 2026-07-20
**File:** `/home/adhish/Productivity/AMSCUP/docs/vAIlt/kradar-effects-audit.md`
**Scope:** Inference-time robustness testing only (not training)

## Summary

The effects system lives exclusively in `datasets/kradar_fusion_v1_0_calib_change.py` and has never been executed — it is **dead code** due to three independent blockers:

1. `build_dataset()` in `utils/util_pipeline.py` doesn't forward `**kwargs` — `cfg_effect` can't reach the dataset
2. The effect overlay PNGs referenced in config don't exist on disk
3. `consider_effects=False` is hardcoded in both reference scripts

All detailed findings with verified code snippets and execution flow diagram are in the full audit document.

## Implementation Status

| Modality | Status | Mechanism |
|----------|--------|-----------|
| Camera | ✅ Code exists, ⚠️ not runnable (images missing) | Threshold-based PNG overlay (L570-580) |
| LiDAR | ✅ Fully implemented | Azimuth-based point removal (L775-784) |
| Radar | ❌ Zero implementation | `cfg_effect.rad.effect = None` everywhere |

## Key Constraints for Adding Radar Effects

- Modify `get_rdr_sparse()` or add a new method called from `__getitem__` after step 4
- Must also fix `build_dataset()` in `utils/util_pipeline.py` to forward `**kwargs`
- Must register `KRadarFusion_v1_0_CalibChange` in `datasets/__init__.py` if using factory
- No randomization or composability exists in the current design — effects are deterministic singletons per sensor

## References

- Full audit: `/home/adhish/Productivity/AMSCUP/docs/vAIlt/kradar-effects-audit.md`
- Dataset file: `repos/K-Radar/datasets/kradar_fusion_v1_0_calib_change.py`
- Eval entry point: `repos/K-Radar/scripts/main_fusion_eval_0.py`
- Pipeline: `repos/K-Radar/pipelines/pipeline_detection_v1_0.py`