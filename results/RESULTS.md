# Results index

Tracked, curated outputs. Large tables are in `data/` (see [`../data/DATA.md`](../data/DATA.md)).

| File | What | Regenerate with |
|---|---|---|
| `figures/metrics_table.png` | Pooled metrics for every condition (thesis figure; identical file to `docs/figures/thesis/metrics_table.png`) | `docs/figures/crossproduct_figures/generate_metrics_table.py` (reads `crossproduct_v2/summary_full_density.parquet`); mAP and R_b^c match `tables/master_metrics_table.md`, mASE differs slightly, see note |
| `figures/modality_map_trend_single.png` | R_b^c by modality across families / severities | not in this repo |
| `tables/master_metrics_table.{md,csv}` | mAP, mATE, mASE, mAOE, RCE, mRR for `original` + 21 conditions | `uv run python scripts/analysis/master_metrics_table.py` (needs `crossproduct_v2/summary_full_density.parquet`; overwrites `data/results/robustness_reports/`) |
| `tables/fpfn_table.{md,csv}` | FP / FN per condition | `uv run python scripts/analysis/fpfn_table.py` |

**mAP definition.** mAP is the aggregated mAP: the num_gt-weighted mean of cell-level `ap_restricted_range` over both classes and all stratum cells of `data/results/robustness_reports/crossproduct_v2/summary_full_density.parquet` (clean 73.99, LiDAR Gaussian noise medium 18.54, high 17.45; mRR 0.2506 / 0.2359). `master_metrics_table.py` was changed to use it (it previously averaged the two per-class APs, giving 72.89 / 23.71 / 21.56); the old outputs are kept in `data/results/robustness_reports/pre_aggmap_backup_20261121/`. After the change all 22 rows match the thesis figure's mAP and R_b^c. mASE does not: 0.2362 vs 0.239 clean (two mASE implementations exist; not traced). The summary parquet also reproduces the thesis FP/FN counts. This also shows the thesis figure was built from `crossproduct_v2`.

Excluded by design: `frame_deletion` (pipeline crashed; no metrics) and mFR (not implemented). Conditions: 30 corrupted (21 evaluable + 9 frame-deletion), clean run not counted.
