# K-Radar Visibility Pipeline

This package computes per-object, per-frame sensor visibility scores for the K-Radar dataset. It fuses radar, LiDAR (OS2-64 and OS1-128), and four camera modalities (front, left, right, rear) to produce visibility flags and confidence scores, outputting a single Parquet table for downstream analysis.

## Architecture

The data flow follows these steps:

1. **Parse labels** – Read `info_label_rev2/*.txt` files to extract frame headers and object annotations.
2. **Load sensor data** – For each frame:
   - Radar: load the corresponding `radar_zyx_cube/*.mat` file.
   - LiDAR: load OS2-64 and OS1-128 point clouds from `os2-64/*.pcd` and `os1-128/*.pcd`.
   - Cameras: load left/right stereo image pairs for each direction.
3. **Load calibration** – Retrieve extrinsic (`T_radar2cam`) and intrinsic matrices for each camera, plus LiDAR-to-radar extrinsics (implicit in point cloud framing).
4. **Compute visibility per sensor**:
   - Radar: compute SNR-weighted sparsity score within the object’s voxel bounding box.
   - LiDAR: count points inside the object’s 3D bounding box, normalize by expected density, optionally apply occlusion fraction from a precomputed range image.
   - Camera: project the 3D bounding box corners, compute a visibility score based on clipped area and centrality, optionally apply depth‑buffer occlusion discount.
5. **Aggregate results** – Determine the primary sensor (highest score) and compute a ghost‑flag sanity check (visible in radar but not in any other modality).
6. **Output** – Assemble all fields into a Polars DataFrame and write to Parquet (or return as DataFrame).

## Module Reference

### `src/kradar_visibility/__init__.py`
Public interface: re-exports key functions and classes from submodules, and provides a `main()` placeholder.

### `src/kradar_visibility/pipeline.py`
Orchestrates the full pipeline: parses labels, loads sensor data and calibration, iterates over frames and objects, calls visibility functions, and builds the output DataFrame. Includes helper functions for radar voxelization, FOV/range checks, rotated bounding‑box corners, and radar cube shape validation.

### `src/kradar_visibility/lidar_visibility.py`
Implements LiDAR visibility for both OS2‑64 and OS1‑128 sensors:
- `prepare_frame_lidar`: (optional) generates a range image from raw point clouds.
- `calculate_lidar_visibility`: counts points inside supplied axis‑aligned bounding boxes, computes a density ratio (point count / expected density), and, when a range image is provided, refines the score with an occlusion fraction derived from the range image.

### `src/kradar_visibility/radar_visibility.py`
Implements radar visibility:
- `compute_radar_sparsity_score`: computes an SNR‑weighted power density score for a single bounding box, normalised to `[0, 1]` using a CFAR‑style noise floor (global median, pre‑computed map, or scalar value).
- `radar_visibility`: vectorised wrapper that applies the score to a list of bounding boxes.

### `src/kradar_visibility/camera_visibility.py`
Implements visibility for the four stereo camera pairs:
- `project_point_to_image`: projects 3D radar‑frame points to image coordinates, optionally applying radial/tangential distortion correction.
- `calculate_visibility_score`: scores a single camera view based on projected 2D bounding box area and centrality, with optional depth‑buffer occlusion discount.
- `calculate_camera_visibility`: computes scores for all four directions (front, left, right, rear) by taking the maximum of the two stereo sub‑cameras per direction.

### `src/kradar_visibility/calibration.py`
Loads and provides access to camera intrinsics and extrinsics (radar‑to‑camera) for each sequence and stereo sub‑camera. Includes helper functions to retrieve specific parameters and the camera map.

### `src/kradar_visibility/parser.py`
Parses K‑Radar label files into structured `HeaderInfo` and `ObjectAnnotation` objects. Also provides utilities to enumerate label files per sequence and parse `description.txt` for weather labels.

### `src/kradar_visibility/data_loader.py`
Loads the raw sensor files:
- `load_radar_cube`: reads MATLAB `.mat` files containing the radar zyx_cube.
- `load_lidar_points`: reads PCD files and returns `(N, 3)` arrays.
- `load_camera_image`: loads PNG images and returns `(H, W, 3)` uint8 arrays.
- Helper functions to construct file paths and read PCD files.

### `src/kradar_visibility/config.py`
Contains constants used throughout the package:
- Radar field‑of‑view, maximum range, and grid dimensions.
- LiDAR sensor specifications (channels, vertical FOV, horizontal resolution) and pre‑computed expected densities.
- Camera image dimensions (half‑width/height for each stereo half).
- Derived constants such as expected LiDAR point densities per square metre.

## Methodology Summary

