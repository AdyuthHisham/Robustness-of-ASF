# Master metrics table -- ASF / K-Radar robustness sweep

22 rows: `original` + 21 severity-specific corrupted conditions (`frame_deletion` excluded -- crashed-run coverage artifact, see robustness-metrics-tables.md). mFR omitted (not implemented). Original mAP = 72.89 (verified clean baseline: 72.89 -- see /home/adhish/official_benchmakr_kradar.txt cross-check against the official eval_revised.py KITTI-eval tool; supersedes the earlier pre-frame-identifier-fix sweep's 69.27, see [[frame-identifier-bug]]).

| Condition | mAP | mATE | mASE | mAOE | RCE | mRR | Coverage (%) |
|---|---|---|---|---|---|---|---|
| original | 72.8934 | 0.3262 | 0.2362 | 0.2068 | -- | 1.00 (baseline) | 100.0000 |
| camera_gaussian_noise_low | 71.4798 | 0.3240 | 0.2438 | 0.2106 | 1.8598 | 0.9806 | 100.0000 |
| camera_gaussian_noise_medium | 71.3193 | 0.3264 | 0.2502 | 0.2153 | 2.0856 | 0.9784 | 100.0000 |
| camera_gaussian_noise_high | 71.1756 | 0.3267 | 0.2572 | 0.2148 | 2.2946 | 0.9764 | 100.0000 |
| camera_loss_partial_low | 71.4496 | 0.3257 | 0.2452 | 0.2135 | 1.9038 | 0.9802 | 100.0000 |
| camera_loss_partial_medium | 71.3829 | 0.3253 | 0.2457 | 0.2106 | 1.9952 | 0.9793 | 100.0000 |
| camera_loss_partial_high | 71.4634 | 0.3254 | 0.2438 | 0.2130 | 1.8759 | 0.9804 | 100.0000 |
| lidar_gaussian_noise_low | 68.3685 | 0.3480 | 0.2389 | 0.2055 | 6.2028 | 0.9379 | 100.0000 |
| lidar_gaussian_noise_medium | 23.7076 | 0.4848 | 0.2013 | 0.1606 | 66.7717 | 0.3252 | 100.0000 |
| lidar_gaussian_noise_high | 21.5616 | 0.4663 | 0.2010 | 0.1371 | 69.7661 | 0.2958 | 100.0000 |
| lidar_loss_partial_low | 72.9946 | 0.3265 | 0.2361 | 0.2105 | -0.1334 | 1.0014 | 100.0000 |
| lidar_loss_partial_medium | 73.0394 | 0.3277 | 0.2355 | 0.2115 | -0.1837 | 1.0020 | 100.0000 |
| lidar_loss_partial_high | 67.9041 | 0.3487 | 0.2364 | 0.2181 | 7.1175 | 0.9316 | 100.0000 |
| radar_gaussian_noise_low | 72.9815 | 0.3260 | 0.2352 | 0.2070 | -0.1306 | 1.0012 | 100.0000 |
| radar_gaussian_noise_medium | 61.7680 | 0.3296 | 0.2501 | 0.1933 | 15.2453 | 0.8474 | 100.0000 |
| radar_gaussian_noise_high | 54.0261 | 0.3288 | 0.2485 | 0.1820 | 25.9768 | 0.7412 | 100.0000 |
| radar_loss_partial_low | 72.9501 | 0.3254 | 0.2353 | 0.2081 | -0.0830 | 1.0008 | 100.0000 |
| radar_loss_partial_medium | 71.8110 | 0.3252 | 0.2354 | 0.2085 | 1.3819 | 0.9852 | 100.0000 |
| radar_loss_partial_high | 64.2950 | 0.3234 | 0.2490 | 0.2117 | 11.9699 | 0.8820 | 100.0000 |
| camera_loss_complete_zero | 71.4257 | 0.3227 | 0.2397 | 0.2169 | 1.9368 | 0.9799 | 100.0000 |
| lidar_loss_complete_zero | 42.1610 | 0.4353 | 0.2260 | 0.1772 | 42.2182 | 0.5784 | 100.0000 |
| radar_loss_complete_zero | 66.7787 | 0.3084 | 0.2423 | 0.2240 | 8.5143 | 0.9161 | 100.0000 |
