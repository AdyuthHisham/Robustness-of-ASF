# K-Radar Visibility Visual Verification & Web UI Specification

> **Document Type:** Standalone implementation spec  
> **Working Directory:** `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`  
> **Dataset Root:** `/home/adhish/Productivity/AMSCUP/repos/K-Radar`  
> **Reference Spec Documents:** `/home/adhish/Downloads/`  
> **Execution Mode:** CPU-Only / Validation-Only  
> **Scope:** Visual inspection tool + Web UI for manual verification of pipeline output

---

## 1. Overview

This document specifies a **visual verification toolkit** for the `kradar_visibility` pipeline. It provides:

1. A **command-line script** to manually inspect 5 diverse annotation instances across radar, LiDAR, and camera views
2. A **web-based UI** (Marimo notebook or Streamlit) to interactively browse all sensor data for any given `info_label_rev2` annotation
3. **Bounding box overlay** on all sensor modalities for ground-truth vs. computed visibility validation

The tool reads from the existing pipeline output (`outputs/smoke_output_*.parquet`) and raw K-Radar sensor files (`radar_zyx_cube/`, `os2-64/`, `os1-128/`, `cam-front/`, `cam-left/`, `cam-right/`, `cam-rear/`).

The reference specification documents that define the pipeline requirements, methodology, and test scaffolds are located in `/home/adhish/Downloads/`:

| Document | Purpose |
|----------|---------|
| `00_orchestrator_kickoff_prompt.md` | Orchestrator task definition, build phases, constraints |
| `04_visibility_methodology.md` | Radar (Section 4.1 Method B), LiDAR (Section 4.2 Method A+B), Camera (Section 4.3 Method B) |
| `06_smoke_tests_scaffold.md` | SMK-01..17 smoke test definitions |
| `07_verification_tests_scaffold.md` | VER-01..26 verification test definitions |
| `08_readme_spec.md` | README requirements and section definitions |
| `kradar_visibility_analysis_prompt.md` | Full spec: sensor suite, label format (Section 2), output schema (Section 3.1), goals (Section 5) |
| `goals_and_subgoals.md` | Hierarchical goals and sub-goals for the build |

---

## 2. Goals & Sub-Goals

### Goal 1: Manual Visual Inspection of 5 Diverse Annotation Instances

Manually verify pipeline correctness by visually inspecting 5 annotation instances that vary across weather conditions, sensor activation patterns, distances, and object classes.

#### Sub-Goal 1.1: Select 5 Diverse Instances
- Query the pipeline Parquet output to select 5 instances covering:
  - **Weather diversity:** At least 2 different conditions from `description.txt` (e.g., clear, rain, snow)
  - **Sensor count diversity:** Instances where 1, 2, 3, and 4+ sensors are active
  - **Sensor identify diversity:** Mix of `R`, `L1`, `L2`, `L`, `RL1`, `L1L2` in `sensor_identify`
  - **Distance diversity:** Close (<30m), medium (30-70m), far (>70m)
  - **Object class diversity:** Sedan, Bus or Truck, Pedestrian, etc.

#### Sub-Goal 1.2: Generate Per-Instance Visualization Figures
For each selected instance, generate a matplotlib figure with subplots showing:
- **Radar:** 3D bbox overlaid on `radar_zyx_cube` max-projection with colorbar
- **LiDAR-64:** 3D scatter with bbox wireframe; in-box points highlighted red
- **LiDAR-128:** Same as above for OS1-128
- **Camera Front:** Stitched image (2560x720) with projected 8 corners + center dot
- **Camera Left:** Same as above
- **Camera Right:** Same as above
- **Camera Rear:** Same as above

#### Sub-Goal 1.3: Produce Inspection Report
- Save figures to `outputs/verification_figs/`
- Generate a markdown table summarizing expected vs. observed visibility per sensor

---

### Goal 2: Web UI for Interactive Sensor Data Exploration

