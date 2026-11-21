# Master metrics table -- ASF / K-Radar robustness sweep

22 rows: `original` + 21 severity-specific corrupted conditions (`frame_deletion` excluded -- crashed-run coverage artifact, see robustness-metrics-tables.md). mFR omitted (not implemented). mAP is the aggregated mAP (num_gt-weighted over both classes and all stratum cells, from `crossproduct_v2/summary_full_density.parquet`): original = 73.99. It is not the mean of the two per-class APs (72.89). RCE is still computed per class.

| Condition | mAP | mATE | mASE | mAOE | RCE | mRR | Coverage (%) |
|---|---|---|---|---|---|---|---|
| original | 73.9866 | 0.3262 | 0.2362 | 0.2068 | -- | 1.00 (baseline) | 100.0000 |
| camera_gaussian_noise_low | 73.2167 | 0.3240 | 0.2438 | 0.2106 | 1.8598 | 0.9896 | 100.0000 |
| camera_gaussian_noise_medium | 72.8623 | 0.3264 | 0.2502 | 0.2153 | 2.0856 | 0.9848 | 100.0000 |
| camera_gaussian_noise_high | 72.6381 | 0.3267 | 0.2572 | 0.2148 | 2.2946 | 0.9818 | 100.0000 |
| camera_loss_partial_low | 73.3539 | 0.3257 | 0.2452 | 0.2135 | 1.9038 | 0.9914 | 100.0000 |
| camera_loss_partial_medium | 72.9326 | 0.3253 | 0.2457 | 0.2106 | 1.9952 | 0.9858 | 100.0000 |
| camera_loss_partial_high | 72.9187 | 0.3254 | 0.2438 | 0.2130 | 1.8759 | 0.9856 | 100.0000 |
| lidar_gaussian_noise_low | 69.5920 | 0.3480 | 0.2389 | 0.2055 | 6.2028 | 0.9406 | 100.0000 |
| lidar_gaussian_noise_medium | 18.5413 | 0.4848 | 0.2013 | 0.1606 | 66.7717 | 0.2506 | 100.0000 |
| lidar_gaussian_noise_high | 17.4531 | 0.4663 | 0.2010 | 0.1371 | 69.7661 | 0.2359 | 100.0000 |
| lidar_loss_partial_low | 74.7381 | 0.3265 | 0.2361 | 0.2105 | -0.1334 | 1.0102 | 100.0000 |
| lidar_loss_partial_medium | 75.2183 | 0.3277 | 0.2355 | 0.2115 | -0.1837 | 1.0166 | 100.0000 |
| lidar_loss_partial_high | 70.9677 | 0.3487 | 0.2364 | 0.2181 | 7.1175 | 0.9592 | 100.0000 |
| radar_gaussian_noise_low | 74.2095 | 0.3260 | 0.2352 | 0.2070 | -0.1306 | 1.0030 | 100.0000 |
| radar_gaussian_noise_medium | 62.9412 | 0.3296 | 0.2501 | 0.1933 | 15.2453 | 0.8507 | 100.0000 |
| radar_gaussian_noise_high | 57.1844 | 0.3288 | 0.2485 | 0.1820 | 25.9768 | 0.7729 | 100.0000 |
| radar_loss_partial_low | 74.0289 | 0.3254 | 0.2353 | 0.2081 | -0.0830 | 1.0006 | 100.0000 |
| radar_loss_partial_medium | 73.2062 | 0.3252 | 0.2354 | 0.2085 | 1.3819 | 0.9895 | 100.0000 |
| radar_loss_partial_high | 67.4771 | 0.3234 | 0.2490 | 0.2117 | 11.9699 | 0.9120 | 100.0000 |
| camera_loss_complete_zero | 72.6563 | 0.3227 | 0.2397 | 0.2169 | 1.9368 | 0.9820 | 100.0000 |
| lidar_loss_complete_zero | 44.0472 | 0.4353 | 0.2260 | 0.1772 | 42.2182 | 0.5953 | 100.0000 |
| radar_loss_complete_zero | 69.3572 | 0.3084 | 0.2423 | 0.2240 | 8.5143 | 0.9374 | 100.0000 |