### Radar
The radar visibility score is an SNR‑weighted power density metric. For each object’s voxel bounding box, the mean signal‑to‑noise ratio (in dB) is computed relative to a noise floor estimated from the radar cube (either a global median, a pre‑computed CFAR map, or a supplied scalar). The SNR is then clipped and normalised by a headroom constant (`DB_HEADROOM`) to yield a score in `[0, 1]`, where 0 indicates no detectable signal and 1 indicates an average SNR at or above the headroom threshold.

### LiDAR
LiDAR visibility follows the method outlined in §4.2 of the methodology: the number of LiDAR points falling inside an object’s axis‑aligned 3D bounding box is counted and divided by an expected density value derived from the sensor’s angular resolution (channels × vertical FOV / 360 × 360 / horizontal resolution). This yields a raw density ratio in `[0, ∞)`. When a precomputed range image is available, an occlusion fraction is estimated by comparing the range image values along lines of sight to the object's corners; the final score is the density ratio scaled by `(1 − occlusion_fraction × confidence)`, where confidence reflects the validity of the range‑image samples.

### Camera
Camera visibility follows a pinhole projection model (§4.3). The eight corners of an object’s 3D bounding box are projected into the image plane using camera intrinsics and extrinsics. If any corner projects behind the camera (`z_cam ≤ 0`), the object is deemed invisible. Otherwise, the projected 2D bounding box is clipped to the image boundaries, and a score is computed as a weighted sum of:
- **Projected‑area weight (W1 = 0.7)**: fraction of the image covered by the clipped box.
- **Centrality weight (W2 = 0.3)**: how close the box centre is to the image centre.
If a depth map is provided, an occlusion discount is applied: for each projected corner, if the depth map value is positive and less than the projected depth, an occlusion ratio is computed; the average ratio reduces the score proportionally.

## Schema Reference

The output Parquet file contains one row per (frame, object) with the following columns:

| Column | Description |
|--------|-------------|
| `sequence_id` | K‑Radar sequence identifier (string). |
| `frame_idx` | Index of the tesseract frame within the sequence. |
| `obj_tracking_id` | Unique object tracking ID from the label file. |
| `obj_class` | Object class label (e.g., `Car`, `Pedestrian`). |
| `radar_visible` | Boolean: object center is within radar FOV and maximum range. |
| `radar_sparsity_score` | Float in `[0, 1]`: SNR‑weighted radar power density score. |
| `lidar64_visible` | Boolean: object has at least one OS2‑64 LiDAR point inside its bounding box and passes FOV/range checks. |
| `lidar64_points_count` | Integer: raw count of OS2‑64 LiDAR points inside the bounding box. |
| `lidar64_sparsity_score` | Float in `[0, 1]`: LiDAR64 visibility score (density ratio, optionally occlusion‑adjusted). |
| `lidar128_visible` | Boolean: analogous for OS1‑128 LiDAR. |
| `lidar128_points_count` | Integer: raw count of OS1‑128 LiDAR points inside the bounding box. |
| `lidar128_sparsity_score` | Float in `[0, 1]`: LiDAR128 visibility score. |
| `cam_front_visible` | Boolean: object is visible in at least one of the two front stereo sub‑cameras. |
| `cam_front_visibility_score` | Float in `[0, 1]`: maximum visibility score of the two front sub‑cameras. |
| `cam_left_visible` | Boolean: object is visible in at least one left stereo sub‑camera. |
| `cam_left_visibility_score` | Float in `[0, 1]`: maximum visibility score of the two left sub‑cameras. |
| `cam_right_visible` | Boolean: object is visible in at least one right stereo sub‑camera. |
| `cam_right_visibility_score` | Float in `[0, 1]`: maximum visibility score of the two right sub‑cameras. |
| `cam_rear_visible` | Boolean: object is visible in at least one rear stereo sub‑camera. |
| `cam_rear_visibility_score` | Float in `[0, in `[0, 1]`: maximum visibility score of the two rear sub‑cameras. |
| `ghost_flag` | Boolean: true if the object is marked radar‑visible but invisible in all LiDAR and camera modalities (a sanity check for spurious radar detections). |

## Known Limitations / Explicitly Out of Scope

- **Doppler‑coherence gating**: The original radar design intended to use Doppler velocity information (requires RTK‑GPS/INS) to gate moving versus static points. This component was **not implemented** because the K‑Radar dataset does not provide RTK‑GPS/INS streams, making Doppler‑based gating infeasible. The radar score relies solely on signal power (sparsity) within the voxel box.
- **Camera temporal consistency**: The pipeline is deliberately **per‑frame and stateless**; no temporal smoothing or multi‑frame consistency checks are performed. This aligns with the requirement that each frame be processed independently, simplifying parallelisation and avoiding error propagation across frames. Consequently, any notion of tracking‑based visibility persistence is out of scope.