# 0. Problem Statement
	The objective of this Thesis Project is to develop a pipeline developed for perception tasks.
	The main innovations of this project are
		 - developing a system to autocalibrate multi-sensors online without the use of targets or offline calibration tools.
		 - create a robust system to function in adverse weather climates.
	The main conclusion desired is a system which is on par or better than pre-calibrated systems at performing perception tasks.
# 1. Research Questions

- Which multi-sensor calibration approaches are most suitable for automatic calibration in non-optimal operating environments for non-fixed sensor configurations?
	- Need a robust system to calibrate all sensors without being computationally heavy
	- Need to identify the main sensors to be working with

- To what extent can an automatic calibration framework mitigate perception performance degradation when one or more sensors in the perception stack become degraded or unavailable?
	- Need to find available datasets with different weathers
	- Need to find algorithms to induce artificial weather or noise

- How does automatic calibration within a unified perception framework affect downstream perception tasks compared to manually calibrated sensor setups in standard benchmark datasets?
	- Need to identify and develop a good testing environment
- how to quickly detect the offset of the calibration parameters? At what rate should the calibration data be updated? How much does the offset of the calibration parameters affect the perception results? At the same time, an ideal calibration solution should be able to run on various platforms regardless of their computational constraints, so there is also a difficult task to balance accuracy, efficiency, and resources. [[liAutomaticTargetlessLiDAR2023]]

# 2. Review papers
#### Camera, LiDAR, and IMU Spatiotemporal Calibration: Methodological Review and Research Perspectives [[lyuCameraLiDARIMU2025]] - 2025 #calib

##### contributions
First paper to systematically review and analyze extrinsic calibration approaches for #camera #lidar and #imu pairings. Also summarizes the classification / #theory of multi-sensor calibration methods and key factors for evaluating / #metrics calibration performance. [[lyuCameraLiDARIMU2025#^962322]]

##### calibration
Two types - #target-based and #targetless calibration. #taxonomy

#target-based - Establishes cross-sensor data introducing specifically designed calibration objects. Common examples include checkerboards or AprilTags for #camera , geometric feature boards for #lidar  and corner reflector arrays for #radar.

#limitation is that it requires a static environment and unsuitable for real-time calibration in dynamic settings.  #basicCalibration


#targetless - Extracts features from natural environments from keypoints, lines or planar surfaces and match with IMU to reduce probability by matching features throughout time.

