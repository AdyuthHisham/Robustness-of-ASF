### SECTION 1: Paper Summaries

**1. Metamorphic Object Insertion for Testing Object Detection Systems**
*   **Authors:** Shuai Wang and Zhendong Su.
*   **Overview:** This paper introduces MetaOD, a metamorphic testing framework for object detectors (ODs). It synthesizes natural-looking images by extracting objects from one context and inserting them into new backgrounds. The metamorphic condition asserts that detection results for existing objects should remain consistent despite the insertion.
*   **Research Questions:** Can metamorphic testing effectively uncover erroneous predictions in black-box ODs? How does guided insertion compare to random insertion in finding defects?.
*   **Datasets Used:** Berkeley DeepDrive, COCO.
*   **Evaluation Metrics:** Average Precision (AP), Intersection over Union (IoU).
*   **Models Tested:** Amazon Rekognition, Google AutoML, Microsoft Azure, IBM Vision, SSD Mobilenet, SSD Inception, RCNN Resnet, RCNN Inception.

**2. LiRTest: Augmenting LiDAR Point Clouds for Automated Testing**
*   **Authors:** An Guo, Yang Feng, and Zhenyu Chen.
*   **Overview:** LiRTest is a tool for automated testing of LiDAR-based autonomous driving systems using metamorphic relations. It applies seven transformation operators—four affine (translation, rotation, scale, symmetry) and three weather-based (rain, snow, fog)—to seed point clouds.
*   **Research Questions:** Do transformations activate different neurons? How effective are these methods for detecting erroneous behaviors? Can retraining with synthetic data improve robustness?.
*   **Datasets Used:** KITTI.
*   **Evaluation Metrics:** Mean Average Precision (mAP), Jaccard distance for neuron coverage.
*   **Models Tested:** PointPillars, SECOND, Part-A2, PV-RCNN.

**3. Challenges, Advances and Future Prospects of Vehicle Detection in Snow**
*   **Authors:** Imran Reza, et al..
*   **Overview:** This is a narrative-thematic review of the challenges snow poses to vehicle detection. It examines the inter-relationship between snowflake morphology, visibility changes, and sensor degradation. It focuses on thermal imaging and sensor fusion as potential solutions.
*   **Research Questions:** Not explicitly listed as a primary research question; focuses on surveying existing literature.
*   **Datasets Used:** DAWN, NCLT, IUPUI, Boreas, ACDC, A2D2, Canadian Adverse Driving Conditions, BDD100K, RADIATE, IWADD.
*   **Evaluation Metrics:** mAP.
*   **Models Tested:** YOLO-v5.

**4. Are we ready for autonomous driving? The KITTI vision benchmark suite**
*   **Authors:** Andreas Geiger, Philip Lenz, and Raquel Urtasun.
*   **Overview:** This paper presents a benchmark suite for stereo, optical flow, visual odometry/SLAM, and 3D object detection. It provides high-resolution imagery and accurate ground truth captured from a real-world platform.
*   **Research Questions:** How do state-of-the-art algorithms perform in realistic, cluttered urban environments compared to laboratory settings?.
*   **Datasets Used:** KITTI (Original).
*   **Evaluation Metrics:** AP, orientation similarity, rotation/translation error, disparity/end-point error.
*   **Models Tested:** PCBP, ITGV, OCV-SGBM, ELAS, VISO2, various variational optical flow methods.

**5. Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems**
*   **Authors:** Garrett Christian, Trey Woodlief, and Sebastian Elbaum.
*   **Overview:** The authors propose a semantic mutation approach to generate diverse tests for LiDAR perception. It leverages real-world data to create "never-before-seen" scenarios (e.g., pedestrians in roadways) while preserving realism invariants.
*   **Research Questions:** How effective is the technique at uncovering severe failures? How realistic are the generated cases? How efficient is the generation process?.
*   **Datasets Used:** SemanticKITTI.
*   **Evaluation Metrics:** Accuracy, Jaccard metric, voting-based realism oracle.
*   **Models Tested:** Cylinder3D, SPVNAS, JS3C-Net, SalsaNext, SqueezeSegV3.

