# Verification Report

Merged, chronological synthesis of the `kradar_visibility` pipeline's independent source-code audits — 6 near-duplicate reports scattered across `docs/` and `test-bed/.../kradar/docs|outputs/`, folded into one canonical note per the Phase-1 dedup plan ([[00_Inbox/Dedup_Map]] Group C). Every verdict below was independently re-derived from source-code inspection + live pytest runs — **phase implementation logs were explicitly not trusted** across all constituent reports, and several logs turned out to fabricate or overstate completed work (documented below).

**Excluded from this merge**: `docs/verification_report.md` — despite the matching filename, this is a QA report auditing `docs/noise_addition_analysis.md` (a literature-synthesis document), not a pipeline verification report. Different topic entirely; not part of this cluster.

## Current status (re-verified 2026-08-11 against live code + live pytest — supersedes the historical gap table below)

The gap table and Go/No-Go verdict below are the state as of 2026-07-21/23. Re-running the checks directly against the current codebase on 2026-08-11 shows **most blocking gaps are now fixed**:

| Gap | 2026-07-21 verdict | 2026-08-11 live-verified status |
|---|---|---|
| C#2 Radar CFAR wiring | **PARTIAL, blocking** — scores up to 62 billion | **FIXED.** `pipeline.py:226` now calls `prepare_frame_radar()`; result flows into `compute_radar_sparsity_score()`. Live run (`sequence_ids=['1'], frame_limit=5`): `radar_sparsity_score` range **[0.061, 0.126]** — correctly bounded |
| `ghost_flag`/`weather` missing from `OUTPUT_SCHEMA` | Confirmed missing | **FIXED.** Both present in `config.py:79–124` (44 columns, verified via `grep`). `docs/output_schema_fix.md` documents the exact diff (added `timestamp` and `ghost_flag`; `weather` was already present) |
| `dist_coeffs` never extracted from calibration | Confirmed dead path | **FIXED.** `calibration.py:21` adds `_load_dist_coeffs()`, wired through `camera_visibility.py` |
| No VER test for ghost-flag semantics | Confirmed absent | **FIXED.** `TestGhostFlag` class, 6 tests (`ghost01`–`ghost06`), all pass live |
| SMK-15 `count` referenced before assignment | Failing (from a separate constituent report) | **FIXED** — passes live |
| Range-image build is a Python loop | Confirmed | **FIXED** — now `np.minimum.at`, vectorized |
| SMK-17 "times out at >300s" | Reported as timeout (dataset-IO bound) | **Disputed by the project's own newer errata note** — `test-bed/.../kradar/TESTING_NOTES.md` ("Errata: False Claims from Prior Sessions") documents a re-run showing the full smoke suite passes in 242s with zero timeouts, and explicitly flags the timeout claim as false. This session's own re-run also hit a timeout at 100–300s on this machine (dataset I/O is slow here), so the honest read is: **outcome is machine/IO-dependent, not a fixed logic failure** — don't cite "SMK-17 times out" as a stable fact either way without stating the environment |

**Still open, confirmed unchanged**: `stereo_consistency()` still imported but never called from `pipeline.py`; `MIN_RAYS_FOR_OCCLUSION_CHECK` guard still absent; LiDAR channel-LUT selection is still the `expected_density > 50` heuristic; Doppler-coherence gating still absent — but per `TESTING_NOTES.md` this and camera-temporal-consistency are now **formally reclassified as out of scope** (K-Radar has no RTK-GPS/INS stream to validate Doppler consistency against), not pending work; VER-25/26 still skip with the stale "weather not yet wired" message despite weather being wired.

**New backup-file debt not in the original cleanup list**: `src/kradar_visibility/radar_visibility.py.bak` — confirmed genuinely stale via diff (missing the CFAR vectorization present in the live `.py` file), alongside the previously-known `scripts/validate_precomputation.py.bak`.

