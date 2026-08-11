# Noise Taxonomy

The corruption effects actually selected for implementation in the robust test-set pipeline, per modality, each traced to the paper it's drawn from. This is the **design-level selection** — see [[03_Theory/Sensor_Noise_and_Degradation_Models|Sensor Noise and Degradation Models]] for the broader literature this was narrowed down from.

## New corruptions implemented (per modality)

| Modality | Effect | Source paper |
|---|---|---|
| LiDAR | Frame Deletion (deterministic + random) | *Towards the Robustness of Multiple Object Tracking Systems* |
| LiDAR | Gaussian Noise | *Benchmarking Robustness of AI-Enabled...* |
| LiDAR | Loss Partial | *Benchmarking Robustness of AI-Enabled...* |
| Camera | Frame Deletion (deterministic + random) | *Towards the Robustness of Multiple Object Tracking Systems* |
| Camera | Gaussian Noise | *Benchmarking Robustness of AI-Enabled...* |
| Camera | Loss Partial | *Benchmarking Robustness of AI-Enabled...* |
| Radar | Frame Deletion (deterministic + random) | *Towards the Robustness of Multiple Object Tracking Systems* |
| Radar | Noise-Induced Shifts (replaces Gaussian noise — radar corruption is a per-point coordinate shift, not additive intensity noise) | *Synthesizing and Identifying Noise Levels in Autonomous Vehicle Camera-Radar Datasets* |
| Radar | Loss Partial | *Benchmarking Robustness of AI-Enabled...* |

`loss_complete` exists as a rendered effect (see [[06_Results/Noise_Visual_Inspection]]) but is **not** implemented as a separate corruption path — frame deletion already produces the same effective condition, so a dedicated "loss complete" generator was judged redundant.

## Corruptions already available in K-Radar (not built by this project)

| Modality | Effect | Description |
|---|---|---|
| Camera | Crack | Overlay crack texture on image |
| Camera | Light scratch | Overlay light scratch texture |
| Camera | Severe scratch | Overlay severe scratch texture |
| LiDAR | Missed | Remove points in an angular range (FOV occlusion simulation) |

## Realized parameters (v2 single-level / v3 severity ladder)

See [[06_Results/Noise_Visual_Inspection]] for the full per-effect parameter table with actual σ/probability values used in the rendered gallery (`effect_parameters.yaml`, `severity_parameters.yaml`, global `seed: 42`).

## Open questions logged during design (unresolved as of last working note, 2026-08-10)

- Exact semantics of `loss_partial` across radar/LiDAR/camera were not fully pinned down before implementation — see [[06_Results]] zero-out diagnostic for the resolution (zeroed rows collapse to `(0,0,0)` rather than being removed, which is why a dedicated zero-out BEV renderer was needed).
- Noise injection historically was not applied to OS1-128 or the side cameras — scope was narrowed to `rdr_sparse` (radar), `ldr_64` (LiDAR), and `cam_front`/`cam_dir.cropped` (camera) to match what K-Radar's own inference path actually consumes (noted 2026-07-29).
- Planned but not yet in the schema: object-density feature (objects identified per frame per sensor), and full `description.txt` environment fields (Environment / Time of Day / Weather — currently only weather is captured; Environment and Time of Day are not yet columns).
- Planned metric: quantify bounding-box deviation between clean and corrupted inference per annotation (not yet implemented as of this note).

## Source

- `docs/Black_Book.md` (69 L, canonical — corruption taxonomy + running working notes, dated 29/July and 10/August 2026)
