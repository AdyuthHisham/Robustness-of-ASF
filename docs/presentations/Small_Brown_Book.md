# Battle Plan
1. Normal inference of the SF models
2. Generate robust test sets based on visibility analysis of the dataset
3. Add noises/corruptions to the data
4. Using robust tests frame sets perform inference using the SF model with and without the noises added to the data.
5. Evaluate the final results and generate metrics

# How the papers for noise were identified
1. Do they have code?
2. Which sensors do they talk about?
3. Novelties
4. Future work
5. List all noises and abnormalities they talk about
6. Categorize all noises and abnormalities into categories and make a unified table showing category, name and which paper talked about it, and how does the noise effect each sensor
7. How many noises did each paper cover?
8. A section on how to mitigate each noise.
9. An indepth description of what each noise is with theory
10. Which all SF models did the papers test on 
11. brief on the paper
12. Datasets used
13. Evaluate metrics used by each paper
14. Research questions they are answering
15. Why & how did they choose the noise
16. What type of noises di the paper not consider or was avoided
17. What are their test categories for robustness like occlusion, etc

# Idenitfied papers: /home/adhish/Productivity/AMSCUP/docs/lit_survey/noise_addition
NOTE: I havent used the whole name for these papers and I abbreviated most of them
1. MOI
No code
RQ: Can testing find erroneous predictions
Metrics: AP, IOU
Datasets: Berkeley deepdive, COCO
Models were random

2. LirTest
Code exists
RQ: Testing of Lidar using metamorphic relations(?) & can training with synthetic data help?
Metrics: mAP, Jacard
Dataset: Kitti
Model: Pointpillar, PV-RCNN, etc

3. Challenges, Advances ...
No code
Its a review paper
Metrics: mAP
Dataset: Random
Model: Yolo-v5

4. Are we ready for autonomous driving?
RQ: Benchmark suite, how do SFM work in realistic urban environment
Metrics: AP, orientation similarity, rotation/translation errors
Dataset: Kitti
Models: Random models

5. Generating realistic ..
RQ: Generation of diverse tests for lidar
Metrics: Accuracy, Jaccard metric, Voting based something
Dataset: SemanticKitti
Models: Random Models

Corruptions:
1. ADD_ROTATE
2. ADD_MIRROR_ROTATE
3. SCENE_REMOVE
4. SIGN_REPLACE
5. VEHICLE_INTENSITY
6. VEHICLE_DEFORM
7. VEHICLE_SCALE

6. Towards the robustness of multiple object tracking system
RQ: Evaluation robustness of MOT system and also uses temporary camera failure
Metrics: MOTA, ration of mapped frame pairs with errors
Dataset: Kitti tracking
Model: random models

Corruptions:
1. Frame deletion (deterministic)
2. Frame deletion ( random )
3. Frame duplicaton
4. Mosaic / Pixelation
5. Gaussian blur

7. Common corruption robustness ----
RQ: Benchmark for PCD detectors against 25 common corruption types
Metrics: CE, mCE, CR
Dataset: KITTI
Model: multiple models

8. Benchmarking robustnes of AI ---
RQ: 14 corruption patterns for checking robustness of MSF systems across tasks like obj det, tracking and depth completion
Metrics: Rb, mRb, AP, MOTA, RMSE
Model: Random models
Dataset: KITTI

Corruption are modified by inducing severity
Also this paper talks about robustness of early fusion and late fusion

Corruptions:
- Lidar:
Gaussian noise, rotation_x, impulse noise, rotation_y, loss partial, rotation_z, loss_complete, delay, rain and fog
- Camera:
Rain, fog, gaussian noise, impulse noise, brightness, darkness, distortion, motion blur, defocus blur, partial loss and complete loss
9. RCBevdet
RQ: BEV3D obj det using radar and camera
Metrics: NDS, mAP, mATE, mASE, mAOE, mAVE, MAAE
Dataset: nuScenes
Models: Random models
Randomly drop images or radar inputs to analyze robustness

10. 4D radar semantics ---
RQ: TMVA4D is designed and focued on evaluation seg performance in adverse field 
Metrics: DICE Coefficient, IOU, Precision, Recall
Dataset: TMV4AD novel multimodal dataset
Model: Radar model

11. Seeing through fog
RQ: Focuses on handling assymetric sensor corruptions through nearest entropy

12. Synthesizing and identify noise levels in autonomous vehicle camera - radar datasets

Corruptions:
- Camera:
blurring, additive noise, high/low exposure
- Radar:
Ghost point generation, RCS-ruled false negative, noise-induced shifts


## Types of Noise / Corruptions
1. Environmental / weather
2. Illumination
3. Geometric
4. Sensor
5. Motion
6. Synthetic