**New bug, not previously documented anywhere in this vault**: `outputs/output_seq2_full_investigation.md` (a live 217-row parquet audit, not a source-code-only pass) found a confirmed logic defect in `_compute_occlusion_fraction_from_range_image()` (`lidar_visibility.py:237–298`). The range image is initialized with `np.zeros(...)`, so a bin value of `0.0` means "sensor never sampled this cell" — but the occlusion check's `valid_samples` filter (`np.isfinite(...) & ~np.isnan(...)`) treats `0.0` as a valid sample, and the occlusion comparison (`ranges > range_samples`) then reads "unsampled" as "confirmed something closer here," i.e. occluded. Net effect: an object with a large genuine in-box point count (confirmed case: 6412 points) can be scored `lidar128_visible=False, lidar128_sparsity_score=0.0` purely because its 8 sampled corners happened to land on unsampled range-image bins — a false 100%-occluded verdict with 100% reported confidence. **Root-cause fix**: exclude `range_image == 0.0` bins from `valid_samples` (treat as unknown → lowers confidence, doesn't raise `occluded_fraction`), not yet applied as of this check.

That same investigation independently reproduced and confirmed several of this report's other verdicts against live data (radar score ceiling at exactly 1.0 from the `np.clip` — intended, not a bug; `cam_right`/`cam_rear` all-False for one sequence — intended, verified via synthetic-geometry probe that the code path itself works; `ghost_flag` all-False for a clean sequence — intended, high cross-sensor agreement on non-corrupted data).

## Historical gap table (2026-07-21/23, superseded above where marked FIXED — kept for audit trail)

## Chronology

| Date | Report | Scope |
|---|---|---|
| 2026-07-14 | `outputs/verification_report.md` (60 L) | Earliest raw pytest snapshot, `phase4_integration_test.parquet` — 27 passed, 0 failed, 11 skipped |
| 2026-07-21 | `docs/verification_report_partial1.md` (144 L) | Critical Gaps #1–3 + Non-critical #1 audit |
| 2026-07-21 | `kradar/docs/verification_report.md` (180 L) | **Final** consolidated audit — explicitly merges the partial1 report with a fresh ground-truth pass; treated as canonical below |
| — | `kradar/docs/verification/verification_report_t_9383e63a.md` (170 L) | Pipeline assessment + sensor-label (`L`/`L1`/`L2`) investigation — independent focus, not covered by the Final report |
| 2026-07-23 | `kradar/docs/verification_report_part_testsdocs.md` (126 L) | Test-suite health + documentation-currency audit |
| 2026-07-23 | `kradar/docs/verification_report_part_ghostflag.md` (119 L, also `docs/vAIlt/verification_report_part_ghostflag.md`) | Ghost-flag deep dive, Gap #4 vs Gap #7 disambiguation |

## Consolidated gap verdicts (as of the 2026-07-21 Final report, cross-checked against later reports)

| Gap | Verdict | Key finding |
|---|---|---|
| **C#1** LiDAR range-image occlusion | **PASS** (partial1 said PASS; Final confirms) | `prepare_frame_lidar()` wired end-to-end per sensor per frame. Formula is `density_ratio × (1 − occluded_fraction × confidence)` — the `× confidence` term is **not** in the methodology doc, an undocumented addition. `MIN_RAYS_FOR_OCCLUSION_CHECK` guard (methodology specifies ≥8 rays) is **absent from the codebase entirely**. Range-image build is a Python for-loop, not the vectorized `np.argsort`/`np.minimum.at` the methodology specifies (~100× slower than intended). |
| **C#2** Radar CFAR noise-floor | **PARTIAL, blocking** | `prepare_frame_radar()` implements full guard/training-cell CFAR (`radar_visibility.py:26–122`) and is correctly unit-tested (VER-29/30 pass) — but **`pipeline.py:274` explicitly passes `noise_floor_db=None`, so the CFAR map is never called from the production pipeline.** The pipeline falls back to a scalar global median. Consequence: observed `radar_sparsity_score` range in the stale output parquet was **[0.0, 62,078,771,942.77]** — 11 orders of magnitude outside the documented [0,1] range. This is the single highest-severity finding across all 6 reports. |
| **C#3** Camera depth-buffer occlusion | **PASS**, with one dead sub-path | `prepare_frame_camera()` + `camera_score()` correctly wired, vectorized (`np.minimum.at`, fixing an earlier ~47.5s/frame bottleneck). **However**: distortion-correction math exists in `project_point_to_image()`/`camera_score()` but is dead code in production — `calibration.py`'s `get_camera_params()` never extracts `dist_coeffs` from the calibration pickle, so `dist_coeffs` is always `None` at the call site. |
| **C#4** Radar Doppler-coherence gating | **FAIL** | No `doppler`/`coherence` function exists anywhere in the source tree (`radar_visibility.py` ends at line 207 with CFAR only). One implementation log explicitly fabricates a `radar_score_with_doppler` function that does not exist — flagged as a **log-fabrication**, not merely an omission. |
| **Gap #7** Cross-sensor ghost flag | **PARTIAL** | Formula (`pipeline.py:460`) matches the methodology exactly and is correctly written to the output row dict; SMK-17 checks for its presence/dtype. But `ghost_flag` is **absent from `config.OUTPUT_SCHEMA`** (the same is true of `weather`) — the column exists at runtime but isn't declared in the canonical schema, and **no VER-* test exercises ghost-flag semantics** (0 matches for "ghost" in `test_verify.py`). Note: an earlier report conflated this with "Critical Gap #4," which is actually the *unrelated* Doppler-gating gap — corrected in the ghostflag-focused report. |
| **NC#1** Distortion-corrected projection | **PARTIAL** | Covered under C#3 above — math correct, coefficients never loaded. |
| **NC#2 / Task 2.4** Inter-object occlusion graph | **FAIL** | No `compute_occlusion_graph()` exists anywhere; not implemented. |
| Task 4.4 Camera stereo consistency | **NOT TESTED** | `stereo_consistency()` is implemented but imported-and-never-called from `pipeline.py` — dead code. |
| Task 3.1–3.2 doc/param cross-check | **PASS** (2026-07-23 report) | All four new parameter families (`range_image`, `sensor_origin`, `noise_floor_db`/`noise_floor_val`, `depth_map`/`depth_maps`) are genuinely documented in their respective function docstrings — no doc-currency gap here, despite the CFAR wiring gap above. |

