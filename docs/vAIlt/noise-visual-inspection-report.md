# Noise Visual Inspection Report

## Frames Selected (non-consecutive)

| #   | Label         | Seq | RDR idx | LiDAR idx | Cam idx | Objects          | Scene   |
| --- | ------------- | --- | ------- | --------- | ------- | ---------------- | ------- |
| 1   | seq001_rdr033 | 1   | 33      | 1         | 2       | Sedan ~24m       | Highway |
| 2   | seq021_rdr015 | 21  | 15      | 11        | 34      | Sedans ~2-5m     | Urban   |
| 3   | seq048_rdr035 | 48  | 35      | 30        | 89      | Bus/Truck 14-58m | Mixed   |

## Effect Parameters

See `effect_parameters.yaml` for full details. Key choices:

- **Radar noise_induced_shifts**: shift_std=2.0m (Gaussian) — shifts each detection by ~2m RMS
- **Radar loss_partial**: fraction=0.5 — drops 50% of points
- **LiDAR gaussian_noise**: sigma_xy=0.5m — adds 0.5m std jitter to xy positions
- **LiDAR loss_partial**: fraction=0.5 — drops 50% of points
- **Camera gaussian_noise**: sigma=40 (pixel-value units, ~15% of 255 range)
- **Camera loss_partial**: fraction=0.3 — blacks out ~30% of image area

## Output

- Root: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/noise_visual_inspection`
- Index: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/noise_visual_inspection/index.html`
- Params: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/noise_visual_inspection/effect_parameters.yaml`
- Script: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/datasets/effects/visualize_effects.py`
- Report: `/home/adhish/Productivity/AMSCUP/docs/vAIlt/noise-visual-inspection-report.md`
