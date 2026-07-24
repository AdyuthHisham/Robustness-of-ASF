# Noise Injection Module — Taxonomy Revision (2026-07-23)

**Summary:** Replaced the 18-effect noise injection taxonomy with a canonical 12-effect design (4 per modality). All effects are eval-time-only — no training code paths touched.

**New taxonomy:** frame_deletion, gaussian_noise/noise_induced_shifts, loss_partial, loss_complete — applied uniformly across radar, LiDAR, and camera modalities.

**Design docs:**
- Design: `docs/vAIlt/noise-injection-design.md` (Rev 2)
- Revision report: `docs/vAIlt/noise-injection-taxonomy-revision-report.md`

**Implementation:**
- Source: `repos/K-Radar/datasets/effects/noise_injection.py`
- Tests: `repos/K-Radar/datasets/effects/test_noise_injection.py` (103 tests, all pass)

**Key design decisions:**
1. **Duplicate "loss partial" resolution:** LiDAR listed as 5 effects was a transcription artifact — it has 4 distinct effects (frame deletion, gaussian noise, loss partial, loss complete)
2. **Loss partial vs loss complete:** Distinct explicit effects. loss_complete sets keys to None; loss_partial(fraction=1.0) leaves an empty array. Different failure-mode semantics.
3. **Frame deletion:** Clears per-sensor data (keys→None/zero), doesn't skip the entire frame. `should_skip()` pre-check available for eval scripts.
4. **Legacy preservation:** All 18 old effects preserved under `# LEGACY EFFECTS` section, not loaded into active registries.

**Testing:** 103 tests — 19 radar, 12 lidar, 17 camera, 17 registry, 22 injector integration. Frame deletion tested with deterministic (interval + index list) and random sub-modes separately.

---

**Amendment 2026-07-24: Camera gaussian_noise legacy resolution**

`CAMERA_EFFECTS_LEGACY["gaussian_noise"]` and `CAMERA_EFFECTS["gaussian_noise"]` were the same function object (`camera_gaussian_noise`, line 349) — the legacy registry merely aliased the new-taxonomy function. Removed the duplicate key from `CAMERA_EFFECTS_LEGACY` with an explanatory comment. Camera legacy count 6→5, total legacy 18→17. Full investigation: `[[camera-gaussian-noise-resolution.pdf]]` (docs/vAIlt/ version).