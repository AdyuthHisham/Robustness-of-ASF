## Dependency Graph
```
pipeline.py
├── lidar_visibility.py
├── radar_visibility.py
└── camera_visibility.py
```

## Upgrade Order (respecting dependencies)
1. lidar_visibility.py - Can be updated independently; adds support for precomputed LiDAR range image (backward compatible).
2. radar_velocity.py - Independent; adds support for precomputed radar noise-floor map (backward compatible).
3. camera_visibility.py - Independent; adds support for precomputed depth map and distortion correction (backward compatible).
4. pipeline.py - Depends on all three sensor modules; updates to pass precomputed data and add ghost flag.