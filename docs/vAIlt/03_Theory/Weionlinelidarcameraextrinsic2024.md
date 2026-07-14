---
title: Weionlinelidarcameraextrinsic2024
type: literature
source: home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/weiOnlineLiDARcameraExtrinsic2024.md
date: 2026-07-02
tags: [03 Theory]
---
TLDR:  
Converts LiDAR to Camera data and compares with actual camera data to see how similar they are. If calibration is needed it uses a ML model to spit out new optimal matrices.

Gemini **TL;DR** The paper proposes an online algorithm to detect and correct misalignments between LiDAR and camera sensors on autonomous vehicles caused by driving vibrations. The methodology works by projecting 3D LiDAR point clouds onto 2D camera planes to create depth images, effectively converting the alignment challenge into a 2D-2D comparison task. A self-checking module then analyzes these inputs using a two-stream neural network—incorporating a **patch-wise transformer** to enhance RGB features and a **pixel-wise matching mask** to handle sparse depth data—to verify if the sensors are synchronized. If misalignment is detected, the system reroutes the data to a recalibration module that iteratively regresses the correct extrinsic parameters over five stages to repair the offset before re-verifying the alignment.