Based on processing mode categorized as #online and #offline . #taxonomy
#online - continuously updates parameters by integrating into a joint state estimation framework. #autocalib
#offline - determines the calibration parameters in one shot. #basicCalibration
*Note:* #online and #offline shouldnt be categorized as #autocalib and #basicCalibration. respectively. I believe the methods can be used for both. #taxonomy
[[lyuCameraLiDARIMU2025#^800794]]]

Based on temporal modelling categorized as #discrete-time and #continuous-time . #taxonomy #temporal
Traditionally - #discrete-time is used to solve for states at sampled time steps. #limitation is that in high-dynamic motion scenes, these approaches often require interpolating asynchronous sensor measurements, such as aligning timestamps, which can introduce errors and reduce accuracy.
#continuous-time treats the system trajectory as a continuous function as a polynomial basis or B-spline allowing for precise modelling under non-uniform sampling or rapid movement. #limitation this increases computational complexity and imposes greater demands on hardware.
[[lyuCameraLiDARIMU2025#^0fa218]]

##### theory #theory
#camera As a widely used imaging sensor, the camera operates based on the principles of optical imaging. Light from the external environment passes through the camera’s lens system, where it is refracted and focused onto a pixel array within the image sensor, such as a CMOS or CCD. Through photoelectric conversion, the optical signal is transformed into a digital image. This imaging process is governed by the camera’s intrinsic parameters, including focal length, principal point, and lens distortion, which together define the projection relationship from the three-dimensional world to the two-dimensional image plane. In addition to monocular #camera/mono , #camera/stereo and #camera/depth cameras are also commonly used. Traditional monocular cameras have more limitations than stereo and depth cameras because they do not inherently provide depth information. Depth must be inferred through triangulation, which restricts their adaptability in complex or dynamic environments. #notTagged

#camera/depth ![[lyuCameraLiDARIMU2025#^fe3d96]]
#lidar #theory ![[lyuCameraLiDARIMU2025#^e6f78e]]
#lidar can be classified into mechanical LiDAR, scanning solid-state LiDAR, flash Lidar #taxonomy

##### intrinsic calibration
#camera Just refer to the paper. Has to be done by user
#lidar Read paper. Calibrated by manufacturer.
#imu The errors can no be predicted or compensated due to its time-varying nature. But modeled using stochastic processes [24] [25] (Refs from the paper)

##### temporal calibration #temporal
![[lyuCameraLiDARIMU2025#^42f27c]] Doesnt work that well for large delays.
The following methods were tried out [[lyuCameraLiDARIMU2025]] -> Table 1. Tldr: Trace method, curve-registration problem, constraint equations, added time as a state variable
##### Extrinsic Calibration
[[lyuCameraLiDARIMU2025#^d9e8b6]] -> Filter based looks like most reasonable.
Also check out Table - 5
###### #camIMU
1. Decoupling-Based
	1. These methods split IMU–camera calibration into simpler subproblems, usually estimating rotation first and translation afterward. Rotation is obtained by aligning relative rotations from gyroscope integration with visual rotation estimates, while translation is solved using accelerometer data and visual motion. They are simple, fast, and intuitive but suffer from error propagation and are sensitive to poor motion excitation.
2. Filter-Based
	1. Filter-based approaches treat the extrinsic parameters as part of the system state in a recursive estimator, typically an Extended Kalman Filter. IMU data predicts the state, and camera measurements update both motion states and extrinsics online. They enable self-calibration during operation but require careful observability and noise modeling to avoid inconsistency.
3. Optimization-Based
	1. These methods formulate extrinsic calibration as a nonlinear least-squares problem, jointly optimizing camera poses, IMU states, biases, and extrinsics over a batch or sliding window of measurements. They combine visual reprojection errors with IMU preintegration errors to achieve high accuracy. While statistically optimal, they are computationally expensive and depend on good initialization and sufficient motion excitation.
4. Learning-Based
	1. Learning-based approaches use data-driven models, often deep neural networks, to estimate IMU–camera extrinsics directly or to assist traditional calibration. By learning the relationship between visual and inertial data, they can be robust to noise and limited excitation. However, they require large training datasets, may not generalize well across sensor setups, and lack strong physical interpretability.
	2. Learning-based methods show considerable potential; however, several unresolved issues, including reliance on labeled data, limited global consistency, and poor interpretability, hinder their ability to replace traditional approaches in the near term. #limitation
###### #lidarIMU
• Regardless of whether LiDAR operates in 128-, 64-, 32-, or 16-channel mode, the algorithm converges to comparable calibration parameter estimates, indicating insensitivity to LiDAR point cloud density [96]. • Experimental comparisons show that, without point cloud de-skewing, calibration results fail to converge and exhibit large fluctuations. When de-skewing is performed using IMU state prediction, scan matching accuracy improves significantly, and calibration parameters converge stably [96]. • During data collection, all rotational and translational degrees of freedom of the sensor suite must be sufficiently excited to ensure full observability of the extrinsic calibration parameters. Experiments demonstrate that, with adequate motion excitation, both translation and rotation parameters converge rapidly; insufficient excitation may result in biased estimates [96,110]. #important
[[lyuCameraLiDARIMU2025#^8916c4]] [[lyuCameraLiDARIMU2025#^afe4ee]]
###### #camLidarIMU
![[lyuCameraLiDARIMU2025#^51928a]] Possible but convergence time is is markedly longer. Robustness evaluations further reveal that current three-sensor calibration methods have not been adequately validated in challenging environments, such as low-texture scenes, dynamic occlusions, or adverse lighting conditions. [[lyuCameraLiDARIMU2025#^cf134d]] Also check out Table 11.

![[lyuCameraLiDARIMU2025#^8893f6]]
##### Metrics
![[lyuCameraLiDARIMU2025#^fed09d]]
1. Automaticity: A key characteristic of automatic calibration is its ability to operate without human intervention.
2. Efficiency: Most existing calibration algorithms depend on iterative optimization to achieve high accuracy, which often results in high computational cost and long processing time.
3. Robustness: Sensitivity to initial values, noise resilience, and environmental adaptability are critical indicators for evaluating the robustness of calibration algorithms, particularly in targetless approaches.
![[lyuCameraLiDARIMU2025#^975f91]]

##### Future Scope #futureScope
1. Low-Cost devices
2. Environment
3. Online Calibration
4. Deep learning

#### Automatic targetless LiDAR–camera calibration: a survey [[liAutomaticTargetlessLiDAR2023]] - 2022 #calib
##### contributions
This paper presents a thorough review of these automatic targetless LiDAR–camera calibration methods. Specifically, based on how the potential cues in the environment are retrieved and utilized in the calibration process, we divide the methods into four categories: information theory based, feature based, ego-motion based, and learning based methods.

##### Types of Automatic targetless LiDAR–camera calibration #taxonomy
![[liAutomaticTargetlessLiDAR2023#^6942e8]]
######  [[liAutomaticTargetlessLiDAR2023#^a32759|1. Information Theory]]
![[liAutomaticTargetlessLiDAR2023#^1f9452]]
Consists of three steps:
1. [[liAutomaticTargetlessLiDAR2023#^fdffbc|3D-2D projection for LiDAR points proj]]
2. [[liAutomaticTargetlessLiDAR2023#^161ed8|Statistical similarity measure]]
3. [[liAutomaticTargetlessLiDAR2023#^f2c703|Optimization]]
information theory based methods evaluate the statistical similarity of data from LiDAR and camera. They calculate precise calibration parameters by maximizing a similarity measurement. However, the accuracy is susceptible to some environmental factors, such as occlusion between objects or the presence of shadows (Pandey et al. 2012) (Parmehr et al. 2014). #limitation #autocalib/method/informationTheory
######  [[liAutomaticTargetlessLiDAR2023#^c3d61c|2. Feature based methods]]
Feature mapping without optimizing their statistical similarities
Consists of three steps:
1. [[liAutomaticTargetlessLiDAR2023#^3eb8ff|Feature extraction]]: Detect unique features
2. [[liAutomaticTargetlessLiDAR2023#^1003cd|Feature matching]]: Match features from camera and LiDAR
3. Transformation estimation: Estimates transformation relationship b/w camera and LiDAR
Many methods combine Feature matching and Transformation estimation.
However, LiDAR data and optical images often capture different characteristics of the environment and feature extraction can be easily affected by random factors such as noise and occlusion (Zhu et al. 2020). Some methods use the motion trajectory of the detected object as a motion feature. This motion feature introduces dynamic information to allow for temporal calibration, however, this variety of methods requires lots of moving objects to generate sufficient trajectories to be tracked #limitation #autocalib/method/featureBased
######  [[liAutomaticTargetlessLiDAR2023#^0b807b|3. Ego-motion based methods]]
Exploits motion of sensors mounted on the vehicle for estimation.
Types:
1. [[liAutomaticTargetlessLiDAR2023#^806e67|Hand-eye based methods]]
2. [[liAutomaticTargetlessLiDAR2023#^d6e61a|3D structure estimation based methods]]
3. [[liAutomaticTargetlessLiDAR2023#^be0c4c|Other Methods]]

They do not require initial calibration parameters and overlapping field of view for hand-eye based methods and turn the 2D–3D registration problem into a 3D–3D registration problem for 3D structure estimation based methods. However, the accuracy of motion estimation for the sensors often affects the performance of these methods. #limitation
However, the accuracy of these algorithms strongly depends on sufficient estimation performance, which usually needs to be refined by other methods (Shi et al. 2019). Since methods based on ego-motion introduces dynamic information, they also need to solve the problem of time synchronization. #limitation
######  [[liAutomaticTargetlessLiDAR2023#^f3ee15|4. Learning based methods]]
Types:
1. ![[liAutomaticTargetlessLiDAR2023#^52c1ec]]End-to-end methods use network models to process input camera images and LiDAR point clouds, then directly output the extrinsic parameters. These methods achieve optimal calibration parameters by minimizing corresponding loss functions.
2. ![[liAutomaticTargetlessLiDAR2023#^780b1e]]Different from end-to-end methods, hybrid-learning methods use neural networks only to extract information such as geometric and semantic features, while feature association and extrinsic parameter calculation procedures are still based on non-learning methods. #important

#### [[shiRadarCameraFusion2024|Radar and Camera Fusion for Object Detection and  Tracking: A Comprehensive Survey]] - 2024 #calib
![[screenshot-2026-02-09-163152.png|Comparison of Lidar/Radar-Camera]]

##### Contributions
- We identify the research gap among the existing reviews  on radar-camera fusion perception by rigorously analyzing the representative surveys listed in Table II and Table  III, which highlight the demand for conducting a comprehensive survey on radar-camera fusion technologies in  terms of object detection and tracking.
- We expatiate on the principles, methodologies, and applications for radar-camera fusion perception, as well as  delve into the emerging strategies for modal representation, data alignment and fusion operation.
- We present a thorough classification for the research  topics of object detection and tracking pertaining to  radar and camera, and provide an up-to-date (2019-2024)  summary of radar-camera fusion datasets and algorithms.
- We elaborately discuss the emerging perspectives in the  direction of radar-camera fusion sensing and highlight the  future development trends.
##### Challenges
1. Deficient in terms of sparsity (Few usable measurements), uncertainty (high variance), ambiguity (different objects reflect differently and motion makes stationary items look like moving) and incompleteness(cant observe scene fully cuz of not full information).
2. Not many public datasets.
3. Lidar-Camera PCDs are wayy better than RADAR-Camera and they are geometrically different so cant be compared one to one.

##### Theory
![[shiRadarCameraFusion2024#^fdb9cd]]]




#### A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving - 2025 #fusion
##### Intro
This paper describes multi-sensor information fusion techniques for autonomous driving environmental perception. Various fusion levels, including data-level, feature-level, and decision-level fusion, are explored, highlighting how these methods can improve the accuracy and reliability of perception tasks such as object detection, tracking, localization, and scene segmentation. In addition, this paper explores the critical role of sensor calibration, focusing on methods to align data in a unified reference frame to improve fusion results. Finally, this paper discusses recent advances, especially the application of machine learning in sensor fusion, and highlights the challenges and future research directions required to further enhance the environmental perception of autonomous systems.
##### #theory
Cameras can provide rich visual information, such as color, texture, and contour, and are widely used for object detection and tracking. Millimeter-wave radar provides data on the distance and speed of objects, which has a wide range of applications in obstacle detection [12], pedestrian [13], and vehicle [14] recognition. GNSS and IMU provide global position information and inertial information for autonomous vehicles to determine their location. This allows the vehicle to update its position in real time on the high-precision map. Lidar can provide accurate distance measurement and three-dimensional spatial information, and is mainly used for positioning, obstacle detection, and environmental reconstruction. Since 3D data provides richer and more accurate environmental information than 2D data, 3D lidar plays an increasingly important role in autonomous driving systems. It can maximize the reconstruction of the real traffic environment to obtain the details of the target by combining sensors such as cameras and lidar.
![[screenshot-2026-02-11-114027.png]] #table #theory
![[Pasted image 20260211134012.png]]
#theory Refer:
1. 2.1. Millimeter-Wave Radar
2. 2.2 Camera
Each unique sensor has it's advantages and disadvantages

#limitation of #target-based is that the target-based calibration method requires setting a specific calibration target; however, the target board has the defect of relatively complex calculation. Secondly, the vehicle will cause changes in hardware, software and the surrounding environment during long-term driving, which will eventually lead to the misalignment of the sensor system, increase the error of the calibration result, or even fail.

#autocalib/ML #limitation the performance of the network is limited by its structural design and capabilities. The overly simple feature extraction and matching network fails to fully consider the geometry of the point cloud. When the internal parameters of the camera change, the trained model needs to be fine-tuned, which may not fully capture the features and relationships between complex sensors, thus affecting the accuracy. Reference [118] proposed CalibNet, which is the first geometrically supervised deep learning method. They use a new architecture based on 3D space transformer, which learns to solve the underlying physical problem by using geometric and photometric consistency to guide the learning process.With a large amount of training data, these methods can obtain suitable feature extraction results. However, the accuracy of this method is inevitably limited by the size of the training dataset and the framework of the deep learning network.

##### #fusion  types #theory
Three types:
1. data-level fusion
2. feature-level fusion
3. decision-level fusion
![[screenshot-2026-02-11-121219.png]]
###### Data Level Fusion
Data-level fusion refers to the fusion process of directly fusing the raw perception data of different sensors and then further processing the fused data. It is a low-level fusion process. This method is most commonly used for multi-source image enhancement, where combining the raw data can present the environment more richly and comprehensively, especially for applications such as remote sensing and image enhancement. In autonomous driving, sensors such as LiDAR and millimeter-wave radar (MMW–radar) generate data at different resolutions and sampling rates. Therefore, spatial and temporal alignment of sensor data is essential to ensure that objects detected by each sensor correspond accurately across all sensors.

This means that the data must be integrated into a unified coordinate system to seamlessly fuse them. For example, compared to camera images, LiDAR provides high spatial resolution but has limited horizontal and vertical resolution. On the other hand, MMW–radar has advantages in bad weather but lacks instant imaging capabilities due to its long wavelength. Data-level fusion achieves fusion by aligning the frames of these different data sources and then integrating them into a comprehensive representation.

Generally speaking, in the research on radar or laser radar (LiDAR) and camera fusion, data-level fusion methods can be divided into two research directions. One is to use the obstacle detection results of radar or laser radar to generate a raster map. The other is to use the optical image as a real sample and generate radar or laser radar images through a generative adversarial network (GAN). #important #fusion

###### Feature Level Fusion
Feature-level fusion refers to the fusion of multi-source heterogeneous sensor data after feature extraction. It is a mid-level fusion that first extracts features from the raw sensor data, such as edges, corners, shapes, and motion patterns, and then merges these extracted features to form a single feature set that can be further processed by machine learning or decision algorithms. Since the same target can be extracted from different sensors in different directions, better target detection and recognition can be achieved.

Target parameter extraction and data feature extraction are two extraction methods in autonomous driving systems. Target parameter extraction includes extracting information such as the size, distance, direction, speed, and acceleration of the target from preprocessed data. Many studies use radar or LiDAR to extract the location features of the target and assist image recognition by generating a region of interest (ROI). This region directly converts the target position detected by the radar into an image, thereby forming a specific area. Data feature extraction is to extract the shape, edge, texture, time–frequency characteristics, and color distribution of the target from the image or processed data for classification and recognition.

###### Decision Level Fusion
Decision-level fusion is a high-level fusion. Each sensor does not merge the raw data and features, but processes its own data independently first, and then fuses the final decision of each sensor through the decision fusion method, so as to make a decision or prediction on the detected object or environment. Common methods of decision fusion include probability-based methods, deep learning methods and fuzzy subset hypothesis methods.

new sensors or update individual sensor algorithms without affecting the entire system. However, since only the final decision is fused, many of the detailed information available in the raw data or features are lost. This may limit the system’s ability to make a nuanced interpretation of the environment. It can also be challenging to handle conflicting and redundant data from multiple sensors. In some studies, it is combined with other fusion methods to take advantage of the advantages of each level while mitigating its limitations. #limitation

##### #fusion/algorithms

![[Pasted image 20260211131611.png]]
###### Kalman Filter
The Kalman filter is a recursive algorithm that uses input measurements from a mathematical process model to recursively estimate the current state of a system over time [133]. It is implemented in two steps: first, in the prediction phase, an estimate of the current state is given under uncertainty. Then, after the measurement is obtained, the previous estimate is updated by a weighted average.

However, the Kalman filter can only accurately estimate linear systems and it is difficult to achieve optimal estimates for nonlinear systems. Since the motion process of the vehicle is nonlinear, many studies have adopted variants of Kalman filtering, such as extended Kalman filtering and unscented Kalman filtering, to linearize the nonlinear problem, and select the optimal algorithm according to different linearity models.

###### Bayesian Estimation
Bayesian estimation is a method that represents various uncertain information provided by multiple sensors as probabilities, and processes them using the Bayesian conditional probability formula in probability theory [134]. Bayesian estimation is a common method for multi-sensor low-level redundant data fusion, and its information is described as the probability distribution of sensor information with Gaussian noise uncertainty added. Bayesian estimation is based on minimizing risk cost as a model and can update the hypothesis likelihood function given a prior likelihood estimate and additional observations.

###### D-S evidence theory
The D-S evidence theory is a generalization of Bayesian estimation. The D-S evidence theory is not hindered by incomplete models or a lack of prior information. The Bayesian theory requires the definition or assumption of prior probabilities and can only assign evidence to one hypothesis. In the D-S evidence theory, evidence is assigned only based on known information and no assumptions are made.

```chatgpt
**Dempster–Shafer (D-S) evidence theory** is a framework for reasoning and fusing **uncertain, imprecise, or conflicting information** from multiple sensors. Unlike Bayesian probability, it doesn’t require precise priors and can explicitly represent **ignorance** by assigning belief to sets of hypotheses rather than single outcomes. Using **basic probability assignments (BPAs)** and **Dempster’s rule of combination**, it merges evidence, reinforcing agreement and handling conflict, producing a **range of belief** for each hypothesis instead of a single probability. D-S is **model-agnostic**, meaning it does not need a state-space or dynamic model, making it suitable for **categorical or static decision problems**. Its main limitations are **high computational cost** for many hypotheses, potential counterintuitive results under strong sensor conflicts, and lack of natural temporal handling compared to **Bayesian or Kalman filters**.
```
Tldr: No state space - reads the sensor values and merges the probability in fancy way

###### Deep learning
\shrug it's just deep learning dawg.

#### A Review of Multi-Sensor Fusion in Autonomous Driving - 2025 #fusion

##### Introduction
The primary goals of this work are as follows:
1. To introduce the theoretical foundations behind sensor fusion, including mathematical models, uncertainty handling, and fusion principles.
2. To analyze and categorize major fusion strategies based on the abstraction level, target tasks, and architectural design.
3. To discuss the advantages and limitations of camera–LiDAR fusion, BEV transformation, cross-modal Transformer layers, and temporal fusion methods.
4. To highlight real-world deployment challenges, including robustness under sensor failure, calibration errors, and domain generalization.
5. To explore inspirations from other domains, particularly agriculture and robotics, for understanding the transferability of fusion architectures.
6. To envision future directions with emerging paradigms such as foundation models, diffusion-based representation recovery, and large language model (LLM)-driven decision making.

##### #fusion/algorithms

![[Pasted image 20260211134634.png]] #fusion #fusion/algorithms
![[Pasted image 20260211135031.png]] #fusion #theory

##### Learning paradigms for Fusion
###### Deep learning Based
For instance, Transfuser employs early-stage camera and LiDAR fusion within a shared CNN backbone, followed by a multi-branch transformer decoder that separately processes route planning and control signals.

Not totally ML

Key #advantages include:
1. Scalability to high-dimensional sensory data.
2. End-to-end optimization from raw input to control output.
3. Ability to capture nonlinear and long-range cross-modal dependencies.
However, deep models are often criticized for their lack of interpretability and reliance on large labeled datasets. Overfitting to training domains and sensitivity to sensor failure also remain challenges. #limitation #ml

###### Probabilistic Fusion Models
Probabilistic models offer a principled framework to handle uncertainty, sensor noise, and partial observability. Techniques such as Kalman Filters, Bayesian networks, and Particle Filters have traditionally been used in localization and tracking tasks. These models estimate the posterior distribution of state variables given noisy observations from multiple sensors.

#advantages  of probabilistic methods include:
1. Explicit modeling of noise and confidence in sensor readings.
2. Smooth state estimation over time.
3. Lightweight implementations suitable for real-time systems.

 Nonetheless, their performance heavily depends on accurate sensor noise models and hand-crafted dynamics, limiting flexibility in highly dynamic or unstructured environments. #limitation

###### Hybrid and Self-Supervised Approaches
These systems integrate neural network based perception with probabilistic inference or leverage self-supervised objectives to enhance data efficiency.

These hybrid strategies provide:
1. Improved generalization under label scarcity.
2. Robustness to partial sensor failure.

##### Fusion Architecture
![[Pasted image 20260211140836.png]] #fusion #theory

###### Early Fusion
Early fusion combines raw or minimally processed data from multiple sensors before any substantial feature extraction. The motivation is to preserve the rich information content across all modalities, allowing a neural network to learn joint features from the very beginning

An #advantage of early fusion lies in its potential to learn deeply coupled cross-modal interactions. It allows the network to leverage complementary modalities early on—for example, aligning semantic texture from the camera with structural geometry from LiDAR.

early fusion also introduces significant challenges: raw data from different sensors often differ in spatial resolution, coordinate frames, sampling rates, and noise characteristics. Aligning such data naively can inject ambiguity or redundancy. Moreover, early fusion tends to result in high-dimensional input spaces, requiring large models and extensive data to train effectively. #limitation

###### Mid-Level Fusion
Mid-level fusion, by contrast, processes each modality independently to obtain semantically meaningful features before performing integration. This allows the network to exploit domain-specific feature extractors—e.g., CNNs tailored to images and PointNet++ or voxel-based encoders for point clouds—prior to fusion.

Mid-level fusion provides a flexible compromise: it reduces the dimensionality of inputs, mitigates sensor misalignment, and enables task-specific fusion heads for downstream components such as detection or planning. **Furthermore, it accommodates missing or degraded sensor inputs by allowing fallback to single-modality streams.** #advantage  #important  ^5aff56

One drawback, however, is the potential loss of fine-grained cross-modal cues due to decoupled early processing. Cross-attention mechanisms are often used to compensate for this gap. #limitation

###### Late Fusion
Late fusion strategies keep modalities separate through most of the network and only merge outputs at the decision level, such as combining detection results or trajectory predictions from each modality.
While this approach lacks deep joint feature learning, it offers high modularity and robustness. #advantage For example, in [14], late fusion aggregates detections from multiple views to improve robustness in adverse conditions. Late fusion is computationally efficient and interpretable, and allows independent optimization of each sensor’s processing pipeline.
However, its main #limitation is its inability to capture inter-modal dependencies at the feature level, making it suboptimal for tasks requiring rich spatial or semantic integration.

###### Evaluation
many real-world autonomous driving systems adopt a hybrid fusion strategy. For instance, HydraFusion [11] #important dynamically adjusts the fusion point depending on context and task, exploiting early fusion in clear environments for detailed reasoning and shifting to mid or late fusion in adverse conditions for robustness.
In summary, the choice of fusion timing: early, mid, or late, should be guided by sensor characteristics, computational constraints, and downstream task requirements. While early fusion enables deep inter-modal coupling, mid-level fusion provides a balance of flexibility and efficiency, and late fusion ensures safety-critical redundancy.

![[Pasted image 20260211141910.png]]![[Pasted image 20260211141928.png]]![[Pasted image 20260211142104.png]]![[Pasted image 20260211142110.png]]

###### 6.4. Toward Universal Fusion Foundation Models
Inspired by CLIP, SAM, and Flamingo [117] in vision–language domains, the community is exploring foundation models for sensor fusion, large-scale pre-trained backbones trained across multiple modalities, tasks, and environments. Unlike task-specific fusion architectures, these models aim to learn general-purpose representations that transfer across datasets and geographies. Early attempts like TransFusion #important , BEVFusion #important , and CMT #important  pretrain encoders on multimodal perception (e.g., camera + LiDAR), but remain constrained to fixed sensor types.

A true foundation fusion model would:
1. Accept arbitrary sensor combinations as input (plug-and-play).
2. Output universal representations (e.g., BEV maps, occupancy fields, trajectories).
3. Transfer across domains with minimal fine-tuning.

This direction demands massive multi-modal datasets with high annotation diversity. Self-supervised training with cross-modal contrastive loss, masked reconstruction, and diffusion pretext tasks can bootstrap training at scale. Moreover, multi-modal alignment tokens, similar to vision–language alignment in BLIP [118], can guide interaction between modalities. By combining the structured reasoning of LLMs, generative fidelity of diffusion, and temporal expressivity of Mamba, foundation fusion models can become both generalizable and controllable. A modular backbone (e.g., a camera encoder, a LiDAR encoder, a fusion head, and a planner head) may soon dominate real-world autonomous driving stacks. #important #important

In response, there is a rising interest in self-adaptive fusion systems, which can dynamically assess sensor reliability and reconfigure the fusion strategy during runtime. For instance, AdaFusion [100] #important proposes attention-based gating mechanisms to downweight noisy or degraded modalities. Similarly, DGFEG #important [101] leverages a dynamic graph structure to route information adaptively between sensor-specific branches. These approaches aim to enhance robustness under partial sensor failure or domain shifts. To achieve full self-adaptivity, future models must integrate principles from uncertainty modeling [102] #important , meta-learning, and policy-driven fusion. Techniques such as dropoutbased uncertainty estimation, test-time adaptation, and reinforcement-learned fusion policies could enable systems to select optimal modality combinations based on environmental context, reliability cues, or resource constraints. Additionally, cross-task and cross-modal pretraining pipelines that support continual learning are essential to maintain performance as sensor suites evolve or new cities are deployed. For instance, multi-task supervision across detection, occupancy, and motion forecasting—as adopted in recent frameworks like Unified-IO #important  [103] and Mask2Map #important  [104] provide a scalable path toward shared representations that generalize across both tasks and sensors. In conclusion, while multi-sensor fusion has traditionally been viewed as a static architecture problem, the rise of foundation models and adaptive learning marks a paradigm shift. Future systems must not only fuse modalities efficiently but also reason about fusion quality, adapt to degradation, and evolve with new data distributions—transforming static perception stacks into flexible, self-improving agents for real-world autonomy. In conclusion, while multi-modal sensor fusion forms the backbone of modern autonomous driving perception systems, its practical deployment faces a multifaceted set of challenges. These span robustness, alignment, efficiency, generalization, and interpretability. Addressing these issues requires not only algorithmic innovation but also cross-domain inspiration, large-scale data infrastructure, and holistic system design thinking.
###### 6.5. Self-Adaptive and Continually Evolving Fusion Systems
Static fusion models, once deployed, often suffer performance degradation under changing environments, sensor wear-out, or unseen scenes. To address this, self-adaptive fusion systems must evolve beyond fixed pipelines to support lifelong learning, policydriven configuration, and dynamic recovery [99] #important .

Core enablers include:
1. Online uncertainty estimation to modulate fusion weights [119].
2. Memory-augmented architectures (e.g., retrieval-based Mamba) for context-aware fusion.
3. Reinforcement learning (RL) policies to optimize sensor selection or fusion mode based on downstream performance (e.g., braking accuracy, latency) [120].
4. Curriculum learning frameworks to gradually expose fusion models to harder conditions (e.g., sensor failure, low light) [121].

Furthermore, continual adaptation requires stability-plasticity balancing: ensuring models retain prior skills while adapting to new ones. Tools like Elastic Weight Consolidation [122], replay buffers, or generative rehearsal (e.g., using diffusion to simulate past scenes) may assist in this. Finally, self-adaptive fusion systems must be interpretable, fail-safe, and certifiable. Coupling real-time causal attribution, uncertainty thresholds, and fallback rules (e.g., logic override under low sensor confidence) is essential for deployment-grade trust. In summary, the future of multi-modal sensor fusion lies in a cross-pollination of deep learning advances: generative modeling (diffusion), efficient sequence modeling (Mamba), and contextual reasoning (LLMs). These paradigms promise not only to enhance fusion accuracy and robustness but also to enable transparent, adaptable, and scalable autonomous systems. The fusion architectures of tomorrow will likely be modular, foundation-based, and self-evolving, which will usher in a new era of intelligence at the intersection of perception, semantics, and control.

# 3. Taxonomy #taxonomy

# 4. Papers
*Note: *

## Perception and sensing for autonomous vehicles under adverse weather conditions: A survey

![[Pasted image 20260303153441.png]]

Has some good notes on Influence of #weather on #sensors. #theory



Mai et al. [142] applied fog to the public KITTI dataset to create a Multifog KITTI dataset for both images and point clouds. #datasets
#metrics like SSIM (Structural Similarity Index Measure) can be used for KITTI stuff ^^

the existing de-hazing quality metrics are restricted to non-reference image quality metrics (NRIQA) [189]. #metrics

[Canadian adverse driving conditions dataset](http://cadcd.uwaterloo.ca/) #datasets

![[Pasted image 20260303160943.png]]

## Safe Autonomous Driving in Adverse Weather:  Sensor Evaluation and Performance Monitoring

Overall can be used as #metrics for testing performance of SF models in adverse conditions #important

```text
The following is used for the different sensors: the dispersion in the vehicle bounding for lidar, the object confidence score of YoloV5, and additionally, the intersection of unions (IOU) with the ground truth bounding box for the camera and the number of detection points of the test vehicle for radar.
```
😀 🤣 👍u
## EPSM: A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving
#important looks like a goldmine of #metrics
**Related Work** is #important
```
Kim et al. [15] proposed a metric for real-time video surveillance systems; they include the time which is required to detect an object.
```
### Metrics
1. TTC -Time to collision
2. TTCE - Time to closest encounter
3. Bidirectional rating
Screw that .

### Keywords/Topics of interest

## 4.1 First Pass
*Note: 10 - 15 mins*
```
Abstract - Method - Contributions - Conclusions
```

## 4.2 Second Pass
```
Calibration theory - Optimization methods - Assumptions / Limitations
```

## 4.3 Third Pass
```
Implementation - Failure cases - Datasets
```
