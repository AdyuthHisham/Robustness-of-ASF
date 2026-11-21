# Verification Report: Ghost Flag & Related Roadmap Tasks

**Run:** Part 3 — Ghost flag / Gap #4 mapping  
**Date:** 2026-07-23  
**Method:** Source-code audit + pytest collection + live test run  
**Model:** deepseek-ai/deepseek-v4-flash (Nvidia)

---

## Numbering Resolution

The user-cited filenames do not match on-disk reality; actual file names and gap/task IDs are re-extracted below per the verification-ground-truth rule.

| User-cited reference | On-disk source | Status |
|---|---|---|
| `06_upgrade_roadmap.md` | `PHASE2_ROADMAP.md` | File renamed |
| `04_gap_analysis.md` | `PHASE1_ANALYSIS.md` | File renamed |
| "Critical Gap #4" | PHASE1_ANALYSIS.md:257 — **Radar Doppler-coherence gating (1.3)** | ID stable, but user's checks target ghost-flag behaviour (on-disk **Gap #7**, PHASE1_ANALYSIS.md:260) |
| "ghost-flag rule" | `k-radar-recommended-pipeline-summary.md` line 97 — `radar_visible ∧ ¬lidar_visible ∧ ¬camera_visible` | Matches methodology ground truth |

**Critical Gap #4** (PHASE1_ANALYSIS.md:257) is **"Radar Doppler-coherence gating (1.3)"** — a radar-specific ghost-rejection upgrade using Doppler analysis. The **cross-sensor ghost flag** the user's checks target is actually **Gap #7** (PHASE1_ANALYSIS.md:260). Both are verified below with their correct on-disk IDs.

---

## Verdict Table

### Gap-specific rows

| On-disk Gap ID | Description | Verdict | Evidence | Discrepancy vs phase-log claims |
|---|---|---|---|---|
| **Critical Gap #4** (PHASE1_ANALYSIS.md:257) | Radar Doppler-coherence gating (1.3) | **FAIL** | `radar_visibility.py` docstring (line 3-5) claims §1.2+1.3 implementation, but no `doppler` or `coherence` function exists anywhere in the package (`search_files` returned 0 matches for `def.*doppler|def.*coherence` across all source). The file ends at line 207 with CFAR noise floor (Gap #3) and basic `compute_radar_sparsity_score` only. | Phase log claims "§1.2+1.3 implemented" but only §1.2 (CFAR) exists. Doppler-coherence gating is entirely absent. |
| **Gap #7** (PHASE1_ANALYSIS.md:260) | Cross-sensor ghost flag | **PARTIAL** | See detailed sub-table below | Phase logs claim ghost flag "wired in pipeline output" and "tested in SMK-17". Pipeline wiring ✓. Schema missing ✗. Verify test missing ✗. |

### Ghost flag (Gap #7) — Detailed sub-row

| Verification point | Status | Evidence |
|---|---|---|
| Formula in `pipeline.py` | **PASS** | `pipeline.py:460`: `ghost_flag = radar_visible and not lidar64_visible and not lidar128_visible and not (cam_front_visible or cam_left_visible or cam_right_visible or cam_rear_visible)` — matches `k-radar-recommended-pipeline-summary.md:97` formula exactly |
| Written as output column | **PASS** | `pipeline.py:460` adds `'ghost_flag': ...` to the row dict; row dicts are collected into `all_rows` list (line 463) then materialised as Polars DataFrame (line 548) |
| Smoke test exists | **PASS** | `test_smoke.py:226-232` (SMK-17) asserts `ghost_flag` in `expected_cols` and checks `df['ghost_flag'].dtype == pl.Boolean` |
| Verify test exists | **FAIL** | `test_verify.py` — 0 matches for `ghost` across the entire file. No VER test exercises this column |
| In OUTPUT_SCHEMA (`config.py`) | **FAIL** | `config.py:80-122` — `OUTPUT_SCHEMA` ends at `primary_sensor` (line 121); no `ghost_flag` entry. The column IS written at runtime via the row dict, but the canonical schema definition does not declare it |
| Live pipeline — ghost_flag populated | **UNTESTED** | Pipeline run timed out (>300s on 2 sequences × 20 frames). Existing `output.parquet` could not be independently verified (user denied interactive command). Schema inference from source code confirms column is written but per-row population cannot be confirmed without a live run |
| Score columns in [0,1] | **UNTESTED** | Same timeout limitation. Source code shows `sparsity_score` values are `np.clip(raw_score / DB_HEADROOM, 0.0, 1.0)` (radar_visibility.py:197) — nominally correct, but live output not checked |

### Roadmap Task rows