Build a browser-based UI to view all radar/LiDAR point clouds and camera images for any annotation.

#### Sub-Goal 2.1: Marimo Notebook UI
Create a `scripts/visualize_sensor_data.py` Marimo notebook that:
- Accepts `sequence_id`, `frame_idx`, and `obj_tracking_id` as inputs
- Loads the corresponding `info_label_rev2/*.txt` file
- Displays all 4 camera images with bounding box overlays
- Displays LiDAR-64 and LiDAR-128 point clouds with bbox wireframe
- Displays radar cube as a heatmap with bbox overlay
- Shows the pipeline-computed visibility scores in a sidebar

#### Sub-Goal 2.2: Standalone Streamlit Fallback
If Marimo is unavailable, provide an equivalent `scripts/visualize_streamlit.py`.

---

### Goal 3: Bounding Box Overlay on All Modalities

Given any `info_label_rev2/*.txt` file path, render all annotated bounding boxes on:
- **LiDAR point clouds** (3D scatter + oriented bbox wireframe)
- **Camera images** (2D projected bbox from 8-corner projection)
- **Radar cube** (3D heatmap slice + axis-aligned bbox region)

#### Sub-Goal 3.1: Unified BBox Rendering
Reuse the existing `get_bbox_corners()` logic from `pipeline.py` for consistency.

#### Sub-Goal 3.2: Multi-Object Support
Handle label files with multiple object lines (not just the first object).

---

## 3. Architecture

```
inputs:
  info_label_rev2/*.txt          -> parser.py (existing)
  radar_zyx_cube/*.mat           -> data_loader.py (existing)
  os2-64/*.ped, os1-128/*.ped   -> data_loader.py (existing)
  cam-*/cam-*_*.png             -> data_loader.py (existing)
  outputs/smoke_output_*.parquet -> pipeline output (existing)

scripts/visualize_instances.py    -> CLI tool for Goal 1 (5-instance inspection)
scripts/visualize_sensor_data.py  -> Marimo notebook for Goal 2 (interactive UI)
scripts/visualize_streamlit.py    -> Streamlit fallback for Goal 2

outputs:
  outputs/verification_figs/      -> PNG figures per instance
  outputs/verification_report.md   -> Summary markdown table
```

---

## 4. File Layout

```
/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar/
├── src/kradar_visibility/          # Existing pipeline modules
│   ├── __init__.py
│   ├── config.py
│   ├── parser.py
│   ├── calibration.py
│   ├── data_loader.py
│   ├── radar_visibility.py
│   ├── lidar_visibility.py
│   ├── camera_visibility.py
│   └── pipeline.py
├── scripts/
│   ├── run_pipeline.py             # Existing CLI entry point
│   ├── visualize_instances.py      # NEW: Goal 1 - 5-instance visual inspection
│   ├── visualize_sensor_data.py    # NEW: Goal 2 - Marimo interactive UI
│   └── visualize_streamlit.py      # NEW: Goal 2 - Streamlit fallback
├── outputs/
│   ├── smoke_output.parquet        # Existing pipeline output
│   ├── smoke_output_1.parquet
│   ├── smoke_output_2.parquet
│   ├── smoke_output_3.parquet
│   ├── verification_report.md      # Existing
│   └── verification_figs/        # NEW: Generated PNGs
├── tests/
│   ├── conftest.py
│   ├── test_smoke.py
│   └── test_verify.py
└── README.md
```

---

## 5. Module Reference

### 5.1 `scripts/visualize_instances.py`

**Purpose:** Command-line tool to select and visualize 5 diverse annotation instances.

**Key Functions:**

