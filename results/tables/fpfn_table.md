# FP / FN table -- ASF / K-Radar robustness sweep

22 rows: `original` + 21 severity-specific corrupted conditions (`frame_deletion` excluded -- crashed-run coverage artifact, see robustness-metrics-tables.md). FP rate = FP/(FP+TP) (1-precision). FN rate = FN/(FN+TP) (miss rate). Rows marked `*` have N < 2000 (FP+FN+TP for that condition) -- treat their rates as noisier than the rest.

| Condition | N | FP | FN | TP | FP rate | FN rate |
|---|---|---|---|---|---|---|
| original | 40355 | 4900 | 8286 | 27169 | 0.1528 | 0.2337 |
| camera_gaussian_noise_low | 40286 | 4831 | 8566 | 26889 | 0.1523 | 0.2416 |
| camera_gaussian_noise_medium | 40360 | 4905 | 8683 | 26772 | 0.1548 | 0.2449 |
| camera_gaussian_noise_high | 40407 | 4952 | 8792 | 26663 | 0.1566 | 0.2480 |
| camera_loss_partial_low | 40327 | 4872 | 8546 | 26909 | 0.1533 | 0.2410 |
| camera_loss_partial_medium | 40375 | 4920 | 8660 | 26795 | 0.1551 | 0.2443 |
| camera_loss_partial_high | 40533 | 5078 | 8632 | 26823 | 0.1592 | 0.2435 |
| lidar_gaussian_noise_low | 39926 | 4471 | 9959 | 25496 | 0.1492 | 0.2809 |
| lidar_gaussian_noise_medium | 36630 | 1175 | 29213 | 6242 | 0.1584 | 0.8239 |
| lidar_gaussian_noise_high | 36297 | 842 | 29828 | 5627 | 0.1302 | 0.8413 |
| lidar_loss_partial_low | 40263 | 4808 | 7975 | 27480 | 0.1489 | 0.2249 |
| lidar_loss_partial_medium | 40004 | 4549 | 7835 | 27620 | 0.1414 | 0.2210 |
| lidar_loss_partial_high | 39878 | 4423 | 9431 | 26024 | 0.1453 | 0.2660 |
| radar_gaussian_noise_low | 40339 | 4884 | 8288 | 27167 | 0.1524 | 0.2338 |
| radar_gaussian_noise_medium | 39286 | 3831 | 12514 | 22941 | 0.1431 | 0.3530 |
| radar_gaussian_noise_high | 37863 | 2408 | 14699 | 20756 | 0.1040 | 0.4146 |
| radar_loss_partial_low | 40264 | 4809 | 8291 | 27164 | 0.1504 | 0.2338 |
| radar_loss_partial_medium | 40016 | 4561 | 8559 | 26896 | 0.1450 | 0.2414 |
| radar_loss_partial_high | 39536 | 4081 | 10767 | 24688 | 0.1419 | 0.3037 |
| camera_loss_complete_zero | 40255 | 4800 | 8824 | 26631 | 0.1527 | 0.2489 |
| lidar_loss_complete_zero | 39235 | 3780 | 19214 | 16241 | 0.1888 | 0.5419 |
| radar_loss_complete_zero | 40278 | 4823 | 9992 | 25463 | 0.1592 | 0.2818 |