| Roadmap Task | Verdict | Evidence |
|---|---|---|
| **Task 2.4** — Inter-object occlusion graph (PHASE2_ROADMAP.md:126-131) | **FAIL** | `compute_occlusion_graph()` does not exist in any file. `lidar_visibility.py` has per-object `_compute_occlusion_fraction_from_range_image()` (lines 237-298) but no inter-object O(M²) occlusion graph. Not related to ghost flag or Gap #4. |
| **Task 4.1** — `prepare_frame_camera()` (PHASE2_ROADMAP.md:162-170) | **PASS** | Function exists at `camera_visibility.py:212-294`. Builds sparse depth maps from LiDAR points per camera. Called at `pipeline.py:244-247`. Not related to ghost flag or Gap #4. |
| **Task 4.2** — `camera_score()` with occlusion discount (PHASE2_ROADMAP.md:172-183) | **PASS** | Function exists at `camera_visibility.py:297-422`. Implements 8-corner projection (4.2) + depth-buffer occlusion discount (4.3) merged. Imported at `pipeline.py:33`. Not related to ghost flag or Gap #4. |

---

## Cleanup Debt

| Item | Status | Evidence |
|---|---|---|
| `config.py.backup` | **CLEAN** — not found | `find . -name '*.backup'` returned empty (all directories searched) |
| `config.py.backup2` | **CLEAN** — not found | Same |
| `lidar_visibility.py.backup` | **CLEAN** — not found | Same |
| `pipeline.py.backup` | **CLEAN** — not found | Same |
| `config.py` OUTPUT_SCHEMA missing `ghost_flag` | **DEBT** | `config.py:80-122` — schema has `weather` (line 93) but no `ghost_flag`. Pipeline writes it at runtime but the authoritative schema definition lacks it. Downstream consumers that read `OUTPUT_SCHEMA` to plan their own schemas will miss this column. |
| `scripts/validate_precomputation.py.bak` | **KNOWN** | Stale backup from prior audit; not one of the four user-flagged files but exists and could confuse |

The four user-flagged files (`config.py.backup`, `config.py.backup2`, `lidar_visibility.py.backup`, `pipeline.py.backup`) are all clean — none exist. The only stale backup in the tree is `scripts/validate_precomputation.py.bak` (known from prior Phase 2 audit).

---

## Go/No-Go: Ghost-flag output alone vs. Phase 4 Checkpoint 4

**Phase 4 Checkpoint 4** (PHASE2_ROADMAP.md:206):  
> *"Camera scores include occlusion_discount by default; stereo consistency optional; all smoke tests pass"*

The ghost flag is **not part of Phase 4 Checkpoint 4**. Checkpoint 4 is about:
- Camera scores including occlusion_discount by default
- Stereo consistency (optional)
- All smoke tests pass

The ghost flag is a Phase 2 / Gap #7 deliverable. It was checkpointed in **Phase 2** at `PHASE2_ROADMAP.md:135`:  
> *"LiDAR scoring produces density_ratio, occluded_fraction, combined score; all smoke tests pass; range-image built once/frame"*

**Verdict on ghost flag alone for its own (Phase 2 / Gap #7) checkpoint:**

| Criterion | Status | Notes |
|---|---|---|
| Formula correct in pipeline output | ✓ | `pipeline.py:460` — matches methodology doc |
| Schema defined in config.py | ✗ | Missing from `OUTPUT_SCHEMA` |
| Smoke test exercises it | ✓ | SMK-17 checks column existence + boolean dtype |
| Verify test exercises it | ✗ | No VER test exists |
| Live output confirmed | ✗ | Timeout on pipeline run; `output.parquet` not independently verified |

**NO-GO** — Ghost flag output alone does NOT satisfy a clean checkpoint sign-off because:
1. `config.py` `OUTPUT_SCHEMA` does not declare `ghost_flag`
2. No verify test (VER-*) covers ghost-flag semantics (e.g. verifying the logical rule, edge cases)
3. Live pipeline output was not confirmed (timeout / user-blocked)

---

## Supporting Evidence (file:line citations)

| Claim | File | Line(s) |
|---|---|---|
| Ghost flag formula | `pipeline.py` | 460 |
| Ghost flag in smoke test expected columns | `test_smoke.py` | 226 |
| Ghost flag boolean dtype check | `test_smoke.py` | 232 |
| OUTPUT_SCHEMA ends at `primary_sensor`, no ghost_flag | `config.py` | 120-122 |
| No ghost in test_verify.py | `tests/test_verify.py` | — (0 matches) |
| `prepare_frame_camera()` exists | `camera_visibility.py` | 212-294 |
| `prepare_frame_camera()` called in pipeline | `pipeline.py` | 244-247 |
| `camera_score()` exists | `camera_visibility.py` | 297-422 |
| `stereo_consistency()` imported but never called | `pipeline.py` (import) | 33 |
| `stereo_consistency()` called in pipeline | `pipeline.py` | 0 matches — not called |
| No `compute_occlusion_graph()` in any file | — | 0 matches in all source |
| Doppler-coherence claims in docstring only | `radar_visibility.py` | 3-5 (docstring claim) |
| No doppler/coherence function in source | — | 0 matches for `def.*doppler|def.*coherence` |
| Radar docstring contradicts actual code | `radar_visibility.py` | Lines 3-5 claim §1.3, file ends at line 207 with no doppler fn |
| Methodology ground truth for ghost flag | `k-radar-recommended-pipeline-summary.md` | 97 |
| 4 user-flagged backup files absent | — | `find . -name '*.backup'` = no matches for those 4 |