```python
def select_diverse_instances(
    parquet_path: Path,
    n: int = 5,
    dataset_root: Path = config.DATASET_ROOT,
) -> pl.DataFrame:
    # Select n instances with maximum diversity across weather,
    # num_sensors_visible, sensor_identify, distance bins, and obj_class.

def render_instance(
    row: dict,
    dataset_root: Path,
    output_dir: Path,
) -> Path:
    # Generate a 7-subplot figure for one instance:
    # - Radar cube with bbox overlay
    # - LiDAR-64 scatter with bbox
    # - LiDAR-128 scatter with bbox
    # - Camera front/left/right/rear with projected bbox
    # Save as PNG to output_dir.

def build_inspection_report(
    instances: pl.DataFrame,
    output_path: Path,
) -> None:
    # Generate markdown table comparing expected vs. observed visibility.
```

**Dependencies:** `polars`, `numpy`, `matplotlib`, `scipy`, `PIL`, existing `kradar_visibility` package.

**Usage:**
```bash
uv run python scripts/visualize_instances.py \
  --parquet outputs/smoke_output_2.parquet \
  --dataset-root /home/adhish/Productivity/AMSCUP/repos/K-Radar \
  --output-dir outputs/verification_figs/
```

---

### 5.2 `scripts/visualize_sensor_data.py` (Marimo)

**Purpose:** Interactive notebook to explore any annotation instance.

**UI Layout:**

```
+-------------------------------------------------------------+
|  [Sequence ID: ___]  [Frame Idx: ___]  [Obj Tracking ID: ___] |
|                    [Load Button]                              |
+-------------------------------------------------------------+
|  Sidebar (Left)          |  Main View (Right)               |
|  ---------------------   |  -----------------------------    |
|  Pipeline Scores:        |  +---------------------------+    |
|    radar_visible: True   |  |    Camera Front (2560x720) |    |
|    radar_score: 0.0146   |  |    [bbox overlay]          |    |
|    lidar64_visible: F    |  +---------------------------+    |
|    lidar64_count: 8      |  +---------+ +---------+        |
|    lidar128_visible: F   |  | Cam Left| |Cam Right|        |
|    cam_front_visible: T  |  | [bbox]  | | [bbox]  |        |
|    cam_front_score: 0.28 |  +---------+ +---------+        |
|    primary_sensor: cam_f |  +---------------------------+    |
|                          |  |    Camera Rear             |    |
|  Object Info:            |  |    [bbox overlay]          |    |
|    class: Sedan          |  +---------------------------+    |
|    distance: 95.6m       |                                   |
|    sensor_identify: L1   |  +---------------------------+    |
|                          |  |    LiDAR-64 (3D scatter) |    |
|                          |  |    [bbox wireframe]        |    |
|                          |  +---------------------------+    |
|                          |  +---------------------------+    |
|                          |  |    LiDAR-128 (3D scatter)|    |
|                          |  |    [bbox wireframe]        |    |
|                          |  +---------------------------+    |
|                          |  +---------------------------+    |
|                          |  |    Radar Cube (heatmap)    |    |
|                          |  |    [bbox region]           |    |
|                          |  +---------------------------+    |
+-------------------------------------------------------------+
```

**Key Cells:**

```python
# Cell 1: Imports
import marimo as mo
from kradar_visibility import config, parser, data_loader, calibration
from kradar_visibility.camera_visibility import get_bbox_corners, project_point_to_image
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Cell 2: Inputs
sequence_id = mo.ui.text(label="Sequence ID", value="2")
frame_idx = mo.ui.text(label="Frame Idx", value="70")
obj_tracking_id = mo.ui.text(label="Obj Tracking ID", value="11")
load_button = mo.ui.button(label="Load & Render")

# Cell 3: Load data on button click
def load_and_render(seq, frame, track_id):
    # Parse label file
    # Load all sensor data
    # Generate matplotlib figures
    # Return as mo.vstack of images
```

**Usage:**
```bash
uv run marimo edit scripts/visualize_sensor_data.py
```

---

### 5.3 `scripts/visualize_streamlit.py` (Fallback)

**Purpose:** Equivalent Streamlit app if Marimo is not preferred.