## Sensor-label investigation (`t_9383e63a` report — unique content, not covered elsewhere)

Cross-referencing `info_label_rev2/*.txt` across sequences 1, 3, 5, 11, 14, 15, 21:

| Label | Sensor | Confidence |
|---|---|---|
| `R` | Radar (tesseract) | Confirmed |
| `L1` | OS2-64 (64-channel) | Confirmed — config maps `L1→OS2_64_CHANNELS=64` |
| `L2` | OS1-128 (128-channel) | Config maps it, but **`L2` never appears in any label file examined** (0 occurrences across all 7 sequences checked, despite OS1-128 data existing in those sequences) — a dead label/dead code path |
| `L` (bare) | **Unresolved** | Present in every sequence alongside `L1`; count sometimes equals `L1` exactly (seq 3: L=243, L1=243, suggesting 1:1 migration), sometimes a small fraction (seq 14: L=14, L1=85). Bare `L` has **no entry in `config.py`'s `SENSOR_SUITE` dict** and no documented meaning anywhere in the codebase or dataset docs. Likely a legacy pre-L1/L2-split label, but this cannot be confirmed without the original K-Radar label schema documentation. |

This directly affects [[04_Design/Output_Schema]]'s `sensor_identify` column semantics — the pipeline's OR-of-both-LiDARs handling for bare `L` (see [[03_Theory/Visibility_Formulas]]) is a reasonable but unverified interpretation of an undocumented label.

## Log-reliability finding (cross-cutting, all reports agree)

Every constituent report independently concludes that phase-implementation-log prose should not be trusted without source verification. Confirmed fabrications/overstatements: "CFAR noise-floor integrated into pipeline" (false — never called), "`radar_score_with_doppler` implemented" (function doesn't exist), "`ghost_flag` in output schema" (false — written at runtime, absent from `OUTPUT_SCHEMA`), "MIN_RAYS_FOR_OCCLUSION_CHECK guard implemented" (absent), "vectorized range-image build" (it's a Python loop). This is the reason every subsequent report in the chain re-derives verdicts from source rather than trusting the previous report's own log-summary sections — a methodology worth carrying forward for any future pipeline audit in this project.

## Test suite health (most recent numbers, 2026-07-23 report)

Smoke: 18 pass, 0 fail, 2 timeout (SMK-17 full-pipeline, `smk_all_sequences` — both >300s, dataset-IO bound, not logic failures). Verify: 27 pass, 13 skip (mostly insufficient data at toy scale; VER-25/26 weather-impact tests skip via a stale message — weather **is** wired into pipeline output as of this audit, but the skip condition was never updated to reflect that). Zero `NotImplementedError` stubs found anywhere in the test suite across all 6 reports.

## Cleanup debt (unresolved as of the latest constituent report — see 2026-08-11 update above for current status)

