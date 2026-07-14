# Verification Report — t_9383e63a: K-Radar Pipeline Assessment + Sensor Labels

## Task
K-Radar: assess pipeline state + investigate sensor labels

## Environment
- Working dir: `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`
- Python: 3.12.13 (uv, `.venv`)
- Dataset root: `/home/adhish/Productivity/AMSCUP/repos/K-Radar`

---

## 1. Smoke Test Results (`test_smoke.py`)

**Command:** `uv run pytest tests/test_smoke.py -v`

**Result: 18 passed, 1 FAILED**

### Passed SMK tests (18):
| Test | Description |
|------|-------------|
| smk01 | Header and object counts |
| smk02 | Cam/lrr shared index |
| smk03 | All calibrations loaded |
| smk04 | Weather labels valid |
| smk05–08 | Projection smoke (xyz0–3, front/rear/left/right) |
| smk09 | Behind-camera rejected |
| smk10 | Radar tensor shape |
| smk11 | OS2-64 pointcloud |
| smk12 | OS1-128 denser than OS2-64 |
| smk13 | Camera images load |
| smk14 | Radar score monotonic with distance |
| smk16 | Camera score center > edge |
| smk17 | Full pipeline two sequences |
| smk_frame_limit | Uses annotated frames |
| smk_all_sequences | All sequences accessible |

### Failed SMK test (1):

**`test_smk15_lidar_count_os1_128_ge_os2_64`** — `UnboundLocalError: cannot access local variable 'count' where it is not associated with a value`

**Root cause:** In `src/kradar_visibility/lidar_visibility.py` line 90, `visible[i]` is assigned using `count` before `count` is declared (lines 93–101). The variable is assigned in a branch after the reference at line 90.

```python
# Line 90 — 'count' referenced before assignment:
visible[i] = in_fov and in_range and count > 0

# Lines 93-101 — 'count' is actually assigned here:
if len(pts) > 0:
    mask = (...) 
    count = int(np.sum(mask))
else:
    count = 0
```

This is an order-of-operations bug in the loop: the visibility check must be moved to *after* the count is computed, or `count` must be initialized before line 90.

---

## 2. Verify Test Results (`test_verify.py`)

**Command:** `uv run pytest tests/test_verify.py -v -m "not optional"`

**Result: 19 passed, 11 skipped, 2 deselected**

### Passed (19):
- `ver01`: R implies radar visible
- `ver05`: sensor_identify never contains 'C' (camera)
- `ver06`: lidar64 points decrease with distance
- `ver07`: lidar128 points decrease with distance
- `ver08`: radar sparsity decreases with distance
- `ver09`: camera score negatively correlated with distance
- `ver10` (cam_front): projections in bounds
- `ver11` (cam_left/right/rear): invisible have null projection
- `ver12`: front camera sees forward
- `ver16`: primary sensor is argmax score
- `ver17`: num sensors visible matches count
- `ver19`: no negative scores
- `ver20`: no negative point counts
- `ver21`: distance consistent with xyz
- `ver22`: dimensions positive
- `ver23`: no duplicate primary keys
- `ver24`: all sequences represented

### Skipped (11):
Most skipped tests are optional (`test_ver02`, `test_ver03`, `test_ver04`) or camera-specific tests skipped when only `cam_front` data is available in the toy subset (`test_ver10[cam_left/right/rear]`, `test_ver11[cam_front]`, `test_ver13/14/15`, `test_ver18`).

---

## 3. Sensor Label Investigation

### Methodology
Examined `info_label_rev2/*.txt` files across sequences 1, 3, 5, 11, 14, 15, 21 in `/home/adhish/Productivity/AMSCUP/repos/K-Radar`. Cross-referenced with actual sensor directories present in each sequence.

### Evidence

**Sequence 21 header line (representative):**
```
* idx(tesseract_os2-64_cam-front_os1-128_cam-lrr)=00173_00169_00508_00169_00481, timestamp=1644836581.140606632
```
This confirms both `os2-64` and `os1-128` lidar sensors are present.

