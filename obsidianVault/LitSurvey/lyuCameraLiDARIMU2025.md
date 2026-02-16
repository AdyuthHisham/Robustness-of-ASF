# Annotations  
(2/5/2026, 1:11:17 PM)

([Lyu et al., 2025, p. 1](zotero://select/library/items/7WQ3WHBU)) #important  
#review

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=2&annotation=AI4F6NJC) “LiDAR emits laser pulses to generate three-dimensional point clouds, offering centimeter-level spatial accuracy and stable performance under challenging lighting. However, LiDAR typically operates at lower frequencies and produces sparse point clouds with limited detail for small or distant objects. Moreover, it lacks semantic content.” ([Lyu et al., 2025, p. 2](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/lidar  
#basicCalibration/basics

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=2&annotation=6ZMZ7J6P) “The main contributions of this review are as follows: • This paper presents a comprehensive overview of sensor calibration methods, beginning with the fundamental principles of individual sensors in order to construct measurement models and to introduce intrinsic calibration techniques. To the best of our knowledge, it is the first paper to systematically review and analyze extrinsic calibration approaches for three sensor pairings (camera–IMU, LiDAR–IMU, and their joint configuration), addressing a gap in existing literature on multimodal sensor calibration. • This paper summarizes the classification of multi-sensor calibration methods and key factors for evaluating calibration performance. It also provides an overview of opensource calibration tools, detailing their technical characteristics and applicable sensor types. These resources help to reduce redundant development efforts for researchers. Finally, the paper outlines potential future research directions to serve as a reference for continued exploration.” ([Lyu et al., 2025, p. 2](zotero://select/library/items/7WQ3WHBU)) #summary ^962322

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=3&annotation=EBDK5AJZ) “Figure 1. Classification of the Camera–LiDAR–IMU Calibration System” ([Lyu et al., 2025, p. 3](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/basics  
#basicCalibration/camLidar  
#basicCalibration/imu

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=3&annotation=WY5TC4VP) “Target-based methods: These methods establish cross-sensor data associations by introducing specifically designed calibration objects. Common examples include checkerboards or AprilTags [12] for cameras, geometric feature boards for LiDAR, and corner reflector arrays for radar. These methods take advantage of well-defined geometric structures, which simplify data association and help ensure calibration accuracy. However, they require a static environment and are unsuitable for real-time calibration in dynamic settings. Targetless methods: These methods extract features directly from natural environments, such as SIFT [13] or SURF [14] keypoints, lines, or planar surfaces, and leverage motion consistency constraints from IMU measurements to establish data association. Therefore, their performance largely depends on the number of features in natural scenes. From the perspective of the processing mode, calibration methods are categorized as either offline or online. Online calibration continuously updates calibration parameters by integrating them into a joint state estimation framework, where they are optimized alongside other states. In contrast, offline calibration determines the calibration parameters in a single batch once data collection has been completed.” ([Lyu et al., 2025, p. 3](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/basics ^800794

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=3&annotation=IX8BHSRI) “In terms of temporal modeling, calibration approaches are divided into a discrete-time and continuous-time model based on how system states are represented. Traditional methods typically adopt discrete-time models that solve for states at sampled time steps. In high-dynamic motion scenes, these approaches often require interpolating asynchronous sensor measurements, such as aligning timestamps, which can introduce errors and reduce accuracy. The continuous-time model treats the system trajectory as a continuous function, such as a polynomial basis or B-spline, allowing for precise the modeling of motion under non-uniform sampling or rapid movement. However, this increases computational complexity and imposes greater demands on hardware.” ([Lyu et al., 2025, p. 3](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/temporal  
#computationCost ^0fa218

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=4&annotation=WXE7HRZR) “The depth estimation principle of a stereo camera relies on capturing images of the same scene from two slightly different viewpoints using two cameras. By leveraging the concept of disparity and applying triangulation, the distance between the object and the camera can be computed. For example, when the baseline distance is known, the target distance can be directly derived using focal length and disparity values through Equation (1). The depth perception range of a binocular camera extends with the baseline length, where a longer baseline can cover distances of several tens of meters. However, since binocular cameras rely on disparity matching computations, they require highly precise hardware calibration. Factors such as lens optical axis alignment and pixel synchronization errors can significantly affect the reliability of disparity calculations. Equation (1) is formulated as follows: Z= f ·b d (1) where Z denotes the depth, f the focal length, b the baseline, and d the disparity.” ([Lyu et al., 2025, p. 4](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camera/depth ^fe3d96

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=4&annotation=VE47V4JZ) “2.2.2. LiDAR LiDAR is a sensing technology that determines the distance between a device and a target based on either the ToF or the phase shift of emitted light pulses. LiDAR sensors output data as a set of spatial points, known as point cloud data (PCD), which include the x, y, and z coordinates along with intensity values reflecting the strength of the returns from objects or obstacles in the surrounding environment. Based on their scanning mechanisms, LiDAR systems can be broadly categorized into three types [15]: mechanical LiDAR, scanning solid-state LiDAR, and flash LiDAR with non-scanning architectures. The most common mechanical LiDAR uses rotating components to steer laser beams across various angles to achieve a wide field of view. Sensors 2025, 25, 5409 5 of 37 In contrast, flash LiDAR eliminates all mechanical components by emitting a broad laser pulse that covers the entire field of view (FoV) in a single shot, while a focal plane array detector simultaneously captures the reflected signals from the scene, directly generating a three-dimensional point cloud. Scanning solid-state LiDAR systems remove the need for mechanical rotation through various beam-steering techniques, such as micro-electro-mechanical systems (MEMSs) micromirrors, rotating mirrors, or prisms. These methods control the deflection of the laser beam over a limited angular range via electrical signals. By significantly reducing the size and complexity of the device while maintaining high accuracy, scanning solid-state LiDAR has become a mainstream solution in modern autonomous driving applications. Although mechanical LiDAR systems have demonstrated reliable measurement performance, they are constrained by the limitations inherent to their mechanical components. Over time, rotating parts are prone to wear and require periodic maintenance to ensure sustained performance. Additionally, mechanical LiDAR units are susceptible to displacement and structural deformation under external forces such as vibrations or shocks, which can degrade scanning accuracy and system stability. In contrast, scanning solid-state and flash LiDAR systems face constraints primarily in terms of FoV. Mechanical LiDAR can readily achieve a full 360◦ horizontal FoV through continuous rotation. Scanning solid-state LiDAR can increase coverage via oscillating mirrors, but flash LiDAR are typically restricted to a fixed FoV.” ([Lyu et al., 2025, p. 4](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/lidar  
#basicCalibration/basics ^e6f78e

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=5&annotation=SPAXPGTW) “Unlike environment-dependent sensors such as cameras or LiDAR, the IMU is a self-contained localization sensor that operates in both indoor and outdoor settings and remains robust under poor lighting and dynamic scenes. However, IMU measurements are affected by various error sources, including bias drift, temperature-induced variations, sensor noise, and random walk. These errors accumulate during integration, leading to unbounded drift in the estimated state over time.” ([Lyu et al., 2025, p. 5](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/imu

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=5&annotation=99KZDCD3) “2.3. Intrinsic Calibration” ([Lyu et al., 2025, p. 5](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/basics  
#ReferPaper  
#theory

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=8&annotation=KKHNVN2J) “The most common types of systematic errors include angular errors and range errors. Angular errors occur when the initial scanning angle deviates from its ideal orientation, typically due to manufacturing tolerances and assembly imperfections.” ([Lyu et al., 2025, p. 8](zotero://select/library/items/7WQ3WHBU))

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=9&annotation=299B2N6F) “Calib-Net” ([Lyu et al., 2025, p. 9](zotero://select/library/items/7WQ3WHBU))

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=10&annotation=EKIS64LR) “The most straightforward approach to estimating the temporal offset between two signals is to identify the peak of their crosscorrelation [27,28]. Mair et al. [29] proposed two methods independent of spatial alignment for estimating time delays: the cross-correlation method and the phase congruency method.” ([Lyu et al., 2025, p. 10](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/temporal  
#ReferPaper ^42f27c

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=10&annotation=QWGUEMRK) “Experiments showed that the cross-correlation method performs reliably for small delays but yields incorrect optima for large delays.” ([Lyu et al., 2025, p. 10](zotero://select/library/items/7WQ3WHBU))

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=10&annotation=JNY7PHIM) “Alternatively, the temporal offset can be modeled directly as an additional state variable, linked to sensor measurements, and jointly estimated with spatial transformation parameters. This approach supports both constant and time-varying offsets, and the uncertainty of the estimate can also be modeled.” ([Lyu et al., 2025, p. 10](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/temporal  
#interesting

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=11&annotation=24AR6I9H) “3.1. Camera–IMU Extrinsic Calibration” ([Lyu et al., 2025, p. 11](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=11&annotation=YENSRGML) “3.1.1. Decoupling-Based Methods” ([Lyu et al., 2025, p. 11](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#basicCalibration/methods  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=12&annotation=MVQTGVF4) “3.1.2. Filter-Based” ([Lyu et al., 2025, p. 12](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/methods  
#basicCalibration/camIMU  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=13&annotation=PPEANBNJ) “Yang et al. [53] proposed an online self-calibration method for visual-inertial navigation systems based on EKF and conducted an observability analysis, which demonstrated that a fully parameterized calibration system has four unobservable directions, corresponding to global yaw and translation.” ([Lyu et al., 2025, p. 13](zotero://select/library/items/7WQ3WHBU)) #autocalib/algorithm/camIMU

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=13&annotation=UK2HRN5J) “Table 2. Characteristics and Contributions of Selected Filter-Based Camera–IMU Calibration Methods.” ([Lyu et al., 2025, p. 13](zotero://select/library/items/7WQ3WHBU)) #autocalib/algorithm/camIMU  
#basicCalibration/camIMU  
#table

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=14&annotation=ZPX276QC) “3.1.3. Optimization-Based” ([Lyu et al., 2025, p. 14](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#basicCalibration/methods  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=14&annotation=XVA8PKWQ) “In their framework, IMU errors are treated as adaptive constraints embedded into error compensation equations, and the Newton method is employed to iteratively solve for the optimal model parameters.” ([Lyu et al., 2025, p. 14](zotero://select/library/items/7WQ3WHBU))

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=15&annotation=63N8E63A) “Table 3. Characteristics and contributions of some optimization-based camera IMU calibration methods.” ([Lyu et al., 2025, p. 15](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#table  
#basicCalibration/methods  
#opensource

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=15&annotation=4988TDR7) “3.1.4. Learning-Based” ([Lyu et al., 2025, p. 15](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#basicCalibration/methods  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=17&annotation=ABRZHU4D) “Table 4. Comparison of the advantages and disadvantages of four methods of camera–IMU calibration.” ([Lyu et al., 2025, p. 17](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/camIMU  
#review  
#table ^d9e8b6

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=19&annotation=HLSQNQ3Y) “LiDAR–IMU Extrinsic Calibration” ([Lyu et al., 2025, p. 19](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/lidarIMU  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=20&annotation=DKP6EESS) “Table 6. Calibration performance of several LiDAR–IMU methods.” ([Lyu et al., 2025, p. 20](zotero://select/library/items/7WQ3WHBU)) #table  
#basicCalibration/lidarIMU ^8916c4

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=21&annotation=TJBH28VT) “Table 7. Characteristics and contributions of representative LiDAR–IMU calibration methods.” ([Lyu et al., 2025, p. 21](zotero://select/library/items/7WQ3WHBU)) #basicCalibration/lidarIMU  
#opensource  
#table ^afe4ee

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=22&annotation=WPJS2MS7) “Table 9. Camera–LiDAR Calibration Method.” ([Lyu et al., 2025, p. 22](zotero://select/library/items/7WQ3WHBU)) #autocalib/camLidar  
#autocalib/method  
#table  
#theory

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=23&annotation=T6P72IT8) “Traditional calibration of camera–LiDAR–IMU (LVI) systems typically follows a pairwise, chain-based strategy in which the extrinsic parameters are estimated sequentially between sensor pairs to derive the complete spatial and temporal relationships among the three sensors. However, this step-by-step approach introduces operational redundancy and allows errors to accumulate at each stage, since every sensor pair requires a customized calibration process. To address these limitations, joint calibration methods have been developed to estimate the spatiotemporal parameters of all three sensors within a unified framework.” ([Lyu et al., 2025, p. 23](zotero://select/library/items/7WQ3WHBU)) #autocalib/multiSensor  
#important ^51928a

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=25&annotation=UJGX4X7D) “Table 10. Characteristics and contributions of representative LVI calibration methods.” ([Lyu et al., 2025, p. 25](zotero://select/library/items/7WQ3WHBU)) #autocalib/multiSensor  
#opensource  
#table ^cf134d

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=26&annotation=7U2TYW2F) “4.1. Key Evaluation Metrics of Calibration Methods” ([Lyu et al., 2025, p. 26](zotero://select/library/items/7WQ3WHBU)) #autocalib/multiSensor  
#important  
#metrics ^fed09d

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=27&annotation=RTXNTSYV) “Table 12. Summary of open-source calibration methods.” ([Lyu et al., 2025, p. 27](zotero://select/library/items/7WQ3WHBU)) #autocalib/algorithm  
#important  
#opensource  
#table ^8893f6

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=28&annotation=BFVLHKR8) “Table 13. Open datasets summary.” ([Lyu et al., 2025, p. 28](zotero://select/library/items/7WQ3WHBU)) #datasets  
#table ^975f91

[Go to annotation](zotero://open-pdf/library/items/4HDN988Q?page=28&annotation=XV8IQDJP) “4.3. Future Research” ([Lyu et al., 2025, p. 28](zotero://select/library/items/7WQ3WHBU)) #misc  
#ReferPaper