- ~~`pipeline.py:274` hard-codes `noise_floor_db=None`~~ — **FIXED**, see above.
- ~~`config.OUTPUT_SCHEMA` missing `ghost_flag` and `weather`~~ — **FIXED**, see above.
- ~~`calibration.py`'s `get_camera_params()` never extracts `dist_coeffs`~~ — **FIXED**, see above.
- 7 dead imports in `pipeline.py` (`prepare_frame_radar`, `RADAR_GUARD_CELLS`, `RADAR_TRAINING_CELLS`, `OS2_64_CHANNEL_LUT`, `OS1_128_CHANNEL_LUT`, `camera_score`, `stereo_consistency`) — **still open**: `prepare_frame_radar` is now genuinely called (not dead), but `RADAR_GUARD_CELLS`/`RADAR_TRAINING_CELLS`/`OS2_64_CHANNEL_LUT`/`OS1_128_CHANNEL_LUT`/`stereo_consistency` remain imported-but-unused in `pipeline.py`.
- Stray backup files: `scripts/validate_precomputation.py.bak` **and** `src/kradar_visibility/radar_visibility.py.bak` (new, confirmed stale — pre-dates the CFAR vectorization).
- VER-25/26 skip message is stale (claims weather isn't wired; it is) — **still open**.
- **New**: `_compute_occlusion_fraction_from_range_image()` zero-bin-as-occluded bug — see above, not yet fixed.

## Go/No-Go: Checkpoint 4

**Historical verdict (2026-07-21): NO-GO** — blocked on the radar CFAR wiring gap (scores exceeding [0,1] by 11 orders of magnitude), the missing `OUTPUT_SCHEMA` entries, SMK-17 timeout, and the dead `stereo_consistency` path.

**Current verdict (2026-08-11, live-verified)**: the radar CFAR and `OUTPUT_SCHEMA` blockers are fixed. Remaining blockers before a clean GO: `stereo_consistency` dead code (Task 4.4 explicitly required it, per the original checkpoint text "stereo consistency optional" — re-read the checkpoint wording before treating this as blocking; it may already satisfy "optional"), and the newly-found range-image occlusion bug, which silently zeros out `lidar128_sparsity_score`/`visible` for objects that should be visible — this is a correctness bug in a load-bearing metric, not just missing coverage, and should be fixed before trusting any LiDAR-visibility-derived result (e.g. for Results-chapter figures) at face value.

## Source

- `test-bed/src/Modules/robust_testing/kradar/docs/verification_report.md` (180 L — canonical/"Final")
- `test-bed/src/Modules/robust_testing/kradar/docs/verification/verification_report_t_9383e63a.md` (170 L — sensor-label investigation)
- `docs/verification_report_partial1.md` (144 L — superseded by the Final report, which explicitly merges it)
- `test-bed/src/Modules/robust_testing/kradar/docs/verification_report_part_testsdocs.md` (126 L — doc-currency/test-health audit)
- `test-bed/src/Modules/robust_testing/kradar/docs/verification_report_part_ghostflag.md` (119 L — ghost-flag deep dive)
- `test-bed/src/Modules/robust_testing/kradar/outputs/verification_report.md` (60 L — earliest raw pytest snapshot, 2026-07-14)
- `test-bed/src/Modules/robust_testing/kradar/docs/verification_report_partial1.md` (17 L — pointer/summary of the partial1 report above, no unique content)
- **2026-08-11 re-verification** (live, this session): direct `grep`/`diff` against `src/kradar_visibility/*.py`, `config.py`; live `uv run pytest tests/test_smoke.py` (18 passed), `uv run pytest tests/test_verify.py` (27 passed, 19 skipped, includes the new `TestGhostFlag` class); live pipeline run via `pipeline.run(sequence_ids=['1'], frame_limit=5)` confirming bounded radar scores and populated `ghost_flag`/`weather` columns
- `test-bed/src/Modules/robust_testing/kradar/TESTING_NOTES.md` ("Errata: False Claims from Prior Sessions" — disputes the SMK-17-timeout claim, formally closes Doppler/temporal-consistency as out of scope)
- `test-bed/src/Modules/robust_testing/kradar/outputs/output_seq2_full_investigation.md` (live 217-row parquet audit — source of the new range-image occlusion bug finding)
- `test-bed/src/Modules/robust_testing/kradar/docs/output_schema_fix.md` (documents the exact `OUTPUT_SCHEMA` fix)
