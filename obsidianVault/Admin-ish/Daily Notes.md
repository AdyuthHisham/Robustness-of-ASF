# tasks

### phase 1

- [x] #task/lit_survey Models ➕ 2026-04-02 ✅ 2026-04-07
- [x] #task/lit_survey Datasets ➕ 2026-04-02 ✅ 2026-04-07

### phase 2

- [x] #task Setup Repo and Workspace ➕ 2026-04-02 ✅ 2026-04-07
- [ ] #task Deploy Model: BevFusion ⏫ ➕ 2026-04-02 📅 2026-04-17
- [ ] #task Deploy Model: AwailAware ⏫ ➕ 2026-04-02 📅 2026-04-17
- [x] #task Deploy Model: MV2D ⏫ ➕ 2026-04-02 📅 2026-04-22 ✅ 2026-05-05
- [x] #task Setup KRADAR 🔺 ➕ 2026-04-02 📅 2026-04-15 ✅ 2026-05-05
- [ ] #task Cross compatability: KRADAR and Nuscenes ⏫ ➕ 2026-04-02 📅 2026-04-24
- [x] #task Setup NuScenes 🔺 ➕ 2026-04-02 📅 2026-04-15 ✅ 2026-04-23
- [ ] #task Visualize BEV ⏫ ➕ 2026-04-02 📅 2026-04-22
- [ ] #task Weather Resistant Metrics ➕ 2026-04-02 📅 2026-04-24
- [ ] #task Data Analysis: Descriptions ⏫ ➕ 2026-04-07 📅 2026-04-17
- [ ] #task Data Analysis: Sensors ⏫ ➕ 2026-04-07 📅 2026-04-15
- [ ] #task Compile Metrics ⏫ ➕ 2026-04-07 📅 2026-04-29
- [ ] #task Raw data quality metric ⏫ ➕ 2026-04-07 📅 2026-04-22
- [ ] #task Robust testing (Different Sensors and stuff) 🔺 ➕ 2026-04-07 📅 2026-05-01

### phase 3

- [ ] #task Analyze results 🔺 ➕ 2026-04-07 📅 2026-05-06
- [ ] #task Develop new robust SF➕ 2026-04-02

# Week 1
## Jan 29
- Thesis Proposal: Success
- Admin-ish: Set up repo and zotero and obsidian, also dicked around with Emacs (but not ready yet)
- Literature Survey
	- Set up a system for efficient note taking (need to be validated)
	- Got a goldmine of a paper [[liAutomaticTargetlessLiDAR2023]]
		- **Need to finish and continue reading from Ego Motion techniques**
	- Skimmed through [[weiOnlineLiDARcameraExtrinsic2024|ML Camera Lidar auto calib paper]]|

# Week 2
## Feb 02
- Need to write a mini section on the four types for better clarity
- Identified Radar based papers for further investigation
- Finished reading [[liAutomaticTargetlessLiDAR2023]]
## Feb 03
- Found good number of papers to read
- Keeping on reading
## Feb 04
- Slowly read papers

## Feb 05
- Installed UV, Marimo (Jupyter notebook replacement), need to try out Polars (Pandas replacement)

## Feb 06
- Not much progress

