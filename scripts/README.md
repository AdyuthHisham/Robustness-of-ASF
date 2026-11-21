# Scripts

Run everything from the repo root with `uv run python <path>`. Paths resolve through `src/amscup_paths.py`. The exceptions are reference-only: `data_transfer/` and `cluster_historical/` carry old absolute paths, and a few `src/effects/` scripts do too. "Output" lists the destinations the script names in its code, under `data/figures/` (charts), `data/results/robustness_reports/` (tables) or `data/visibility/`; "see script" means it prints or takes paths as arguments. Inputs for `analysis/` are the tables in `data/results/robustness_reports/` (mostly `row_table_iou03.parquet`); inputs for `visibility/` are the K-Radar dataset (`KRADAR_DATASET_ROOT`) plus `configs/`. Descriptions are each script's own docstring (first line). I ran only `analysis/master_metrics_table.py` end to end; the other scripts were parsed and their imports of `amscup_paths` names checked, not run.

| Directory | Purpose | Runnable now? |
|---|---|---|
| `analysis/` | metrics tables, charts, cross-product and exploratory analysis from the result tables | Yes, with the data bundle |
| `visibility/` | per-object visibility pipeline, CFAR checks, projection helper | Only with the K-Radar dataset |
| `data_transfer/` | moving K-Radar data between machines (rsync + verification) | Historical (source machines gone) |
| `cluster_historical/` | Alvis SLURM scripts that produced the predictions | **Reference only. Alvis is permanently unavailable** |


## `analysis/`

