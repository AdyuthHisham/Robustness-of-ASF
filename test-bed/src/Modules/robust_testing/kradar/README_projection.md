# K-Radar 3D Bounding Box to Camera Projection

This script projects 3D bounding boxes from K-Radar annotation files onto camera images using the dataset's calibration data.

## Overview

The script:
1. Reads K-Radar annotation files (`info_label_rev2/*.txt`)
2. Loads camera calibration data (intrinsics + extrinsics)
3. Computes 3D bounding box corners in the radar/LiDAR coordinate frame
4. Projects corners to 2D image plane using camera calibration
5. Draws 3D wireframe boxes on the camera image
6. Saves annotated images

## Dependencies

- Python 3.8+
- numpy
- opencv-python
- kradar_visibility package (local)

Install dependencies:
```bash
cd /home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar
uv add numpy opencv-python
```

## Usage

```bash
cd /home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar

# Process first 3 frames from sequence 1, front camera
uv run python project_bbox_to_camera.py --sequence 1 --camera cam-front --frames 3

# Process specific frame with verbose output
uv run python project_bbox_to_camera.py --sequence 1 --camera cam-front --specific-frame 00132_00100 --verbose

# Process sequence 2, 3 frames
uv run python project_bbox_to_camera.py --sequence 2 --camera cam-front --frames 3
```

### Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--sequence` | `-s` | `1` | Sequence folder name in `data/` |
| `--camera` | `-c` | `cam-front` | Camera: `cam-front`, `cam-left`, `cam-right`, `cam-rear` |
| `--frames` | `-f` | `3` | Number of frames to process (from start) |
| `--output-dir` | `-o` | `output/projections` | Output directory for annotated images |
| `--dataset-root` | `-d` | `/home/adhish/Productivity/AMSCUP/repos/K-Radar` | Dataset root path |
| `--verbose` | `-v` | - | Print detailed projection math for first object |
| `--specific-frame` | - | - | Process specific frame (e.g., `00132_00100`) |

## Output

Annotated images saved to `output/projections/` with naming:
```
seq_{sequence}_frame_{camera_frame_idx}_projected.png
```

Example: `seq_1_frame_00299_projected.png`

## Coordinate Systems

- **Radar/LiDAR frame**: X=forward, Y=left, Z=up (annotation coordinates)
- **Camera frame**: Standard pinhole camera (Z=forward, X=right, Y=down)
- **Image plane**: (u,v) pixels, origin at top-left

## Calibration Data

The script uses the calibration pickle files in:
```
/home/adhish/Productivity/AMSCUP/repos/K-Radar/resources/cam_calib/T_params_seq/{seq_id}
```

Each camera has:
- `camera_intrinsics`: 4x4 matrix with K in top-left 3x3
- `radar2camera`: 4x4 extrinsic transform (radar → camera frame)
- `camera2radar`: 4x4 inverse transform

## Annotation Format

Each `info_label_rev2/XXXXX_YYYYY.txt` file:
- **Line 1**: Header with sensor indices mapping
  - `cam-front_idx` gives the front camera image filename
- **Lines 2+**: Object annotations
  - Format: `*, SENSOR_ID, TRACK_ID, CLASS, X, Y, Z, THETA, HL, HW, HH`
  - Dimensions are HALF-sizes (multiply by 2 for full L/W/H)
  - Theta is heading in radians

## Verification Example

For frame `00132_00100` from sequence 1, first object (Sedan, ID 0):

```
Raw annotation:
  Center: (85.285, -3.195, 0.962)
  Half-dims: l=2.186, w=1.043, h=0.630
  Theta: -0.168 rad (-9.6 deg)

3D Corners (radar frame):
  0: (82.956, -3.858, 0.332)
  1: (82.956, -3.858, 1.592)
  2: (83.304, -1.802, 0.332)
  3: (83.304, -1.802, 1.592)
  4: (87.266, -4.588, 0.332)
  5: (87.266, -4.588, 1.592)
  6: (87.614, -2.532, 0.332)
  7: (87.614, -2.532, 1.592)

Camera coords (Z): all > 0 (in front of camera)
Projected pixels: u≈640-660, v≈370-380 (within 2560x720 image)
```

## Architecture

The script reuses existing modules from `kradar_visibility`:
- `parser.py` - Annotation parsing
- `calibration.py` - Calibration loading
- `data_loader.py` - Image loading

New functions in `project_bbox_to_camera.py`:
- `compute_3d_corners()` - 8-corner box generation
- `project_corners_to_image()` - 3D→2D projection
- `draw_3d_box()` - Wireframe drawing on image
- `process_frame()` - Per-frame pipeline
- `main()` - CLI entry point

## Edge Cases Handled

- Missing calibration files → graceful error
- Missing camera images → graceful error
- Empty annotations → saves clean image
- Points behind camera (Z≤0) → filtered out
- Points outside image bounds → filtered from drawing
- Distortion coefficients (optional, not in current calibration)

## Troubleshooting

**No objects projected?**
- Check that the frame has objects (some frames have 0 annotations)
- Verify camera calibration loaded correctly

**Image not found?**
- Camera images may have different frame indices than cam-front_idx
- The script uses cam-front_idx for all cameras (known limitation)

**Wrong projection?**
- Verify calibration sequence ID matches data sequence
- Check coordinate system conventions (X-forward, Y-left, Z-up)