# OUTPUT_SCHEMA Drift Fix

## What was wrong
`config.py`'s `OUTPUT_SCHEMA` listed 42 columns, but `pipeline.py` emits 44. Two columns — `timestamp` and `ghost_flag` — were missing from the canonical schema definition, creating schema drift where downstream consumers reading `OUTPUT_SCHEMA` would miss columns the actual parquet contains.

## Edits made
**File:** `src/kradar_visibility/config.py`

1. **Added `timestamp`** (line 82) right after `frame_idx`, matching pipeline.py's row-dict emission order at pipeline.py:440. Dtype: `Float64` (originates from `parser.py:HeaderInfo.timestamp: float`).

2. **Added `ghost_flag`** (line 123) after `primary_sensor` as the last entry, matching pipeline.py:481. Dtype: `Boolean`.

3. **`weather`** was confirmed present in all 44-column parquet outputs (dtype `String`, emitted at pipeline.py:480) and already listed at OUTPUT_SCHEMA line 93 — kept as-is.

## Before/After diff

```diff
 OUTPUT_SCHEMA = [
     "sequence_id",
     "frame_idx",
+    "timestamp",
     "obj_tracking_id",
     ...
     "primary_sensor",
+    "ghost_flag",
 ]
```

Count: 42 → 44 columns.

## Verification
Cross-check against `outputs/visibility_output.parquet` (a recent pipeline run):
- Schema columns: 44
- Parquet columns: 44
- Extra: none
- Missing: none
- Result: **PASS — zero mismatches**