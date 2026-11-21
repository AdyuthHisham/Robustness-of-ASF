# AMSCUP Audit — Master Doc

## Scope & boundaries

Audit target is the **working-tree state as of 2026-09-08, not HEAD**. `repos/K-Radar`, `docs/Latex_Report`, and several vault docs are modified-uncommitted; treat that as the current reality to check claims against, not noise.

Ground truth (do not re-report as findings):
- Monorepo of loosely-coupled parts. No single top-level build/test/lint command by design — not a fault.
- `repos/K-Radar`, `repos/AMSCUP_PLUS`, `docs/Latex_Report` are git submodules. `repos/AI-MSF-Benchmark` is vendored. Document interface only (what calls in/out); never propose restructuring their internals.
- `docs/vAIlt/` (project docs) and `obsidianVault/` (personal research KB) are deliberately separate. Settled decision — never propose merging.
- Alvis (HPC cluster) permanently gone as of 2026-09-01. `repos/AMSCUP_PLUS` (Slurm scripts) is now dead infra — legitimate restructure/archive candidate, not a bug.
- Actively developed piece: `test-bed/src/Modules/robust_testing/kradar/` (`kradar_visibility`) — own pyproject.toml/uv.lock/git repo, own AGENTS.md/architecture.md (both read by orchestrator; see below).
- Already-tracked, don't rediscover: 2026-08-26 frame-identifier bug (fixed); row_table_iou03 camera_frame_deletion gap (expected/tracked); mFR excluded from metrics stack (user decision 2026-09-01, two conflicting in-repo defs, neither adopted); crossproduct regen 2026-08-31 already rebuilt post-camgauss-fix (2 vault docs still cite stale numbers — find the rest systematically, don't assume only these two).
- Uncommitted working-tree items (`docs/delete_/`, `backups/`, `alvis_archive_2026-08-28/`, modified tracked files): probable intentional in-progress user state. Note in restructure doc as "needs a decision," never flag for deletion as a bug.

## Anti-confabulation rule (hard constraint)

Every finding needs:
- `file:line` (or file + clear location, e.g. vault doc heading)
- actual mechanism — quote or closely paraphrase real code/text, not summarized from memory
- a **repro** (command/concrete input) OR a **failure scenario** (specific inputs/state → specific wrong output/crash/contradiction)

No evidence bar cleared → goes to `## Unverified / Suspicion` only, with a one-line reason. Never invent APIs, function names, numbers, or citations. Grep before claiming existence/absence.

## Architecture reference (from architecture.md / AGENTS.md, read in full by orchestrator)

Module layout: `config.py` (constants/schema only), `parser.py` (label file I/O), `calibration.py` (camera calib pickles), `data_loader.py` (lazy per-frame loading, returns None on missing), `radar_visibility.py` (SNR-weighted power density, DB_HEADROOM=20.0), `lidar_visibility.py` (point-in-box count/expected-density ratio), `camera_visibility.py` (8-corner projection, W1=0.7 area / W2=0.3 centrality), `pipeline.py` (orchestration, `_world_to_voxel`/`_radar_fov_check`/`_obj_corners` helpers, `run()` entry point). Error handling: missing sensor → `visible=False, score=0.0`, never raise; calib failure → `calib_available=False`, camera metrics zeroed; per-frame exceptions → log + skip + continue. Output schema fully enumerated in architecture.md §Output Schema — use as the reference to diff against `config.OUTPUT_SCHEMA` and docs.

## Chunk status

| # | Chunk | Reviewer A | Reviewer B | Status |
|---|-------|-----------|-----------|--------|
| 1 | kradar_visibility core | done | done | complete |
| 2 | kradar_visibility tests | done | done | complete |
| 3 | corruption/sweep/analysis scripts | done | done | complete |
| 4 | outer test-bed | done | done | complete |
| 5 | docs/vAIlt claims | done (spot-check) | done (lead) | complete |
| 6 | obsidianVault claims | n/a (no spotcheck needed) | done (lead) | complete |
| 7 | submodule interfaces + dead infra | done | done | complete |

## Finding schema

Each finding:
- id (e.g. A-1-03 = Reviewer A, chunk 1, finding 3)
- file:line
- claim/mechanism (quoted or closely paraphrased)
- failure scenario or repro
- severity (blocks correctness / silent wrong output / doc-drift / cosmetic)

## Findings log (append-only)

### Chunk 1 — kradar_visibility core modules