**6. Towards the Robustness of Multiple Object Tracking Systems**
*   **Authors:** Xiaoyuan Xie, et al..
*   **Overview:** This paper evaluates the robustness of Multiple Object Tracking (MOT) systems using metamorphic testing. It focuses on dynamic features like object speed variety and temporary camera failures (freeze, jamming, focus loss).
*   **Research Questions:** Can the proposed method detect violations in MOT systems? What are the specific details and types of detected violations? How do different systems compare?.
*   **Datasets Used:** KITTI tracking.
*   **Evaluation Metrics:** MOTA (implied by references), ratio of mapped frame pairs with errors.
*   **Models Tested:** SORT+YOLOv3, PointTrack, CenterTrack.

**7. K-Radar: 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions**
*   **Authors:** Dong-Hee Paek, Seung-Hyun Kong, and Kevin Tirta Wijaya.
*   **Overview:** Introduces K-Radar, a large-scale dataset providing 4D Radar Tensor (4DRT) data (Doppler, range, azimuth, elevation). It aims to demonstrate that 4D Radar is more robust than LiDAR in adverse weather like fog, rain, and snow.
*   **Research Questions:** Is height information crucial for 3D object detection in radar? How does 4D radar compare to LiDAR in robustness?.
*   **Datasets Used:** K-Radar.
*   **Evaluation Metrics:** AP (3D and BEV).
*   **Models Tested:** RTNH (Baseline NN), PointPillars.

**8. Common Corruption Robustness of Point Cloud Detectors: Benchmark and Enhancement**
*   **Authors:** Shuangzhi Li, et al..
*   **Overview:** The paper establishes a benchmark for point cloud detectors against 25 common corruption types (weather, noise, density, transformation). It uses physical-aware simulation to generate over 1.1 million examples.
*   **Research Questions:** How do corruptions affect performance? How does detector design affect robustness? What bugs are triggered? How effective are enhancement techniques?.
*   **Datasets Used:** KITTI (as a base for synthesis).
*   **Evaluation Metrics:** Corruption Error (CE), mean CE (mCE), Corruption Risk (CR).
*   **Models Tested:** SECOND, PointRCNN, PVRCNN, BtcDet, VoTr-SSD, VoTr-TSD, SE-SSD, Centerpoint.

**9. Benchmarking Robustness of AI-Enabled Multi-sensor Fusion Systems**
*   **Authors:** Xinyu Gao, et al..
*   **Overview:** This study investigates the robustness of Multi-Sensor Fusion (MSF) systems across tasks like object detection, tracking, and depth completion. It utilizes 14 corruption patterns (weather, sensor noise, misalignment) to evaluate tightly-coupled AI systems.
*   **Research Questions:** How do MSF systems perform against corrupted signals? How sensitive are they to sensor misalignment? To what extent are components coupled? Can fusion mechanisms be repaired?.
*   **Datasets Used:** KITTI (base for KITTI-C).
*   **Evaluation Metrics:** Robustness score (Rb), mean Rb (mRb), task-specific metrics (AP, MOTA, RMSE).
*   **Models Tested:** EPNet, FConv, CLOCs, JMODT, DFMOT, TWISE, MDANet.

**10. RCBEVDet: Radar-Camera Fusion (BEV)**
*   **Authors:** (Short Title: RCBEVDet).
*   **Overview:** This paper focuses on multi-view 3D object detection using radar and camera fusion in Bird’s-Eye View (BEV). It proposes an RCS-aware scattering encoder to address radar noise and a cross-attention fusion module.
*   **Research Questions:** Not explicitly stated as formal questions; focuses on improving radar-camera fusion.
*   **Datasets Used:** nuScenes.
*   **Evaluation Metrics:** NDS, mAP, mATE, mASE, mAOE, mAVE, mAAE.
*   **Models Tested:** RCBEVDet, CenterFusion, CRAFT, RCBEV4d, CRN, BEVDet, BEVDepth, SOLOFusion, StreamPETR.

