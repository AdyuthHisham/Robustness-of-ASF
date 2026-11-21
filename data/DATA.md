# Data catalogue

Everything under `data/` except this file is **gitignored**. It is shared as a drive bundle (**TODO: add link**) and unpacked into `data/`. Paths are defined once in [`src/amscup_paths.py`](../src/amscup_paths.py); override with `AMSCUP_DATA_DIR` and `KRADAR_DATASET_ROOT`.

| Path (under `data/`) | What | Size | Format / schema | Produced by | Regenerable now? |
|---|---|---|---|---|---|
| `KRadar/` | K-Radar dataset (sequences, `info_label_rev2`, calibration). **Not in the bundle**; obtain from the K-Radar authors | n/a | K-Radar layout | external | n/a; required for `tests/` and `scripts/visibility/` |
| `results/all_preds*.parquet`, `all_preds.txt`, `all_gts.txt` | Merged ASF predictions and ground truth, all conditions | see `du` | KITTI-style rows, Parquet | `src/robustness/merge_predictions_text.py`, `ingest.py` | **No** for predictions (Alvis inference); re-merging only works from the raw per-sequence outputs |
| `results/alvis_seq*/`, `results/batches/` | Raw per-sequence outputs retrieved from Alvis | 118 MB (seq1), 122 MB (batches) | text + Parquet | Alvis ASF runs | **No** (cluster permanently unavailable) |
| `results/robustness_reports/row_table_iou03.parquet` | Main analysis table: one row per prediction / unmatched GT, IoU 0.3 | 53 MB, 1,109,616 rows, 29 cols (`condition`, `cls`, `sequence`, `frame`, `is_tp/is_fp/is_fn`, `iou`, `score`, box fields, GT fields, context) | Parquet | `src/robustness/ingest.py` | From `all_preds.parquet`; not from scratch |
| `results/robustness_reports/full_denormalized_table_22cond*.parquet` | Row table joined with visibility, weather, density (22 conditions) | 52 to 54 MB, 872,745 rows, 34 cols | Parquet | `scripts/analysis/build_denormalized_table.py` | Yes, from the row table and `data/visibility/` |
| `results/robustness_reports/master_metrics_table*.{csv,md}` | mAP / mATE / mASE / mAOE / RCE / mRR per condition (+ by weather, time of day, environment) | KB | CSV, Markdown | `scripts/analysis/master_metrics_table.py` | Yes (about 18 s). Copy of the main one is tracked in `results/tables/` |
| `results/robustness_reports/fpfn_table*.{csv,md}` | FP / FN counts per condition | KB | CSV, Markdown | `scripts/analysis/fpfn_table.py` | Yes |
| `results/robustness_reports/churn_by_condition*.json` | Per-object detection-status churn | KB | JSON | `src/robustness/gt_transition_analysis.py`, `scripts/analysis/run_churn_*.py` | Yes |
| `results/robustness_reports/ap_robustness_local.json` | AP / RR / CRI per condition and class | 316 KB | JSON | `src/robustness/run_ap_robustness.py` | Yes (needs merged predictions) |
| `results/robustness_reports/crossproduct/`, `crossproduct_v2/`, `crossproduct_v3_weather_corrected/` | Cross-product (condition x class x weather x time x environment) summaries, deltas, anomaly reports | 3 to 4 MB each | Parquet, JSON, MD | `scripts/analysis/crossproduct/run_analysis.py` | Yes. Three variants exist; which one the thesis uses is **not recorded here** (open item) |
| `results/robustness_reports/exploratory/` | Exploratory passes 1 to 4 | 4 MB | CSV, MD | `scripts/analysis/exploratory_passes.py`, `pass4_stratifier_charts.py` | Yes |
| `results/robustness_reports/*backup*`, `*.bak`, `pre_*` | Pre-fix snapshots kept for provenance | about 250 MB | various | manual | n/a (do not use for analysis) |
| `visibility/output_with_env_density.parquet` | Per-object radar / LiDAR / camera visibility scores plus weather, environment, density | 37 MB total in `visibility/` | Parquet, schema in `src/kradar_visibility/config.py` (`OUTPUT_SCHEMA`) | `scripts/visibility/run_all_sequences.py` | Needs the K-Radar dataset |
| `figures/` | Charts written by `scripts/analysis/*` (bar, box, heatmap, radar, line, dumbbell, distributions) | 170 MB | PNG | `scripts/analysis/*` | Yes, from the tables above |

Known, expected gap: `camera_frame_deletion` rows are missing from `row_table_iou03.parquet` because that sweep crashed. Do not treat as a new bug.

Tracked, small outputs live in [`results/`](../results/RESULTS.md).