**[Orchestrator note, added post-chunk-7]** A-7-01 casts doubt on which crossproduct build is actually reproducible from current code: the code writes to `crossproduct/` (stale), but chunk 3's and chunk 5's "confirmed clean" number-matches (RELIABILITY_FLOOR, D3=209, 2 suspected_bug flags) were validated against `crossproduct_v2/` — a directory current code does not produce. Those matches are real (v2 vs. docs agree), but they are not matches against what running the code today would generate.

**A-1-01** — `pipeline.py:301-306` — `radar_visible` set purely from object geometry (`radar_fov_in and radar_range_in`), not gated on `radar_cube is not None`. Only `radar_score` checks cube presence. Violates the documented missing-sensor→`visible=False` invariant. Failure scenario: missing `.mat` file, object geometrically in FOV → row emits `radar_visible=True, radar_sparsity_score=0.0`; inflates `num_sensors_visible` and can wrongly select `primary_sensor='radar'` (radar checked first in the argmax tie-break at pipeline.py:445/462). Severity: silent wrong output.

**A-1-02** — `lidar_visibility.py:185-195` — occlusion channel-LUT selection uses `if expected_density > 50: OS1_128_CHANNEL_LUT else OS2_64_CHANNEL_LUT`. Verified `_EXPECTED_OS2=8000.0`, `_EXPECTED_OS1=32000.0` (both computed and print-verified) — both exceed 50, so OS2-64 always gets misclassified as OS1-128's LUT for occlusion scoring. May silently no-op occlusion correction (if `_validate_range_image_dimensions` catches the shape mismatch) or silently produce wrong occlusion fractions (if it doesn't) — neither path is flagged in output/logs. Severity: silent wrong output.

**B-1-01** — architecture.md:153-166 describes `lidar_visibility.py` as plain point-count/expected-density ratio with no mention of occlusion; code (lines 116-320) actually applies a range-image-based occlusion discount (`final_score = density_ratio * (1.0 - occluded_fraction * confidence)`) when `range_image`/`sensor_origin` supplied — which pipeline.py does by default. Code's own docstring flags this as a later addition. Severity: doc-drift.

**B-1-02** — architecture.md:169-189 describes camera visibility as pure area/centrality (`W1*area + W2*centrality`), omits a depth-buffer occlusion pass the code applies (`camera_visibility.py:18,405-424`, `DEPTH_MARGIN`/`DEPTH_SAMPLE_RADIUS`-driven `occlusion_discount`). Severity: doc-drift.

**B-1-03** — architecture.md's Output Schema table (lines 235-269, 33 columns) is missing 4 real columns present in `config.OUTPUT_SCHEMA` and populated by pipeline.py: `lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `ghost_flag` (radar-visible but no other sensor sees it), `occluded` (in radar FOV/range but zero sensors visible). Severity: doc-drift. **Count superseded by chunk-5 A-spot-check: OUTPUT_SCHEMA actually has 50 entries, 8 missing from architecture.md, not 46/4 — see chunk 5.**

**B-1-04** — context note only, folded into B-1-03: config.py's own `OUTPUT_SCHEMA` list is NOT itself found missing any column — the drift is architecture.md's separate hand-written table vs. config.py, not config.py vs. pipeline.py. Severity: cosmetic.

### Chunk 2 — kradar_visibility tests

**A-2-01** — no test in test_smoke.py/test_verify.py ever calls `pipeline.compute_visibility_for_frame`/`run()` (grep confirms zero matches). VER-01's radar_visible check only asserts one-directional implication on whatever the fixture already produced; never drives a missing-radar-cube frame through the pipeline. This is why A-1-01 shipped: no test exercises the failure path. Severity: doc-drift (suite's stated verification purpose doesn't match actual coverage).

**A-2-02** — `TestLidarWithRangeImage` (VER-27/28/29, test_verify.py:78/117/179) hardcodes `expected_density=10.0` with a comment explicitly acknowledging the `>50` threshold (`"<=50 -> selects OS2_64_CHANNEL_LUT"`) — i.e. the test author knew about the threshold but only tested the branch reachable by a synthetic small value, never the real production values (8000/32000) that trigger A-1-02. `uv run pytest tests/test_verify.py::TestLidarWithRangeImage -v` passes today despite the bug being live. Severity: silent wrong output.

**B-2-01** — SMK-16 (test_smoke.py:195-205, spec `docs/vAIlt/05_Implementation/6_Smoke_Test_Scaffold.md:147-149`) is named/specified as "center score > edge score" but only constructs a center object and asserts `score > 0` — no edge object, no comparison. A broken/constant centrality term would still pass. Severity: doc-drift.