**Usage:**
```bash
uv run streamlit run scripts/visualize_streamlit.py
```

---

## 6. Methodology for Visual Verification

### 6.1 Radar Cube Visualization (per 04_visibility_methodology.md Section 4.1 Method B)

**Input:** `radar_zyx_cube/*.mat` (3D array, Z x Y x X)

**Rendering:**
1. Load cube via `scipy.io.loadmat`
2. Compute max-projection along Z (elevation) -> 2D Y x X heatmap
3. Map bbox center (x, y, z) to cube indices using world-to-cube transform
4. Draw rectangle showing bbox extent in the XY plane
5. Colorbar showing power values (dB or linear)

**Validation Question:** Does the heatmap show returns inside the bbox? Does `radar_sparsity_score` reflect actual SNR-weighted power?

---

### 6.2 LiDAR Point Cloud Visualization (per 04_visibility_methodology.md Section 4.2 Method A+B)

**Input:** `os2-64/*.ped` or `os1-128/*.ped` (N x 3 point array)

**Rendering:**
1. Load points via `data_loader.load_lidar_points()`
2. Compute oriented bbox corners from annotation
3. Run point-in-box test (CPU, axis-aligned for visualization)
4. Plot all points in gray; in-box points in red
5. Draw bbox wireframe in blue

**Validation Question:** Does the red point count match `lidar64_points_count`? Are there red points outside the wireframe (false positives) or gray points inside (false negatives)?

---

### 6.3 Camera Image Visualization (per 04_visibility_methodology.md Section 4.3 Method B)

**Input:** `cam-*/cam-*_*.png` (2560 x 720 stitched stereo pair)

**Rendering:**
1. Load stitched image via `PIL.Image.open`
2. Split into left/right halves (1280 x 720 each)
3. For each stereo half:
   - Project 8 bbox corners via `project_point_to_image()`
   - Draw polygon connecting visible corners
   - Mark projected center with a dot
4. Show left and right halves side by side or overlay both projections

**Validation Question:** Does the projected bbox align with the actual object in the image? Is the center dot near the object center?

---

## 7. Selection Criteria for 5 Diverse Instances

Use this Polars query to select instances:

```python
import polars as pl

df = pl.read_parquet("outputs/smoke_output_2.parquet")

# Join weather info
weather_df = pl.DataFrame({
    "sequence_id": ["1", "2", "58"],
    "weather": ["clear", "clear", "heavy snow"],
})
df = df.join(weather_df, on="sequence_id", how="left")

# Select 5 instances
selected = (
    df
    .with_columns(
        pl.col("obj_distance_ego").cut([0, 30, 70, 120]).alias("dist_bin"),
    )
    .group_by(["weather", "num_sensors_visible", "sensor_identify", "dist_bin"])
    .agg(pl.all().first())
    .sort("weather", "num_sensors_visible")
    .head(5)
)
```

**Target diversity matrix:**

| # | Weather | Sensors Visible | sensor_identify | Distance | Class |
|---|---------|-----------------|-----------------|----------|-------|
| 1 | clear | 1 | R | <30m | Sedan |
| 2 | clear | 2 | L1 | 30-70m | Sedan |
| 3 | clear | 3 | RL1 | >70m | Bus or Truck |
| 4 | rain/snow | 2 | L | 30-70m | Sedan |
| 5 | clear | 4+ | L1L2 | <30m | Pedestrian |

*(Adjust based on actual data availability in the 2-sequence subset.)*

---

## 8. Setup & Usage

### 8.1 Install Dependencies

```bash
cd /home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar

# Add visualization dependencies
uv add matplotlib pillow scipy

# Optional: Marimo for interactive UI
uv add marimo

# Optional: Streamlit fallback
uv add streamlit
```

### 8.2 Run Visual Inspection (Goal 1)