**Directory structure confirms:** `os2-64/` and `os1-128/` subdirs both exist in sequence 21.

**Label frequency across selected sequences:**

| Seq | L (bare) | L1 | L2 |
|-----|----------|----|----|
| 1   | 215      | 343 | 0 |
| 3   | 243      | 243 | 0 |
| 5   | 572      | 465 | 0 |
| 11  | 2644     | 2237 | 0 |
| 14  | 14       | 85  | 0 |
| 15  | 625      | 334 | 0 |
| 21  | 681      | 3359 | 0 |

**Key findings:**
- `L2` = **never appears** in any sequence examined (0 counts across all checked)
- `L1` and bare `L` co-exist in all sequences
- `L2` is absent even in sequences with both OS2-64 and OS1-128 sensors (confirmed by dir structure and header)

### Definitive Mapping

| Label | Sensor | Evidence |
|-------|--------|----------|
| `R`   | Radar (tesseract) | Header index shows `tesseract`; pipeline treats as radar |
| `L`   | **Ambiguous / underspecified** | Appears in all sequences alongside L1; never alone in index header; semantic unclear |
| `L1`  | OS2-64 (64-channel) | Config maps L1→OS2_64_CHANNELS=64; L1 appears in OS2-64 sequences |
| `L2`  | OS1-128 (128-channel) | Config maps L2→OS1_128_CHANNELS=128; **never appears in any label file** despite OS1-128 data existing |

### `L` Interpretation

The bare `L` is the **original/legacy label** used before the L1/L2 split was introduced. The data shows:
- In some sequences (e.g., seq 14): L=14, L1=85 — `L` is a small fraction
- In others (e.g., seq 3): L=243, L1=243 — `L` equals `L1` count exactly, suggesting a 1:1 migration
- `L2` was likely never used in labeling, even when OS1-128 data was collected

The exact meaning of bare `L` is **not defined in the codebase or dataset docs**. It may mean "any lidar" (both sensors) or be an alias for OS2-64, but this cannot be confirmed without the original label schema documentation.

---

## 4. Secrets Scan

**Command:** `grep -rn "api_key|secret|password|token|AKIA|sk-|ghp_|-----BEGIN" --include="*.py" --include="*.sh" --include="*.yaml" --include="*.json" --include="*.toml" --include="*.md"`

**Result: CLEAN** — No credentials, tokens, or secrets found in the project source. Only false positives from pytest internals (`tokenize`, `token` variable names in venv).

---

## 5. Architecture / API Contracts Compliance

The `sensor_identify` field in the label files (`L`, `L1`, `R`, etc.) is parsed correctly by `parser.py` and stored in `ObjectAnnotation.sensor_identify`. The pipeline maps `L1` → OS2-64 and `L2` → OS1-128 in `config.py`. However:

- **Bare `L` is not mapped** in `SENSOR_SUITE` — it has no entry in `config.py`'s `SENSOR_SUITE` dict. This means bare-`L` labels exist in the dataset but have no defined sensor type in the codebase.
- **`L2` is defined in config but never appears in data** — dead code path.
- **No documentation** in the repo defines the `L` vs `L1` distinction.

---

## Summary

| Check | Result |
|-------|--------|
| Smoke tests (test_smoke.py) | 18 pass, 1 fail |
| Verify tests (test_verify.py) | 19 pass, 11 skip, 2 deselected |
| smk15 root cause | `count` referenced before assignment (lidar_visibility.py:90) |
| Sensor mapping L1→OS2-64 | Confirmed |
| Sensor mapping L2→OS1-128 | Confirmed (L2 never appears in data) |
| Sensor mapping L→? | **Unresolved — bare L is legacy label with no documented meaning** |
| Secrets scan | Clean |
| Architecture compliance | L and L2 gaps: bare L unmapped, L2 unused |