**B-2-02** — VER-32 (test_verify.py:322-356) claims to verify "distortion correction applied when coefficients provided" but calls `calculate_visibility_score` identically both times (same `cam_params` with `dist_coeffs` set in both) — no no-distortion variant exists to compare against; only range-checks the (duplicate) result. Severity: doc-drift.

**B-2-03** — VER-30 (noise-floor-map adaptation) and VER-31 (depth-buffer occlusion discount), test_verify.py:266-272/315-320, both claim comparative behavior in their docstrings but only assert `[0,1]` range on both variants — no inequality assertion. Test's own comments admit no comparison is made. A no-op implementation of either feature would pass. Severity: doc-drift.

### Chunk 3 — scripts/ (corruption/sweep/analysis)

**A-3-01** — `validate_precomputation.py:281-297,358-363` reimplements the identical buggy `radar_visible = radar_fov_in and radar_range_in` (same as A-1-01, no cube-presence check), and its comparison against pipeline output (line 358) is only range asserts on the recomputed values — never an equality/mismatch check against the pipeline's actual row. A validator whose stated job is to catch precomputation drift structurally cannot catch A-1-01, whether present or fixed. Severity: silent wrong output.

**B-3-01** — `validate_output.py:5-10,33-42` claims to check "every column in expected_cols is present" but `expected_cols` omits 3 real columns (`lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `occluded`) that config.OUTPUT_SCHEMA/pipeline.py emit (same gap as B-1-03). The validator would clean-PASS a Parquet missing or wrong-dtype in those 3 fields. Severity: doc-drift.

Confirmed clean (not findings): RELIABILITY_FLOOR and crossproduct-doc numbers in `docs/crossproduct_trends_and_anomalies*.md` are self-consistent with current code post-2026-09-01 rebuild — the "2 stale vault docs" from memory are elsewhere, not in scripts/ scope. CORRUPTED_CONDITIONS (22 conditions) consistent across master_metrics_table.py/fpfn_table.py/run_churn_*.py; frame_deletion exclusion matches already-tracked ground truth.

No corruption-injection code (gaussian noise/loss application) exists under `kradar/scripts/` — it lives outside this repo's scope (submodule or upstream), not a gap in this chunk.

### Chunk 4 — outer test-bed/

No findings from Reviewer A (nuscenes/example/main.py are exploratory stubs with no stated invariants to falsify; nuscenes-devkit is fail-loud by its own design, not this repo's missing-sensor convention). Root pyproject.toml/uv.lock confirmed consistent (sklearn/matplotlib/tqdm/pyquaternion present as transitive deps).

**Resolved (chunk 3's open question)**: corruption-injection code (`noise_injection.py`) exists only in `repos/K-Radar/datasets/effects/` (submodule) — confirmed absent anywhere under `test-bed/`. Out of restructure scope per ground truth. `test-bed/` is precomputation/analysis/validation-only.

**B-4-01** — `nuscenes/compare_paraquet.py:1-4` docstring's own usage instructions cite `compare_parquet.py` (correct spelling) but the file itself is `compare_paraquet.py` (misspelled) — documented invocation doesn't exist on disk. Severity: cosmetic.

Confirmed accurate (not findings): CLAUDE.md's "Hello from test-bed!" claim, ruff exclude of repos/K-Radar/**, wise_gather_RLC_nu.py's 12-field docstring claim.

### Chunk 5 — docs/vAIlt/ + top-level crossproduct docs

**B-5-01** — `docs/vAIlt/06_Results/robustness-visualization-plan.md:1-5,52-60` presents mFR as an active, plannable metric (proposes mAP/mFR line plots, frame_deletion-vs-loss_complete mFR comparisons) with no note of the 2026-09-01 exclusion decision. Severity: doc-drift.

**B-5-02 (A-verified, corrected)** — `KRadar_configpy_Reference.md` and `Config_Reference.md` both show the identical 42-column OUTPUT_SCHEMA list. Real `config.py:110-161` has **50 columns** (not 46 as B first estimated) — both docs are missing the same **8 columns**: `timestamp`, `lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `environment`, `time_of_day`, `frame_object_count`, `ghost_flag`, `occluded`. Same drift class as B-1-03/B-3-01, now confirmed present in docs/vAIlt too. Severity: doc-drift.

**Resolved ground-truth correction**: the memory `project_crossproduct_regen_20260831` is itself stale. `docs/crossproduct_trends_and_anomalies.md` (mtime Sep 1 11:41) and `docs/trend_candidates.md` were already corrected against the `crossproduct_v2/reports/findings.md` rebuild (D3=209, 2 suspected_bug flags — direct match) before the memory's own timestamp window closed. Zero hits for the stale numbers (1421/1042/173/187/186) in either doc. No repo-side fix needed; this is a memory-hygiene correction, not a finding.

Confirmed clean (not findings): `manual-code-vetting-checklist.md` correctly documents mFR exclusion; no doc found asserting VER-25/26 currently pass (the chunk-2 flagged risk did not materialize).

### Chunk 6 — obsidianVault/Knowledge + Projects/K-Radar

**B-6-01** — `obsidianVault/Projects/K-Radar/robustness-radar-charts.md:14-24,105-109` claims frame_deletion axes (CF/LF/RF) "still appear as chart axes" (10 axes total: 9 sensor×effect + OG). `radar_charts.py:48,64-67` excludes frame_deletion from `RADAR_AXIS_EFFECTS` entirely (comment: "excluded per user request 2026-08-25") — real axis count is 7 (6 sensor×effect + OG), not 10. Doc describes a prior code state. Severity: doc-drift.

**B-6-02** — `obsidianVault/Knowledge/robustness-metric-selection.md:89-93` presents "Frame-level flip/consistency (mFR family)" as one of five legitimate metric families, no caveat. `master_metrics_table.py:10-11,325` — which cites this same note as its spec source — explicitly omits mFR as not implemented, per the tracked 2026-09-01 exclusion. The note never mentions the family it describes was later excluded. Severity: doc-drift.

Confirmed clean: `asf-corruption-study-alvis.md` — all Alvis references are past-tense/dated log entries, none present Alvis as currently available; not a live contradiction.

### Chunk 7 — submodule interfaces + dead infra

**A-7-01** — `crossproduct.py:32`'s `SUMMARY_OUT_DIR` hardcodes the path to `repos/K-Radar/outputs/robustness_reports/crossproduct/` (stale, last written Aug 31 23:11) but current docs (`docs/crossproduct_trends_and_anomalies.md:7,16`) treat `crossproduct_v2/` (Sep 1-2) as authoritative. Both directories exist and look complete on disk. Rerunning `run_analysis.py`/`queries.py`/`plots.py` today would silently regenerate the superseded `crossproduct/` directory and leave `crossproduct_v2/` (the path every current doc cites) untouched and increasingly stale — no error, no warning. `plots.py:26` independently hardcodes the same stale path. Severity: silent wrong output.

**B-7-01** — architecture.md:251-253,86 describes `weather`/`environment`/`time_of_day` as populated from `description.txt` per-sequence metadata, with `weather`'s "normal" fallback framed as an edge case. `find` confirms zero `description.txt` files exist anywhere in the local `repos/K-Radar` checkout — `parser.py:142-153` always returns `{}`, so every row gets the fallback/null, permanently (these files "only ever lived on Alvis," corroborated by `obsidianVault/Daily/2026-09-07.md:20-22`, and Alvis is gone for good). This is now a structural, permanent limitation, not a transient gap — and directly explains why VER-25/VER-26 (chunk 2) are unconditionally skipped: the data they'd test against can never exist locally again. Severity: doc-drift.

Resolved for restructure doc: `repos/AMSCUP_PLUS` has zero functional call sites from test-bed/ (one comment-only reference) — confirmed dead infra, no live interface to preserve. `repos/AI-MSF-Benchmark` has zero references anywhere under test-bed/ — either unused or referenced only submodule-internally (open question, not resolved). CLAUDE.md's descriptions of both submodules confirmed accurate. No "Alvis still available" claim found anywhere in obsidianVault/Daily/, README.md, or top-level docs/*.md grepped.

## Unverified / Suspicion

- (chunk7) whether `crossproduct_v2/` was created by a patched one-off run or some other process — affects whether A-7-01 is "constant never updated after rename" vs. "parallel directory, code never repointed"; either way the mismatch is real. `docs/ALVIS_MIGRATION_PLAN.md`, `docs/FINAL_CHECK_LOG.md`, `docs/thesis_writing_bible.md` Alvis references confirmed present via grep but not read in full — `ALVIS_MIGRATION_PLAN.md` in particular is ambiguous by filename alone (migration off vs. back onto Alvis) and worth a follow-up read. `anomaly_plots.py:21` uses an independent `HERE.parents[8]` path derivation vs. the `AMSCUP_ROOT` pattern used elsewhere — currently resolves to the same path but is a latent fragility. `docs/vAIlt/06_Results/loss-partial-aimsf-replacement-verification.md` already documents its own submodule-internal correctness issues (2 FAILs) — out of restructure scope but worth citing as a known issue. AMSCUP_PLUS's own internal docs (MIGRATION_STATE.md, FIXES.md) not read.
- (chunk6) ~20 files in obsidianVault/Knowledge/ and Projects/K-Radar/ not deep-read beyond the 4 git-modified files + mFR cross-check (time-boxed) — listed in B-chunk6.md if a follow-up pass is warranted. AP figures in robustness-radar-charts.md's tables not re-verified against live parquet (plausibility-checked only). Knowledge/Verification/ subdirectory not checked.
- (chunk5) no exhaustive line-by-line pass over docs/vAIlt/05_Implementation (10+ files) or 06_Results (20+ files) beyond the targeted mFR/crossproduct/schema checks; methodology-description diff for radar/lidar/camera formula docs (re: B-1-01/B-1-02 occlusion additions) not completed. docs/vAIlt/10_Archive/ not audited (archived, allowed to be stale — confirm assumption if restructure doc cites it). docs/crossproduct_figures/ captions not checked. API_Contracts.md's CAMERA_INTRINSICS/EXTRINSICS placeholder claim (flagged chunk 1) still unresolved.
- (chunk4) nested ThreadPoolExecutor in multi_wise_gather_RLC_nu.py making concurrent nusc.get() calls — thread-safety of nuscenes-devkit's in-memory tables not verified, not executed (dataset presence unconfirmed).
- (chunk4) compare_paraquet.py's 388-line body not read beyond the docstring/filename mismatch; black's direct-vs-transitive dependency status in pyproject.toml not resolved; Dockerfile/marimo notebook/.egg-info under src/Modules/ not reviewed.
- (chunk3) CFAR scripts (cfar_evidence_*.py, benchmark_and_verify_cfar.py, verify_cfar_fix.py) not reviewed by either lens — flagged open for follow-up if restructure doc needs CFAR-specific claims checked.
- (chunk3) Full line-by-line pass not done over all ~30 scripts/analysis files or scripts/analysis/crossproduct/ (bootstrap_reliability.py, anomaly.py detectors, plots.py) — prioritized by graphify+grep signal; negative grep result (no hits) for chunk-1-bug propagation into metrics, not exhaustive.
- (chunk3) scripts/alvis/* exists, not audited — dead infra per ground truth.
- (chunk2/A) did not run test_smoke.py (dataset presence unconfirmed); did not cross-check all SMK-01..17/VER-01..26 IDs line-by-line against spec docs; test_parallel_smoke.py and conftest.py internals not reviewed (deferred to chunk 3/general).
- (chunk2/B) `TestGhostFlag` docstring cites pipeline.py:481 for ghost_flag formula; chunk 1's B-1-03 cited ~515 — line-number reconciliation needed, not independently resolved.
- (chunk2/B) VER-25/VER-26 (TestWeatherImpact) are unconditional `pytest.skip` — always skipped. Visible in code so not itself a claims finding, but flag for chunks 5/6: if any vault/doc claims VER-25/26 as implemented/passing, that IS a doc-drift finding there.
- (A) `_validate_range_image_dimensions` fallback behavior under the A-1-02 LUT mismatch — whether it silently no-ops occlusion correction or produces wrong fractions — not traced to a concrete numeric output this pass.
- (A) camera_visibility.py occlusion/depth-map code (`prepare_frame_camera`, `camera_score`, `stereo_consistency`) and calibration.py not reviewed for correctness in chunk 1 — open for a later pass.
- (A) `obj.theta` degrees-vs-radians handling (pipeline.py:132-134 comment claims raw label files store degrees) not independently verified against an actual label file.
- (B) `lidar_visibility.py:263-264` code comment claims a specific prior bug (occluded_fraction 0.0 buggy vs 0.167 correct) already fixed — not independently reproduced, flagged only as worth a correctness-lens check that the fix is real/complete.
- (B) Whether `docs/vAIlt/04_Design/API_Contracts.md`'s description of `CAMERA_INTRINSICS`/`CAMERA_EXTRINSICS` as placeholder-zero (config.py:82-100) is accurately flagged elsewhere as dead/superseded by calibration.py's real pickle-loaded values — deferred to chunk 3/4/5.