```bash
# Generate 5-instance verification figures
uv run python scripts/visualize_instances.py \
  --parquet outputs/smoke_output_2.parquet \
  --dataset-root /home/adhish/Productivity/AMSCUP/repos/K-Radar \
  --output-dir outputs/verification_figs/

# View generated figures
ls outputs/verification_figs/
# -> instance_001_seq2_frame70_obj11.png
# -> instance_002_seq2_frame80_obj11.png
# -> ...
```

### 8.3 Launch Interactive UI (Goal 2)

```bash
# Marimo (recommended)
uv run marimo edit scripts/visualize_sensor_data.py

# Or Streamlit fallback
uv run streamlit run scripts/visualize_streamlit.py
```

### 8.4 Verify Bounding Box Overlay (Goal 3)

```bash
# Pass any info_label_rev2 file directly
uv run python scripts/visualize_instances.py \
  --label-file /home/adhish/Productivity/AMSCUP/repos/K-Radar/data/2/info_label_rev2/00070_00001.txt \
  --dataset-root /home/adhish/Productivity/AMSCUP/repos/K-Radar \
  --output-dir outputs/verification_figs/
```

---

## 9. Known Limitations

| Limitation | Explanation |
|------------|-------------|
| **Toy-scale only** | 2 sequences, 20 frames - may not cover all weather/sensor combinations |
| **CPU-only rendering** | 3D LiDAR plots may be slow for dense point clouds |
| **Axis-aligned LiDAR bbox** | Visual wireframe is axis-aligned; actual annotation uses oriented bbox - may cause minor misalignment |
| **Stitched camera images** | Camera images are 2560 x 720 stitched stereo pairs; UI splits into left/right halves but does not undistort |
| **Radar cube index mapping** | World-to-cube mapping is approximate (linear interpolation over fixed ROI); may not perfectly align with calibration |
| **No occlusion handling** | Camera bbox overlay does not account for occlusion by other objects (Method B only, per 04_visibility_methodology.md Section 4.3) |

---

## 10. Future Scope

| Feature | Priority | Notes |
|---------|----------|-------|
| Full 58-sequence dataset | High | Run on all sequences for comprehensive diversity |
| GPU-accelerated point-in-box | Medium | Use `points_in_boxes_gpu` for accurate LiDAR counts |
| Real-time Web UI | Medium | Streamlit/Gradio with frame slider |
| Occlusion-aware camera overlay | Low | Method C from 04_visibility_methodology.md Section 4.3 - LiDAR depth-buffer discount |
| Video export | Low | Generate MP4 of all frames for an object track |

---

## 11. References

All reference specification documents are located in `/home/adhish/Downloads/`:

| Document | File Path | Purpose |
|----------|-----------|---------|
| Orchestrator Kickoff | `/home/adhish/Downloads/00_orchestrator_kickoff_prompt.md` | Build phases, environment, constraints, delegation strategy |
| Visibility Methodology | `/home/adhish/Downloads/04_visibility_methodology.md` | Radar (Section 4.1 Method B), LiDAR (Section 4.2 Method A+B), Camera (Section 4.3 Method B) |
| Smoke Tests | `/home/adhish/Downloads/06_smoke_tests_scaffold.md` | SMK-01..17 test definitions |
| Verification Tests | `/home/adhish/Downloads/07_verification_tests_scaffold.md` | VER-01..26 test definitions |
| README Spec | `/home/adhish/Downloads/08_readme_spec.md` | README requirements (Section 11) |
| Analysis Prompt | `/home/adhish/Downloads/kradar_visibility_analysis_prompt.md` | Sensor suite (Section 1), label format (Section 2), schema (Section 3.1), goals (Section 5) |
| Goals & Sub-Goals | `/home/adhish/Downloads/goals_and_subgoals.md` | Hierarchical goal definitions |

- K-Radar repo: https://github.com/kaist-avelab/K-Radar

---

*Generated for K-Radar visibility pipeline visual verification. Refer to existing pipeline code in `src/kradar_visibility/` for actual function signatures and data loading logic.*
