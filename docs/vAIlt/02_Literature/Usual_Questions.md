---
title: Usual Questions
type: literature
source: home/adhish/Productivity/AMSCUP/obsidianVault/Methodology - Automatic Multi-Sensor Calibration and Unified Perception.md
date: 2026-07-02
tags: [02 Literature]
---
# Usual Questions
1. What is a Voxel? A voxel (volume element) is the smallest indivisible unit in a 3D grid: it occupies a small cubic (or rectangular) volume in space and stores properties such as occupancy, density, or averaged point features.
2. What is MLP (Multi-Layer Perceptron)? Just a simple fully connected neural network.
3. ```markdown
   - **Queries** = **“Smart object proposals”** Each query is a vector that **represents one possible car** (or pedestrian, truck, etc.).
     It starts with:

    - An **estimated 3D position** (center of the object)
    - Some initial features (appearance from camera or geometry from LiDAR)
    - For camera queries only: a **depth uncertainty distribution** (not a single guess)

    So yes, queries are basically “I think there is a car here at this rough position — tell me more.”

- **Keys** = **“The raw evidence map from the sensor”** Keys are **not** positions of cars. Keys are small feature vectors taken from the **full feature map** produced by the backbone. They describe “what the camera/LiDAR actually saw at every location” (edges, colors, point density, etc.). Think of the keys as a huge library of tiny descriptions: “this pixel looks red and metallic”, “this voxel has high point density”, etc.
   ```
# Methods
**Assess few pipelines under same conditions with metrics**
1. [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#Hybrid and Self-Supervised Approaches]] sounds cool

2. ![[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#6.4. Toward Universal Fusion Foundation Models]]
3.
4. we also extract weather data recorded by the weather station closest to the global ego-position at the time of recording from Visual Crossing’s weather API [18]
5.
6. ![[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^5aff56]]

# Notes
1. For Lidar - Camera: Ego based methods sound more feasible for my requirements

# Metrics
From [[lyuCameraLiDARIMU2025]] - pg 18
```
Following the evaluation approach in [75], we also assessed the robustness of these algorithms from four perspectives: (A) Whether experiments tested the method on multiple dataset types or real-time data. Methods tested on two or more types received two stars (☆☆). (B) Whether tests included degenerate or challenging scenarios. If so, one star was awarded (☆). (C) Whether the range of initial errors in the test data was sufficiently large. If the initial average translation exceeded 50 mm or the initial average rotation exceeded 10◦, one star was awarded (☆). (D) Whether anti-noise testing was conducted. If so, one star was awarded (☆).
```


# Dataset
- Most probably need to setup streaming datasets
## Nuscenes
