


# phase 2

## test series : normal

| `#`                       | 1                                                  | 2                | 3                | 4                           | 5            | 6        |
| ------------------------- | -------------------------------------------------- | ---------------- | ---------------- | --------------------------- | ------------ | -------- |
| dataset                   | KRadar                                             | KRadar           | KRadar           | nuScenes                    | nuScenes     | nuScenes |
| model                     | availability aware (KRadar)                        | BevFusion        | MV2D             | availability aware (KRadar) | BevFusion    | MV2D     |
| data-type                 | raw ?                                              |                  |                  |                             |              |          |
| d-camera                  | yes                                                | yes              | yes              | yes                         | yes          | yes      |
| d-lidar                   | yes                                                | yes              | yes              | yes                         | yes          | yes      |
| d-radar                   | yes                                                | yes              | yes              | yes                         | yes          | yes      |
| m-camera                  | yes                                                | yes              | yes              | yes                         | yes          | yes      |
| m-lidar                   | yes                                                | yes              | yes              | yes                         | yes          | yes      |
| m-radar                   | yes                                                | no               | no               | yes                         | no           | no       |
| required-data-adaptation  | no                                                 | 🔥yes (required) | 🔥yes (required) | 🔥yes (required)            | no           | no       |
| required-code-adaptation  | no                                                 | 🔥yes+++         | 🔥yes++          | 🔥yes++                     | no           | no       |
| required-model-retraining | no                                                 | no               | no               | no                          | no           | no       |
| status                    | ✅ deployed ✅ inference ✅ training ⌛ validation | pending          | pending          | pending                     | ⌛deployment | pending  |
| comment                   |                                                    |                  |                  |                             |              |          |

## test series : robust

| `#`                       | 1                           | 2              | 3              | 4                           | 5              | 6        |
| ------------------------- | --------------------------- | -------------- | -------------- | --------------------------- | -------------- | -------- |
| dataset                   | KRadar                      | KRadar         | KRadar         | nuScenes                    | nuScenes       | nuScenes |
| model                     | availability aware (KRadar) | BevFusion      | MV2D           | availability aware (KRadar) | BevFusion      | MV2D     |
| data-type                 | raw ?                       |                |                |                             |                |          |
| status                    | completed                   | in-progress    |                | pending                     |                |          |
| comment                   |                             |                |                |                             |                |          |
| d-camera                  |                             |                |                |                             |                |          |
| d-lidar                   |                             |                |                |                             |                |          |
| d-radar                   |                             |                |                |                             |                |          |
| m-camera                  |                             |                |                |                             |                |          |
| m-radar                   |                             |                |                |                             |                |          |
| m-lidar                   |                             |                |                |                             |                |          |
| required-data-adaptation  | no                          | yes (required) | yes (required) | yes (required)              | yes (required) | no       |
| required-code-adaptation  |                             |                |                |                             |                |          |
| required-model-retraining |                             |                |                |                             |                |          |


# phase 3


## test series : normal

| `#`                       |     |
| ------------------------- | --- |
| dataset                   |     |
| model                     |     |
| data-type                 |     |
| status                    |     |
| comment                   |     |
| d-camera                  |     |
| d-lidar                   |     |
| d-radar                   |     |
| m-camera                  |     |
| m-radar                   |     |
| m-lidar                   |     |
| required-data-adaptation  |     |
| required-code-adaptation  |     |
| required-model-retraining |     |

## test series : robust

| `#`                       |     |
| ------------------------- | --- |
| dataset                   |     |
| model                     |     |
| data-type                 |     |
| status                    |     |
| comment                   |     |
| d-camera                  |     |
| d-lidar                   |     |
| d-radar                   |     |
| m-camera                  |     |
| m-radar                   |     |
| m-lidar                   |     |
| required-data-adaptation  |     |
| required-code-adaptation  |     |
| required-model-retraining |     |
