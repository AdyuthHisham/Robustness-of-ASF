# K-Radar Object Class Distribution

Full-dataset histogram of `obj_class` values across `info_label_rev2/*.txt`, computed from all 58 sequences (34,994 label frames, 115,816 total object annotations). Verified: per-class counts sum exactly to the total line count, and `tracking_id` values are unique per frame regardless of `sensor_identify` tag (R/L/L1), so there is no per-sensor duplicate counting.

| Class | Instances | Share |
|---|---|---|
| Sedan | 89,340 | 77.1% |
| Bus or Truck | 18,401 | 15.9% |
| Pedestrian | 6,008 | 5.2% |
| Bicycle | 1,202 | 1.0% |
| Motorcycle | 628 | 0.5% |
| Pedestrian Group | 231 | 0.2% |
| Bicycle Group | 6 | <0.01% |

`Label` (a generic/fallback class listed in `configs/cfg_RTNH_wide.yml`'s label dict) has zero instances in the actual data — appears to be an unused config placeholder, not a real annotation category.

## Why only Sedan / Bus or Truck are trained on

`configs/cfg_RTNH_wide.yml` (and the K-Radar Model Zoo benchmark tables in `repos/K-Radar/docs/labeling.md`) only enable/report Sedan and "Bus or Truck" for RTNH detector training — together ~93% of all instances (107,741/115,816). The remaining classes are annotated but sparse: Pedestrian/Bicycle/Motorcycle are an order of magnitude rarer, and the Group variants (single box for a cluster of pedestrians/cyclists too close to separate) are vanishingly rare — 6 Bicycle Group instances across the entire dataset — too few to train a stable detector head on.

## Relevance to kradar_visibility

`kradar_visibility`'s parser (`test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/parser.py`) treats `obj_class` as an opaque passthrough string with no filtering — all 6 real classes (everything except `Label`) will appear in the visibility output if present in a frame's label file.
