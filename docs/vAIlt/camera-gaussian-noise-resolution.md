# Camera Gaussian Noise — Legacy vs New Taxonomy Resolution

**Date:** 2026-07-24
**Investigator:** Hermes agent (theasstnt)
**File:** `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/noise_injection.py`

---

## Finding

`CAMERA_EFFECTS["gaussian_noise"]` and `CAMERA_EFFECTS_LEGACY["gaussian_noise"]` point to the **exact same function object**.

| Property | CAMERA_EFFECTS | CAMERA_EFFECTS_LEGACY |
|---|---|---|
| Resolved function | `camera_gaussian_noise` | `camera_gaussian_noise` |
| `id()` | Same | Same |
| `__qualname__` | `camera_gaussian_noise` | `camera_gaussian_noise` |
| `__code__` (code object) | Same object | Same object |
| `__code__.co_firstlineno` | 349 | 349 |
| `__code__.co_name` | `camera_gaussian_noise` | `camera_gaussian_noise` |
| `is` comparison | `True` | `True` |
| `__doc__` | `C2 — Additive Gaussian noise per pixel per channel` | Identical |

**Verdict: Case #2 — same function object, not a separate legacy copy.**

---

## Assessment: Was This Intentional or Accidental?

**Intentional.** Two pieces of evidence:

1. The revision report explicitly documents this (line 53): *"camera_gaussian_noise (C1) → gaussian_noise (camera) — Preserved. Same function."* The author knew this was the same function and chose not to create a separate legacy copy.

2. The comment in the legacy registry (line 956): `# note: same name as new; overridden in active registry` — the author was aware of the duplicate entry but left it as a convenience alias.

---

## The Contract Violation

The taxonomy revision report claims (line 97): *"All 18 old effect functions are preserved in noise_injection.py under a # LEGACY EFFECTS section, with full docstrings and function bodies."*

This claim is violated for camera Gaussian noise because there **is no separate legacy copy** of `camera_gaussian_noise`. The legacy registry entry merely references the same function that powers the active taxonomy. The other 17 legacy effects each have their own distinct function body in the `# LEGACY EFFECTS` section; camera Gaussian noise does not.

This is correct from a **design** standpoint — adding Gaussian noise to camera pixels is a maximally simple, canonical operation that doesn't need a legacy-specific variant — but it contradicts the **procedural claim** of "all 18 effects separately preserved."

---

## Classification

| Check | Result |
|---|---|
| Same function object? | **Yes** |
| Same code / different object (copy-paste)? | No |
| Different functions, same name? | No |
| Was overlap intentional? | **Yes** (documented in revision report) |

---

## Resolution

### What was done

We removed the misleading duplicate entry `"gaussian_noise"` from `CAMERA_EFFECTS_LEGACY` and replaced it with an explicit comment explaining that camera Gaussian noise has no separate legacy copy because it was carried forward into the active taxonomy unchanged.

**Rationale for removal over alias-keeping:**

The legacy registries exist to hold effects that were **removed** or **replaced** from the active taxonomy — effects with no counterpart in the new 12-effect set. Camera Gaussian noise is NOT a removed/replaced effect; it was carried forward as-is. Leaving a duplicate alias in the legacy dict implies it was somehow deprecated or moved out of the active set, which is misleading.

The function `camera_gaussian_noise` remains available:
- At module level: `from noise_injection import camera_gaussian_noise`
- In the active registry: `CAMERA_EFFECTS["gaussian_noise"]`

The legacy camera count decreases from 6 to 5, reflecting only genuinely distinct legacy effects.

### Files changed

1. **`noise_injection.py`** — Removed `"gaussian_noise"` key from `CAMERA_EFFECTS_LEGACY`; added comment documenting why.
2. **`test_noise_injection.py`** — Updated legacy count check from 6 to 5.
3. **`noise-injection-taxonomy-revision-report.md`** — Added amendment note.

### Test results

```
Before: 103 tests, 103 PASS, 0 FAIL
After:  102 tests, 102 PASS, 0 FAIL
```

Count dropped by 1 because the legacy-count test was revised from 6→5, removing the check for the 6th camera legacy effect. No functional tests were removed or changed.

---

## Second-Order Concern

No other effect across the four registries (RADAR_EFFECTS, LIDAR_EFFECTS, CAMERA_EFFECTS, and their LEGACY counterparts) has this problem. All other 17 legacy effects have their own standalone function definition in the `# LEGACY EFFECTS` section. The cross-registry function-identity check is clean for every other key.