**11. 4D Radar Semantic Segmentation of People in Field Conditions**
*   **Authors:** Mikael Skog, et al..
*   **Overview:** Proposes TMVA4D, a family of neural network architectures for semantic segmentation of people using 4D radar point clouds. It uses temporal multi-view networks to distinguish people from background in low-visibility field conditions like dust and smoke.
*   **Research Questions:** Not explicitly stated; focuses on evaluating segmentation performance in adverse field conditions.
*   **Datasets Used:** TMVA4D novel multimodal dataset (radar/thermal).
*   **Evaluation Metrics:** Dice coefficient, IoU, Precision, Recall.
*   **Models Tested:** TMVA4D-CNN, TMVA4D-IntConvLSTM, TMVA-Net.

**12. 4D mmWave Radar in Adverse Environments for Autonomous Driving: A Survey**
*   **Authors:** Xiangyuan Peng, et al..
*   **Overview:** A comprehensive survey reviewing 4D mmWave radar research in adverse environments. It analyzes datasets, methodologies (single-modal and multimodal), and applications like perception and SLAM.
*   **Research Questions:** Not applicable (Survey).
*   **Datasets Used:** Surveys various: TJ4DRadSet, K-Radar, Dual Radar, Bosch Street, WaterScenes, etc..
*   **Evaluation Metrics:** Not applicable.
*   **Models Tested:** Surveys various: RadarOcc, TMVA4D, RTNH+, L4DR, RIDERS.

**13. Seeing Through Fog Without Seeing Fog: Deep Multimodal Sensor Fusion**
*   **Authors:** Mario Bijelic, et al..
*   **Overview:** Presents a deep fusion network for object detection that generalizes to adverse weather without needing a massive corpus of labeled adverse data. It introduces a novel multimodal dataset acquired over 10,000 km.
*   **Research Questions:** Not explicitly listed; focuses on handling asymmetric sensor corruptions through measurement entropy.
*   **Datasets Used:** Seeing Through Fog (STF) novel dataset.
*   **Evaluation Metrics:** AP.
*   **Models Tested:** Deep Entropy Fusion, AVOD-FPN, Frustum PointNets, Fusion SSD, Concat SSD.

---

### SECTION 2: Code & Repositories

