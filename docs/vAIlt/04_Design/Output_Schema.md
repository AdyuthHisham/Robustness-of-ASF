# Output Schema

One row per (sequence, frame, tracked object) in the `kradar_visibility` Parquet output. Column order and names are defined in `config.OUTPUT_SCHEMA` — **a single source of truth that downstream queries depend on exactly**; changing a column name is a breaking change (see `AGENTS.md`).

| Column | Type | Source |
|---|---|---|
| `sequence_id` | str | folder name |
| `frame_idx` | int | header `tesseract_idx` |
| `timestamp` | float64 | header |
| `obj_tracking_id` | int | annotation |
| `obj_class` | str | annotation |
| `obj_x` / `obj_y` / `obj_z` | float | annotation (meters) |
| `obj_theta` | float | annotation (radians) |
| `obj_length` / `obj_width` / `obj_height` | float | annotation (full extent, meters — doubled from the half-dimensions in the raw label) |
| `obj_distance_ego` | float | computed, `√(x²+y²+z²)` |
| `sensor_identify` | str | annotation (which sensor(s) the original K-Radar label used) |
| `radar_visible` / `radar_fov_in` / `radar_range_in` | bool | computed, see [[03_Theory/Visibility_Formulas]] |
| `radar_sparsity_score` | float | `radar_visibility` module |
| `lidar64_visible` / `lidar64_points_count` / `lidar64_sparsity_score` | bool / int / float | `lidar_visibility` module, OS2-64 |
| `lidar128_visible` / `lidar128_points_count` / `lidar128_sparsity_score` | bool / int / float | `lidar_visibility` module, OS1-128 |
| `cam_{dir}_visible` | bool | `camera_visibility` module, `dir ∈ {front, left, right, rear}` |
| `cam_{dir}_proj_x` / `cam_{dir}_proj_y` | float | `camera_visibility` module — object **center** projection, pixels; `null` when not visible |
| `cam_{dir}_visibility_score` | float | `camera_visibility` module |
| `num_sensors_visible` | int | computed, count of `*_visible=True` across all 7 sensors |
| `primary_sensor` | str | computed, `argmax` of score among visible sensors |

44 columns total (per `api_contracts.md` — see [[API_Contracts]] for the `config.py` constant reference this schema is generated from).

## Fields planned but not yet present (open gaps as of 2026-08-10)

Per the open questions logged in [[Noise_Taxonomy]]:
- Per-frame object-density feature (count of objects identified per sensor per frame).
- Full `description.txt` environment fields — only `weather` is currently captured; `location`/`Environment` and `time`/`Time of Day` are parsed by `parser.parse_description_txt()` but not yet joined into the visibility output schema.
- A bounding-box-deviation metric between clean and corrupted inference (planned for the noise-injection evaluation, not the visibility schema itself).

## Source

- `test-bed/src/Modules/robust_testing/kradar/architecture.md` §"Output Schema"
- `test-bed/src/Modules/robust_testing/kradar/api_contracts.md` (`config.py` §`OUTPUT_SCHEMA`)
- `docs/Black_Book.md` (10/August entry — gap list)
