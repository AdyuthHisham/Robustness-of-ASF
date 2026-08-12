## Corruption

### Lidar
1. Frame Deletion (deterministic and random)
Paper: Towards the robustness of MOT

2. Gaussian Noise
Paper: Benchmarking robustness of AI enabled

3. Loss Partial 
Paper: Benchmarking robustness of AI enabled

### Camera
1. Frame Deletion (deterministic and random)
Paper: Towards the robustness of MOT

2. Gaussian Noise
Paper: Benchmarking robustness of AI enabled

3. Loss Partial 
Paper: Benchmarking robustness of AI enabled

### Radar
1. Frame Deletion (deterministic and random)
Paper: Towards the robustness of MOT

2. Noise induced shifts
Paper: Synthesizing and Identify noise levels in Autonomous vehicles camera - radar datasets

3. Loss Partial 
Paper: Benchmarking robustness of AI enabled

## Corruptions already available in K-Radar
### Camera
1. Crack: Overlay crak texture on image
2. Light scratch: Overlay light scratch texture
3. Severe scratch: Overlay severe scratch texture

### Lidar
1. Missed: Remove points in angular range (FOV occlusion simulation)

## Questions about K-Radar/Outputs/noise_visual_inspect

1. What exactly does loss partial do in Radar and Lidar and Camera?
2. The noise injection is not done on OS1 and the side cameras

## 29/July

- Kradar inference only uses rdr_sparse
- Lidar uses ldr_64
- Camera uses camera_front and cam_dir.cropped

## 10/August

### Workflow:
Using the processed frames create a robust test set to create a robust test set to idenitfy the performance of the models on a particular test set. 
Perform inference on the test set using regular data and also data which has noise induced on it
Compare both inference data

### Questions and todo
1. Explain sparsity for every sensor
2. In the visibility analysis parquet what are the ranges of each values and if it can be negative what does the negative value indicate?
3. Explain in depth how noises are added program wise and how it parallels with irl hardware issues. Also mention how the hyper parameters influence the corruption.
4. Add an object density feature that shows how many object are identified in a particular frame of camera, lidar or camera
5. Also add the environment data (not just the weather to the parquet), Like it the object in a highway or something. The descriptions.txt for KRADAR has three values usually (Environment, Time of Day and Weather). I want all these in my parquet.
6. Need to generate a status report of the project
7. Need to identify suitable metrics for the evaluation, for example how much difference is there between the uncorrupted bounding box and corrupted bounding box of an annotation
8. I can use the train set for noise based testing since adding noise changes the train set origianl images. 
9. I dont need the loss complete corruption since frame delete already handles that.