# Week 3
## Feb 09
- Making notes of calibration based review papers
## Feb 10
- Nothing of note
## Feb 11
- Focusing on fusion based review papers
- [ ] [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#Hybrid and Self-Supervised Approaches]] looks interesting #interesting
## Feb 12
## Feb 13
- Submitted proposal plan for review

# Week 4
## Feb 16
- Huggingface allows streaming
- [Tutorial for Alvis](https://github.com/c3se/alvis-intro/tree/main)
- RLCNet looks good but no code - Fundamentally does what I wanna do
- UniLion has code
## Feb 19
- Alvis/Mimer has datasets but idk if they are outdated
- Doing a beginner's guide to HPC given by chalmers
## Feb 20
- What is LSS (Lift-Splat-Shoot)?
- [Futur3D](https://tsinghua-mars-lab.github.io/futr3d/) does multimodal 3D detection
	- No idea on calibration
	- Not tested for weather resistant
- [Need to read this](UniTR: A Unified and Efficient Multi-Modal Transformer for
Bird’s-Eye-View Representation)

# Week 5
## Feb 23 - 24
- Writing the planning report
![[IMG_20260220_163239570_AE.jpg]]

![[IMG_20260223_162122895_AE.jpg]]

## Feb 25
- Mailed REVERE
- Top two fusion models from nuscenes
	- [C-L based fusion](https://github.com/hht1996ok/EA-LSS)
	- [C-L-R based fusion](https://github.com/tianweiy/CenterPoint)
- [Streaming Datasets](https://docs.mosaicml.com/projects/streaming/en/stable/getting_started/main_concepts.html)

# Week 6
## March 02
- Skimmed Nuscenes and Waymo
- Started using Marimo to make a notebook for nuscenes / dataset
- Basic documentation
## March 03
- Marimo can suck my nuts
- Debugged Jupyter notebook and UV setup
- Reading papers to identify suitable metrics'

## March 04
- [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring]]
- [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving]] -  Dint finish reading
- Working on jupyter notebook - studying nuscens

## March 06
- NuScenes does not have the weather scenes categorized

# Week 7
## March 09
- Have fun exporting all the finnicky packages from /opt for centerpoint
- I hate debugging the installation segment of packages
- Do this
```bash
yay -S gcc7
```

## March 10
- Installed GCC-7
- Fought with Centerpoint and ES_LSS

## March 11
- Friendship with .venv is over, docker is my new best friend (for now)
	- CenterPoint is built (ig)
- In the process of executing code on Centerpoint

# Week 8
## March 16
**Top SF models**
*Note:* we only care about the test set results

| SF Model                                                                                                   | Sensors                             | mAP(!mine) | mATE(!mine) | NDS(!mine) | mAP(mine) | mATE(mine) | NDS(mine) | Desc                                                                                                   | Github?            |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------- | ----------- | ---------- | --------- | ---------- | --------- | ------------------------------------------------------------------------------------------------------ | ------------------ |
| [MVP](https://github.com/tianweiy/MVP?tab=readme-ov-file)                                                  | camera, lidar                       | 66.4       |             | 70.5       |           |            |           | [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^b2db47\|Description]] | yes                |
| [MV2D](https://github.com/wangzt-halo/MV2DFusion?tab=readme-ov-file)                                       | camera, lidar                       | 74.5       |             | 76.7       |           |            |           | [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^89cccc\|Description]] | yes                |
| [EA-LSS](https://arxiv.org/pdf/2303.17895)                                                                 | camera, lidar                       | 72.2       |             | 74.4       |           |            |           | [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^c559ce\|Description]] | yes                |
| [HVDetFusion](https://arxiv.org/pdf/2307.11323)                                                            | camera, radar, lidar(only training) | 60.9       | 37.9        | 67.4       |           |            |           | [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^d905bc\|Description]] | only model no code |
| [EchoFusion](https://arxiv.org/abs/2307.16532)                                                             | camera,radar                        | ~51.42     |             | kradar     |           |            |           | [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^c054b2\|Description]] | yes                |
| [Availability-aware Sensor Fusion<br>via Unified Canonical Space](https://github.com/kaist-avelab/K-Radar) | camera,radar,lidar                  | 87.2       |             | kradar     |           |            |           |                                                                                                        | yes                |

**Metrics**
1. AMOTA (Average Multi-object tracking accuracy | #metrics/tracking ): A metric that measures multi-object tracking performance by averaging tracking accuracy across different recall levels, accounting for false positives, false negatives, and identity switches.
2. NDS (nuScenes detection score | #metrics/detection): A composite metric used in the **nuScenes** benchmark that combines detection accuracy and localization quality (e.g., mAP, translation, scale, orientation, velocity, and attribute errors) into a single score to evaluate 3D object detection performance.
3. mAP (Mean Average Precision | #metrics/detection ): How well the model detects objects correctly (precision–recall performance across classes). Higher mAP = better detection performance.
4. mATE (Mean Average Translation Error | #metrics/localization): The average **position error** (distance between predicted and ground-truth object centers), usually in meters. Lower mATE = more accurate object placement.
5. mASE (Mean Average Scale Error | #metrics/translation ): How accurately the model predicts the **size (width, length, height)** of objects. Lower mASE = better size estimation.
6. mAOE (Mean Average Orientation Error | #metrics/translation ) : The average error in predicting the **heading angle** (rotation) of objects. Lower mAOE = better orientation prediction.
7. mAVE (Mean Average Velocity Error | #metrics/tracking ) : The error in predicting an object’s **velocity** (speed and direction). Lower mAVE = better motion prediction.
8. mAAE (Mean Average Attribute Error | #metrics/attributes ): How well the model predicts object attributes such as: Vehicle state (moving / parked) and Special properties (e.g., emergency vehicle). Lower mAAE = better attribute classification.
9. PKL(Planning KL Divergence| #metrics/trajectory): The difference between predicted and ground-truth trajectory distributions using KL divergence. It evaluates: Planning quality and How close predicted driving behavior is to expert behavior. Lower PKL = better planning performance.

## March 17
1. Read HVDetFusion and EchoFusion
2. Setting up MV2D

## March 18
1. Studying interface of apptainer
2. Re-identified Availability aware SF
	1. Need to implement it
3. Need to make a proper table tomorrow

# Week 9

## March 23
1. Worked on [[Canvas.canvas]]
2. ![[Meeting Notes#March 23]]
## March 24
1. Settin up Bevfusion on apptainer
	1. Dependency issues and other issues here and there
## March 26
1. Working on debugging bevfusion apptainer

## March 27
1. Excel sheets TME180_Group L contains data on Datasets
	1. Number of Lidars, cameras\
	2. Weather
# Week 10
## March 30
1. Can identify which radar and camera is used to identify annotated object
	1. Need to verify
	2. Write down the math
	3. use ngrams and TF-IDF (Scikit)
		1.  And add a level of smartness for identifying weather and objects of interest etc
2. Running dataset preparation of Nuscenes
3. Use parquet and polars for saving the data

## April 02
![[Meeting Notes#April 02]]


# Week 11
## April 08
   1. K-Radar
   ```yaml
      CLASS_VAL_KEYWORD: {
     'Sedan': 'sed',
     'Bus or Truck': 'bus',
     'Motorcycle': 'mot',
     'Bicycle': 'bic',
     'Bicycle Group': 'big',
     'Pedestrian': 'ped',
     'Pedestrian Group': 'peg'
   }
   ```
2.

# Week 12
## April 13
1. Got assistance for Nuscenes preprocessing
	1. In progress
2. Rebuilding Bevfusion container
3. Pausing KRADAR
4. Generating Sensor Analysis data for Nuscenes
5. need to do the other analysis
