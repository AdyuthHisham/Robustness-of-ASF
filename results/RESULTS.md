# Results index

Tracked, curated outputs. Large tables are in `data/` (see [`../data/DATA.md`](../data/DATA.md)).

| File | What | Regenerate with |
|---|---|---|
| `figures/metrics_table.png` | Pooled metrics for every condition (thesis figure; identical file to `docs/figures/thesis/metrics_table.png`) | the thesis figure's rendering script is not in this repo; its numbers differ from the table below, see note |
| `figures/modality_map_trend_single.png` | R_b^c by modality across families / severities | not in this repo |
| `tables/master_metrics_table.{md,csv}` | mAP, mATE, mASE, mAOE, RCE, mRR for `original` + 21 conditions | `uv run python scripts/analysis/master_metrics_table.py` (overwrites `data/results/robustness_reports/`) |
| `tables/fpfn_table.{md,csv}` | FP / FN per condition | `uv run python scripts/analysis/fpfn_table.py` |

**Two aggregations of mAP.** `tables/master_metrics_table.md` regenerates exactly from the local row table and gives clean mAP 72.89, LiDAR Gaussian noise medium 23.71, high 21.56. The thesis figure gives 73.99, 18.54, 17.45 (R_b^c 0.251 / 0.236). Both use the same data: the figure's FP/FN counts (clean 4,900 / 8,287; LiDAR noise medium 1,175 / 29,214) match `row_table_iou03.parquet` exactly. 72.89 equals the mean of the thesis's per-class BEV APs ((77.86 + 67.93) / 2), which suggests the table averages per class and the figure pools both labels. A pooled AP was not recomputed to confirm. The README quotes the thesis figure.

Excluded by design: `frame_deletion` (pipeline crashed; no metrics) and mFR (not implemented).
