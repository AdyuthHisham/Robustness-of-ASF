# Context-breakdown radar charts — ASF, K-Radar

**Script:** `test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py`
**Output:** `test-bed/src/Modules/robust_testing/kradar/output/context_radar_charts/`

Extends [[robustness-radar-charts]] with a context-field breakdown: 54 charts total
(3 metrics `mAP`/`mASE`/`mATE` × 3 context fields `time_of_day`/`weather`/`environment` ×
2 classes × 3 severities). `weather`/`environment`/`time_of_day` are already columns in
`row_table_iou03.parquet` (populated from K-Radar's per-sequence metadata), so no join was
needed to build this. Reuses `radar_charts.py`/`box_plots.py` conventions (axis codes, shared
per-class y-scale, `frame_deletion` handling).

Also edited `radar_charts.py` while building this: `frame_deletion` is now excluded from radar
chart axes specifically (`RADAR_AXIS_EFFECTS`), not from the box plots — per-user request,
scoped narrowly since [[robustness-metrics-tables]] documents `frame_deletion`'s crash-coverage
artifact as a data-quality issue affecting box plots too, but the radar-chart exclusion here was
a display choice, not a re-litigation of that bug.

## This work surfaced the frame-identifier bug

Building these charts, `bus`/`university` showed exactly 0% mAP across *every* condition,
including the clean `original` baseline — implausible enough to be a measurement artifact
rather than a detector result. That observation is what led to the frame-identifier
investigation — see [[frame-identifier-bug]] for the full root cause and fix.

**Caveat:** these 54 charts (and the tables in [[robustness-metrics-tables]]) were generated
from `row_table_iou03.parquet` data that still carries the frame-identifier bug's mislabeling.
TP/FP/FN/AP/ATE/ASE values are *not* corrupted by that bug (pairing within an `idx_datum` is
internally consistent — see [[frame-identifier-bug]]), so the metric values themselves should
still be trustworthy; only per-frame cross-referencing was broken. Regenerate once the Alvis
re-sweep with the fix completes, to be safe.