| Script | Purpose | Output | Command |
|---|---|---|---|
| `analysis/bar_charts.py` | Bar charts of mAP / mATE / mASE (raw values), plus their Rb robustness-ratio | `bar_charts`, `bar_charts/v2_official` | `uv run python scripts/analysis/bar_charts.py` |
| `analysis/box_plots.py` | Box plots of per-sequence metric distributions, one chart per metric, one | `box_plots` | `uv run python scripts/analysis/box_plots.py` |
| `analysis/build_denormalized_table.py` | Full-granularity denormalized analysis table: one row per prediction/GT | `full_denormalized_table.parquet`, `full_denormalized_table_22cond.parquet` | `uv run python scripts/analysis/build_denormalized_table.py` |
| `analysis/context_radar_charts.py` | Radar charts breaking mAP/mASE/mATE down by scene-context field | `context_radar_charts` | `uv run python scripts/analysis/context_radar_charts.py` |
| `analysis/dataset_distributions.py` | Descriptive distribution charts for the K-Radar dataset itself (not model | `dataset_distributions` | `uv run python scripts/analysis/dataset_distributions.py` |
| `analysis/density_line_charts.py` | Line charts of mAP, mATE, mASE vs. per-frame GT object density, one panel | `density_line_charts` | `uv run python scripts/analysis/density_line_charts.py` |
| `analysis/distance_dumbbell_charts.py` | Dumbbell plots of mAP / mATE / mASE at near vs. far range, one row per | `distance_dumbbell_charts` | `uv run python scripts/analysis/distance_dumbbell_charts.py` |
| `analysis/distance_line_charts.py` | Line charts of mAP / mATE / mASE vs. distance from ego, one line per | `distance_line_charts` | `uv run python scripts/analysis/distance_line_charts.py` |
| `analysis/distance_line_charts_by_modality.py` | Line charts of mAP / mATE / mASE vs. distance from ego, same data and | `distance_line_charts_by_modality` | `uv run python scripts/analysis/distance_line_charts_by_modality.py` |
| `analysis/distance_robustness_charts.py` | Line charts of the Rb robustness ratio (Gao et al.; == RR/mRR/RS -- see | `distance_robustness_charts` | `uv run python scripts/analysis/distance_robustness_charts.py` |
| `analysis/exploratory_passes.py` | Passes 1-3 of the full-granularity exploratory pass (see | `exploratory` | `uv run python scripts/analysis/exploratory_passes.py` |
| `analysis/fpfn_table.py` | FP/FN table: one row per severity-specific corruption condition (21 | `data/results/robustness_reports/fpfn_table*.{csv,md}` | `uv run python scripts/analysis/fpfn_table.py` |
| `analysis/heatmaps.py` | Heatmaps of mAP/mATE/mASE (raw values), plus their Rb robustness-ratio | `heatmaps` | `uv run python scripts/analysis/heatmaps.py` |
| `analysis/master_metrics_table.py` | Master metrics table: one row per severity-specific corruption condition | `data/results/robustness_reports/master_metrics_table*.{csv,md}` | `uv run python scripts/analysis/master_metrics_table.py` |
| `analysis/merge_churn.py` | Merges gt_transition_analysis.py's churn output into Pass 1 (condition | `churn_by_condition.json`, `exploratory` | `uv run python scripts/analysis/merge_churn.py` |
| `analysis/pass4_stratifier_charts.py` | Pass 4 of the exploratory pass: distance_from_ego / frame_density as | `exploratory` | `uv run python scripts/analysis/pass4_stratifier_charts.py` |
| `analysis/radar_charts.py` | Radar (spider) charts of per-class AP by condition, for a single K-Radar | `radar_charts` | `uv run python scripts/analysis/radar_charts.py` |
| `analysis/robustness_line_charts.py` | Line charts of the Rb robustness ratio (Rb^c = corrupted_metric / | `robustness_line_charts` | `uv run python scripts/analysis/robustness_line_charts.py` |
| `analysis/run_churn_context.py` | Context-stratified churn for Pass 3, run as a single pass over the | `churn_by_condition.json`, `robustness_reports` | `uv run python scripts/analysis/run_churn_context.py` |
| `analysis/run_churn_pass4.py` | Churn stratified by the two continuous stratifiers Pass 4 covers for | `robustness_reports` | `uv run python scripts/analysis/run_churn_pass4.py` |
| `analysis/zero_ablation_line_charts.py` | Line charts of mAP / mATE / mASE vs. distance from ego, restricted to the | `zero_ablation_line_charts` | `uv run python scripts/analysis/zero_ablation_line_charts.py` |
| `analysis/zero_ablation_robustness_line_charts.py` | Line charts of the Rb robustness ratio (corrupted / clean, per bin) vs. | `zero_ablation_robustness_line_charts` | `uv run python scripts/analysis/zero_ablation_robustness_line_charts.py` |

## `analysis/crossproduct/`

| Script | Purpose | Output | Command |
|---|---|---|---|
| `analysis/crossproduct/anomaly.py` | Peer-group anomaly detection (the addendum's second detection mode -- | see script | `uv run python scripts/analysis/crossproduct/anomaly.py` |
| `analysis/crossproduct/anomaly_plots.py` | Figures for the peer-group anomaly detection addendum. Same conventions | `crossproduct` | `uv run python scripts/analysis/crossproduct/anomaly_plots.py` |
| `analysis/crossproduct/bootstrap_reliability.py` | Shared bootstrap-CI utility for stratified mAP, reused by every | see script | library, imported by other scripts (no CLI) |
| `analysis/crossproduct/build_queries_report.py` | Answer queries.py Q1-Q7 and write docs/crossproduct_queries_report.md. | see script | `uv run python scripts/analysis/crossproduct/build_queries_report.py` |
| `analysis/crossproduct/crossproduct.py` | Cross-product enumeration and the summary-table builder (Step 2.1/2.2 of | `crossproduct` | `uv run python scripts/analysis/crossproduct/crossproduct.py` |
| `analysis/crossproduct/detectors.py` | D1-D5: the addendum's named detectors, run alongside anomaly.py's | see script | library, imported by other scripts (no CLI) |
| `analysis/crossproduct/metrics.py` | Pure aggregation functions for the cross-product analysis. No I/O, no | see script | library, imported by other scripts (no CLI) |
| `analysis/crossproduct/plots.py` | Figures for the cross-product analysis, PNG for LaTeX inclusion. Reuses | `crossproduct` | `uv run python scripts/analysis/crossproduct/plots.py` |
| `analysis/crossproduct/queries.py` | One function per deliverable question, each returning a ranked | see script | `uv run python scripts/analysis/crossproduct/queries.py` |
| `analysis/crossproduct/run_analysis.py` | Thin orchestrator: build summaries -> deltas -> run every query -> write | see script | `uv run python scripts/analysis/crossproduct/run_analysis.py` |

## `visibility/`

| Script | Purpose | Output | Command |
|---|---|---|---|
| `visibility/benchmark_and_verify_cfar.py` | Step 5 (Benchmark) + Step 6 (Multi-frame per-object verification) for CFAR vectorization. | see script | library, imported by other scripts (no CLI) |
| `visibility/benchmark_precomputation.py` | Performance benchmark for precomputation overhead (Phase 4 Task 4.2). | see script | `uv run python scripts/visibility/benchmark_precomputation.py` |
| `visibility/cfar_evidence_b.py` | Benchmark: load one cube, run all CFAR operations on it fresh each time. | see script | library, imported by other scripts (no CLI) |
| `visibility/cfar_evidence_c.py` | Part 2: Per-object scoring on real multi-object frames (sequence 2). | see script | library, imported by other scripts (no CLI) |
| `visibility/cfar_evidence_gathering.py` | Evidence-gathering: numerical equivalence, benchmarks, per-object scores on real K-Radar data. | see script | library, imported by other scripts (no CLI) |
| `visibility/project_bbox_to_camera.py` | K-Radar 3D Bounding Box to Camera Image Projection | see script | `uv run python scripts/visibility/project_bbox_to_camera.py` |
| `visibility/run_all_sequences.py` | scripts/run_all_sequences.py — Regenerate output_with_env_density.parquet | `data/visibility/output_with_env_density.parquet` | `uv run python scripts/visibility/run_all_sequences.py` |
| `visibility/run_full_sequence.py` | scripts/run_full_sequence.py — Run kradar_visibility pipeline against one FULL real sequence. | see script | `uv run python scripts/visibility/run_full_sequence.py` |
| `visibility/run_pipeline.py` | scripts/run_pipeline.py — CLI entry point for the kradar_visibility pipeline. | see script | `uv run python scripts/visibility/run_pipeline.py` |
| `visibility/run_split.py` | scripts/run_split.py — Run kradar_visibility over a K-Radar dataset split | see script | `uv run python scripts/visibility/run_split.py` |
| `visibility/summarize_output.py` | scripts/summarize_output.py — Read a kradar_visibility Parquet output and produce a markdown report. | see script | `uv run python scripts/visibility/summarize_output.py` |
| `visibility/validate_output.py` | Validation script for the visibility output Parquet file. | see script | `uv run python scripts/visibility/validate_output.py` |
| `visibility/validate_precomputation.py` | Validation script for precomputation outputs (Phase 3 Task 3.2). | see script | `uv run python scripts/visibility/validate_precomputation.py` |
| `visibility/verify_cfar_fix.py` | Standalone verification: CFAR fix produces valid [0,1] radar scores on real data. | see script | library, imported by other scripts (no CLI) |

`analysis/crossproduct/run_analysis.py` is the orchestrator for the other files in that folder. Several outputs depend on which cross-product result tree is canonical (`crossproduct`, `crossproduct_v2`, `crossproduct_v3_weather_corrected`); this is an open item (see `data/DATA.md`).

## `data_transfer/` and `cluster_historical/`

`data_transfer/`: `phase1_mapper.py`, `phase2_rsync.py`, `phase3_verify.py`, `quick_check.py`, `run_pipeline.sh` (+ `sync_manifest.json`). `cluster_historical/`: `asf_run.sbatch`, `merge_batch.sbatch`, `run_batched_sweep.sh`, `submit_run.sh`, `kradar_visibility_alvis/*`. Not runnable without the original machines.