| Paper Title | Link |
| :--- | :--- |
| Metamorphic Object Insertion... | [github.com/MetaOD/MetaOD](https://github.com/MetaOD/MetaOD) |
| LiRTest: Augmenting LiDAR... | [github.com/open-mmlab/OpenPCDet](https://github.com/open-mmlab/OpenPCDet) (and tool-specific code released) |
| Generating Realistic and Diverse... | [github.com/less-lab-uva/semLidarFuzz](https://github.com/less-lab-uva/semLidarFuzz) |
| Towards the Robustness of MOT... | [github.com/duaaany/ISSRE22-MT4MOT](https://github.com/duaaany/ISSRE22-MT4MOT) |
| K-Radar: 4D Radar Object Detection... | [github.com/kaist-avelab/k-radar](https://github.com/kaist-avelab/k-radar) |
| Common Corruption Robustness... | [sites.google.com/ualberta.ca/robustness1pc2detector/](https://sites.google.com/ualberta.ca/robustness1pc2detector/) |
| Benchmarking Robustness of MSF... | [sites.google.com/view/ai-msf-benchmark](https://sites.google.com/view/ai-msf-benchmark) |
| 4D Radar Semantic Segmentation... | Publicly available upon publication (implied) |
| Seeing Through Fog... | [github.com/princeton-computational-imaging/SeeingThroughFog](https://github.com/princeton-computational-imaging/SeeingThroughFog) |

---

### SECTION 3: Sensors Discussed

*   **RGB Camera:** MetaOD, Snow review, KITTI, MOT Robustness, K-Radar, MSF systems, RCBEVDet, 4D Radar survey, Seeing Through Fog.
*   **LiDAR:** LiRTest, Snow review, KITTI, Semantic mutations, MOT (implied context), K-Radar, PC corruption benchmark, MSF systems, 4D Radar survey, Seeing Through Fog.
*   **Standard Radar (3D):** Snow review, Seeing Through Fog.
*   **4D mmWave Radar:** K-Radar, RCBEVDet, People segmentation, 4D Radar survey.
*   **Gated NIR (Near-Infrared) Camera:** Snow review, Seeing Through Fog.
*   **FIR (Far-Infrared) / Thermal Camera:** Snow review, People segmentation, 4D Radar survey, Seeing Through Fog.
*   **GPS/IMU:** LiRTest, Snow review, KITTI, K-Radar, 4D Radar survey.
*   **Ultrasonic:** Snow review (as background reference).

---

### SECTION 4: Novelties

*   **MetaOD:** First metamorphic testing approach specifically for ODs, treating them as black-boxes.
*   **LiRTest:** First systematic and automated testing tool for LiDAR-based vehicles using weather-specific physics models.
*   **Snow Review:** Snow-specific synthesis integrating snowflake morphology with detection visibility and intensity.
*   **KITTI:** First large-scale benchmark with realistic non-synthetic imagery and accurate ground truth for stereo and flow.
*   **Semantic Mutations:** First semantic mutation testing for LiDAR-based perception using realism invariants.
*   **MOT Robustness:** First method to efficiently test MOT robustness using dynamic features like speed variety and camera failure.
*   **K-Radar:** First large-scale object detection dataset featuring 4D Radar tensor data with height information.
*   **PC Corruption Benchmark:** First robustness benchmark for point cloud detection covering 25 physical-aware corruptions.
*   **MSF Robustness:** First public benchmark evaluating MSF systems' robustness against corrupted signals and misalignment.
*   **RCBEVDet:** Introduction of RCS-aware scattering encoder to handle radar noise in Bird's Eye View.
*   **TMVA4D:** First study of semantic segmentation of people in 4D radar heatmaps under adverse field conditions (dust/smoke).
*   **4D Radar Survey:** First survey specifically focusing on 4D mmWave radar datasets and methods for adverse environments.
*   **Seeing Through Fog:** Adaptive single-shot deep fusion architecture steered by measurement entropy to generalize without adverse training data.

---

### SECTION 5: Future Work

*   **MetaOD:** Developing semantic understanding to make inserted objects more natural; exploring human gesture mutation in specific scenes.
*   **LiRTest:** Exploring impacts of other factors like electromagnetic waves; fine-tuning parameters based on real-world back-scattering data.
*   **Snow Review:** Improving integration of contextual information; exploring weakly supervised/unsupervised learning for limited data.
*   **KITTI:** Gradually increasing benchmark difficulty; including visual SLAM, loop-closure, and SFM into the framework.
*   **Semantic Mutations:** Exploring feedback-driven parameter selection; generating mixed-input mutations across multiple sensors simultaneously.
*   **MOT Robustness:** Designing MRs for new scenarios; testing more MOT systems with larger datasets.
*   **K-Radar:** Using 4DRT for tracking, SLAM, and other perception tasks beyond 3D object detection.
*   **PC Corruption Benchmark:** Calls for more research on robustness enhancement techniques based on findings.
*   **MSF Robustness:** Fine-grained robustness evaluation for systems beyond perception; formal analysis and repair of MSF systems.
*   **RCBEVDet:** Not explicitly detailed in the provided excerpt (focuses on ablation results).
*   **TMVA4D:** Deployment in live systems and further field robotics applications.
*   **4D Radar Survey:** Addressing noise/sparsity handling; exploring new tasks and scenes (e.g., waterways).
*   **Seeing Through Fog:** Developing end-to-end models for failure detection and adaptive sensor control (e.g., noise/power level control).

---

### SECTION 6: Noises & Abnormalities — Unified Catalog

| Category | Noise/Abnormality Name | Paper(s) | Affected Sensor(s) | Effect on Sensor / Description |
| :--- | :--- | :--- | :--- | :--- |
| **Environmental / Weather** | Rain | | Camera, LiDAR, Radar | Pixel attenuation/streaks in cameras; laser scattering/absorption in LiDAR; attenuation/backscatter in radar. |
| | Snow | | Camera, LiDAR, Radar | Reduced visibility and illumination variation; geometric obstructions in LiDAR; information shift. |
| | Fog | | Camera, LiDAR | Distance-dependent loss in contrast/color; false reflections by droplets. Radar is mostly unaffected. |
| | Sleet | | LiDAR | Lost measurements for objects ahead during driving. |
| | Dust / Smoke | | Camera, LiDAR | Drastic reduction in visibility; makes people undetectable by color/thermal cameras and LiDAR. |
| **Photometric / Illumination** | Darkness / Low-light | | Camera | Passive RGB camera degenerates with decreasing light. |
| | Brightness / Glare | | Camera | Adjustments to pixel values; affects signal-to-noise ratio. |
| **Geometric / Structural** | Occlusion | | All Sensors | Blocks visibility; creates blind spots; triggers recognition failure. |
| | Misalignment (Spatial) | | MSF (Cam/LiDAR) | Deviations due to vibration or thermal fluctuations. |
| | Misalignment (Temporal) | | MSF (Cam/LiDAR) | Signal delay causing synchronization errors. |
| **Sensor / Hardware** | Gaussian Noise | | Camera, LiDAR | Variance in ranging/coordinates. |
| | Impulse Noise | | Camera, LiDAR | Deterministic perturbations to subsets of points/pixels. |
| | Video Freeze | | Camera | Occasional temporary loss of video updates. |
| | Signal Jamming | | Camera | Occasional signal disturbance leading to pixelated frames. |
| | Focus Loss | | Camera | Blurring caused by camera being out of focus. |
| | Motion Blur | | Camera | Blurring caused by camera shaking or moving quickly. |
| | Distortion | | Camera | Optical aberrations from lens design. |
| | Beam/Layer Deletion | | LiDAR | Malfunction of rotary lasers losing entire layers of data. |
| **Dynamic / Motion** | Speed Variety | | MOT System | Objects moving at different speeds (high/low) affect trajectory formulation. |
| **Adversarial / Synthetic** | Object Insertion | | Camera, LiDAR | Synthetic objects (e.g., car, sign) added to background. |
| | Object Relocation | | Camera | Moving objects toward background centroids. |
| | Semantic Mutations | | LiDAR | Mirroring, rotating, deforming, or scaling entities. |

---

### SECTION 7: Noise Coverage Per Paper

*   **MetaOD:** 2 (Random insertion, Guided insertion).
*   **LiRTest:** 7 (Translation, Rotation, Scale, Symmetry, Rain, Snow, Fog).
*   **Snow Review:** Not quantified; covers general snow-related degradations.
*   **KITTI:** 4+ (Illumination conditions, large displacements/high speed, non-lambertian surfaces, disparity shadows/occlusion).
*   **Semantic Mutations:** 7 (Add, Remove, Rotate, Mirror, Adjust Intensity, Deform, Scale, Swap).
*   **MOT Robustness:** 5 (Speed stability, Speed waves, Video freeze, Signal jamming, Focus loss).
*   **K-Radar:** 4 (Fog, Rain, Sleet, Snow).
*   **PC Corruption Benchmark:** 25 (Rain, Snow, Fog, Uniform_rad, Gaussian_rad, Impulse_rad, Upsample, Background, Cutout, Beam_del, Layer_del, etc.).
*   **MSF Robustness:** 14 (Rain, Fog, Brightness, Darkness, Distortion, Motion Blur, Defocus Blur, Gaussian Noise (C/L), Impulse Noise (C/L), Spatial/Temporal Misalignment).
*   **RCBEVDet:** 1 (Radar noise/clutter via RCS scattering).
*   **TMVA4D:** 3 (Dust, Water spray, Smoke).
*   **4D Radar Survey:** 10+ (Fog, Rain, Sleet, Snow, Gloom, Smoke, Night, Glare, Low-light).
*   **Seeing Through Fog:** 3 (Heavy fog, Heavy snow, Severe rain).

---

### SECTION 8: Noise Mitigation Strategies

| Noise/Abnormality | Mitigation Strategy | Paper(s) |
| :--- | :--- | :--- |
| **Snow/Rain** | Retraining with synthetic weather-corrupted data. | LiRTest |
| **Snow** | Sensor fusion (e.g., thermal imaging) and optimal filtering. | Snow review |
| **Radar Noise** | RCS-aware scattering encoder to model radar noise in BEV. | RCBEVDet |
| **Common Corruptions** | Data augmentation (Part-Aware DA) and denoising (KNN-based filtering). | PC Benchmark |
| **MSF Coupling Bugs** | Enhancing fusion mechanisms (e.g., additional guidance branch). | MSF Robustness |
| **Asymmetric Distortion** | Adaptive single-shot deep fusion architecture steered by measurement entropy. | Seeing Through Fog |
| **Fog/Smoke/Dust** | Temporal Multi-View Networks (ConvLSTM/CNN) using 4D radar. | TMVA4D |
| **Occlusion** | Occupancy estimator for estimating occluded regions. | PC Benchmark |
| **Recognition failures** | Not addressed (focuses on exposing defects). | MetaOD |

---

### SECTION 9: In-Depth Noise Descriptions

*   **Fog Physical Model:** Modeled as a cylinder in 3D space ($x^2 + y^2 = R^2$) where density correlates with concentration. Visibility is calculated using Koschmieder's law. Fog causes distance-dependent contrast loss in intensity images.
*   **Radar RCS-aware Scattering:** Uses the Radar Cross Section (RCS) values to determine a scattering radius ($r$) for radar point features: $r = (c_x^2 + c_y^2) \times V_{RCS}$. This addresses the noise inherent in radar returns by modeling the spatial distribution of power.
*   **LiDAR Weather Equation:** Uses a simplified LiDAR equation $P_r(z) = \frac{C_s \beta}{z^2} e^{-2\alpha z}$ where $\alpha$ is the extinction coefficient representing the scattering and absorption of light by raindrops or fog.
*   **Measurement Entropy:** Local measurement entropy ($\rho$) is used to steer fusion: $\rho = \sum P_{mn}^i \log(P_{mn}^i)$. It measures the reliability of each sensor patch to determine how much information should be extracted from that modality.
*   **Speed-up Simulation:** Since a video is a series of images at a fixed rate, an object going equal distance at faster speed is captured in fewer frames. MR1-1 removes every $k$-th frame to simulate a stable $2x$ speedup.

---

### SECTION 10: Noise Selection Rationale

*   **LiRTest:** Chose affine and weather transformations to mimic realistic driving phenomena and sensor sensitivity to environmental conditions.
*   **MOT Robustness:** Selected speed variety and camera failure because existing metamorphic relations mostly focus on static features; dynamic features are exclusive and critical to video-based MOT.
*   **PC Corruption Benchmark:** Chose 25 corruptions based on physical imaging principles (e.g., flawed sensors, weather-induced false reflections) to build a comprehensive robustness evaluation.
*   **MSF Robustness:** Selected patterns based on operational environment changes (external weather) and sensor-internal changes (transmission noise) to investigate "tightly-coupled" system failures.
*   **Seeing Through Fog:** Chose rare "edge-case" weather (thick fog, etc.) because they are statistically infrequent (e.g., thick fog 0.01% of the time) but safety-critical.

---

### SECTION 11: Omissions & Avoided Noises

*   **MetaOD:** Specifically avoided transformation rules like rotation or blurring on inserted objects to "preserve realism at our best effort".
*   **MetaOD:** Avoided extreme cases that "stress ODs" (like extreme contrast tweaks) to maintain a conservative test oracle.
*   **LiRTest:** Did not cover all possible factors, such as electromagnetic wave interference, leaving them for future work.
*   **MOT Robustness:** Avoided scenarios involving deliberate artificial noise (adversarial examples) to focus on common real-life robustness issues.
*   **MSF Robustness:** Omitted artifacts for LiDAR sensors (e.g., broken beams), focusing only on camera artifacts for the initial benchmark.
*   **4D Radar Survey:** Notes that fog and smoke have minimal Rayleigh scattering on mmWaves and thus have less pronounced impact than rain/snow.

---

### SECTION 12: Robustness Test Categories

*   **Metamorphic Relations (MRs):** Testing framework where the relationship between original and transformed inputs/outputs is defined (e.g., equality criteria).
*   **Neuron Coverage:** A metric used to capture input-output diversity and trigger internal DNN logic.
*   **Common Corruption Benchmark:** Groups tests into representations (voxel vs. point) and proposal architectures (one-stage vs. two-stage).
*   **Coupling/Signal Loss:** A framework for evaluating MSF systems by simulating partial or complete loss (10%-100%) of signal branches to test system resilience.
*   **Scene-level vs. Object-level:** Taxonomy for point cloud corruptions categorized by whether they affect the entire scene (weather) or individual objects (transformations).
*   **Field Robotics Conditions:** Framework for evaluating human detection using visibility reduced by airborne particles (dust, water spray, smoke) in specific industries (mining, construction).

---
