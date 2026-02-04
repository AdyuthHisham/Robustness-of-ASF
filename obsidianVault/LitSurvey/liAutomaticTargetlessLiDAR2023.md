# Annotations  
(2/2/2026, 3:12:45 PM)

([Li et al., 2023, p. 9949](zotero://select/library/items/PS2ECS24)) #review  
#important  
#2022  
READ REVIEWS FOR EACH METHOD

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9951&annotation=H2UFY7GT) “(1) information theory based methods that measure the statistical similarity between joint histogram values of several common properties between the two modalities, (2) feature based methods that extract geometric, semantic or motion features from the environment, (3) ego-motion based methods that make use of the sensor-movement related information, and (4) learning based methods that use neural network models to estimate the extrinsic parameters.” ([Li et al., 2023, p. 9951](zotero://select/library/items/PS2ECS24))

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9953&annotation=JCE2X432) “where fx and fy denote the focal length in pixels on the x and y axes respectively, (u0, v0) denotes the optical center (the principal point), and s denotes the skew coefficient, which is non-zero if the image axes are not perpendicular. Meanwhile, ZC denotes the depth scale factor.” ([Li et al., 2023, p. 9953](zotero://select/library/items/PS2ECS24)) #basicCalibration/camera

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9953&annotation=3V9RTLB6) “where R and t denote the rotation matrix and the translation vector between LiDAR and camera coordinates, respectively. Let T = [R t]. In the following, we use T to denote the extrinsic parameters.” ([Li et al., 2023, p. 9953](zotero://select/library/items/PS2ECS24)) #basicCalibration/camLidar

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9954&annotation=P82K3SJW) “Automatic target-based Different from manual target-based methods, these methods do not require human intervention, where the correspondences between point clouds and images are automatically estimated using various features w.r.t. the calibration targets. There are various calibration methods in this category. For instance, Geiger et al. (2012) presented an automatic extrinsic calibration method using a single shot only. In specific, the method required finding several checkerboards in different places, other than taking several shots on one checkerboard located differently. Toth et al. (2020) uses a spherical target for automatic extrinsic calibration. The method calculates the sphere center of the target using the detected surfaces and contour from point clouds and images respectively, and estimates extrinsic parameters via the geometric constraint for the same sphere center. Manual targetless Extrinsic parameters may need to be adjusted online in some real-world applications, like self-driving (Levinson and Thrun 2013). Then targetless calibration methods are required to estimate extrinsic parameters in the real world without specified targets. Manual targetless methods consider the problem by manually specifying the correspondences between point clouds and images, which often require a set of predefined rules or patterns for selecting the correspondences. For example, Scaramuzza et al. (2007) proposed a targetless calibration method. The method first manually selects a set of pairs between 3D points in point clouds and pixels in images. Then it estimates extrinsic parameters using the PnP (Perspective from n Points) algorithm (Quan and Lan 1999) followed by an iterative least-squares refinement. Automatic targetless Automatic targetless calibration methods estimate extrinsic parameters by exploiting useful information from surrounding environments automatically. These approaches neither require any specified calibration targets nor heavy manual work. In the next section, we summarize various existing automatic targetless extrinsic calibration methods according to which information they are used for the estimation.” ([Li et al., 2023, p. 9954](zotero://select/library/items/PS2ECS24)) #basicCalibration/basics

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=NUDXTQEY) “three categories of automatic targetless LiDAR–camera calibration methods, i.e., information theory based methods, feature based methods, and ego-motion based methods. Different from them, learning based methods use neural networks to implicitly capture useful information from environments for the calibration.” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/method  
#important

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=9NJ9WQP4) “information theory based methods are preferred for environments with few features, as they are to maximize the similarity between (the projection of) the set of all 3D points from the LiDAR and the whole image from the camera, rather than certain kinds of features.” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=6LGPBMFH) “feature based methods are suitable for scenes that provide sufficient features such as urban environments with rich geometric and semantic features.” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=ZTZVMIPF) “Ego-motion based methods can be performed for scenarios when both LiDAR and camera are moving during the calibration process, like the case that both sensors are mounted on a moving car.Correspondingly, ego-motion based methods should not be applied for scenarios when both sensors are static during the calibration process, like the applications of roadside sensing systems” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/methods/egoMotion

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=URN8MSPY) “the applications of learning based methods require large sets of training data and enough computing resources for online inference.” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/method/learningBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9955&annotation=U33V2MJU) “3.1 Information theory based methods Information theory based methods estimate the extrinsic parameters by maximizing the similarity transformation between the LiDAR sensor and the camera, which is measured by various information metrics. In specific, the basic principles of information theory based methods can be summarized as the following equation: 9956 X. Li et al. 13 where PL denotes the set of 3D points generated by the LiDAR sensor, pC denotes the image generated by the camera, projT denotes the project function from the set of 3D points to the image w.r.t. the extrinsic parameters T, and IM denotes the corresponding information metric that measures the similarity between projT(PL) and pC. Following the statement in Eq. (4), an information theory based method for LiDAR–camera calibration consists of three steps: 3D–2D projection for LiDAR points projT projects the set PL of 3D LiDAR points to the image projT(PL) w.r.t. the extrinsic parameters T. Statistical similarity measure IM measures the statistical similarity between the 2D projected image projT(PL) and the camera image pC w.r.t. some features that share the similar distribution between the sensor data obtained by LiDAR and camera. Notice that, different choices of these features and corresponding statistical dependence measures would result in different LiDAR–camera calibration methods. Optimization The statistical dependence measure IM is usually a non-convex function, which requires an optimization method to reach global optima. A typical pipeline of an information theory based approach is shown in Fig.4. Note that, there are several attributes of the sensor data obtained by LiDAR and camera that share a similar distribution. For instance, LiDAR data points with high reflectivity usually correspond to bright surfaces in the image, and points with low reflectivity correspond to dark areas (Pandey et al. 2012). The correlation between the LiDAR reflectivity and camera intensity is often applied to measure the similarity between the data of LiDAR and camera. Besides reflectivity and intensity, gradient magnitude and orientation extracted from both LiDAR points clouds and camera images can also be considered here (Taylor et al. 2013).” ([Li et al., 2023, p. 9955](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9956&annotation=CHYKQPT6) “3.1.1 Pairs of point cloud and image attributes” ([Li et al., 2023, p. 9956](zotero://select/library/items/PS2ECS24)) **Methods to compare Cameras and Lidars**  
#autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9956&annotation=5CVEWANW) “T∗ = argmax T IM( projT(PL), pC )” ([Li et al., 2023, p. 9956](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=DWMVUYYQ) “Reflectivity—Grayscale intensity” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=APKLVLZ6) “Surface normal—Grayscale intensity” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=RCFVEJEZ) “Gradient magnitude and orientation—Gradient magnitude and orientation” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=YQNMEJ9D) “3D semantic label–2D semantic label” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=9F5PAVIC) “Combination of 3D–2D attribute-pairs” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9957&annotation=Z46WI3BN) “3.1.2 Statistical similarity measure Based on the above attribute pairs for LiDAR point clouds and camera images, we can use various statistical dependence measures to measure the statistical similarity between” ([Li et al., 2023, p. 9957](zotero://select/library/items/PS2ECS24)) **Measure of relativity between Cameras and Lidars**  
#autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9958&annotation=XTPIWYGZ) “them, where larger measure values lead to better correspondences. In the following, we summarize statistical dependence measures that are commonly applied in existing information theory based methods.” ([Li et al., 2023, p. 9958](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9959&annotation=35GCLR2L) “3.1.3 Optimization methods We also summarize optimization methods that are most commonly adopted in existing information theory based methods.” ([Li et al., 2023, p. 9959](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9960&annotation=NR6A8FZL) “3.1.4 Summary of information theory based methods Following the above discussion, we summarize information theory based methods in Table 1 and group the methods by corresponding ‘Information metric’, ‘LiDAR attribute – Image attribute’, and ‘Optimization method’. When using combined 3D–2D attribute pairs, the specific attribute pairs are selected differently for each method. Taylor and Nieto (2013) and Guislain et al. (2017) both choose ‘reflectivity - grayscale intensity’ and ‘surface normal - grayscale intensity’ the two attribute pairs. Irie et al. (2016) also used ‘depth discontinuity – edge’ attribute pair. The assumption of this method is that depth changes in the point cloud are likely to appear as edges in the image, which will be described in detail later in the feature based method section. Zhao et al. (2016) used reflectivity, surface normal, and curvature as LiDAR attributes and intensity, hue, and gradient as image attributes. Here, the curvature attribute in the point cloud is used to correspond to the gradient attribute in the image. Besides reflectivity and surface normal for the point cloud and color for the image, the curvature attribute in the point cloud corresponds to the gradient attribute in the image.” ([Li et al., 2023, p. 9960](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9960&annotation=JJJQ5S2N) “3.2 Feature based methods Different from information theory based methods, feature based methods for automatic targetless LiDAR–camera calibration directly extract and match the features from LiDAR and camera images, without optimizing their statistical similarities. Features that are commonly adopted in these methods can be sorted into three categories, including geometric, semantic and motion features. They need to be acquired online from both LiDAR points and camera images of surrounding environments. In specific, geometric features are constructed by a set of geometric elements like points or edges in environments. Semantic features are high-level representations that often specify semanticaware components of the environment, such as skylines, cars, and poles. Motion features describe the characteristics of moving objects, including pose, velocity, acceleration, etc. As illustrated in Fig. 5, the process of a typical feature based method often contains three steps, i.e., feature extraction, feature matching, and transformation estimation. Feature extraction Feature extraction aims to automatically detect stable and unique features from both point clouds and images. These features usually represent specific geometric or semantic elements in the surrounding environments. Feature matching Feature matching intends to provide the correspondence between the features extracted from the point cloud and the image. For this purpose, various feature descriptors as well as spatial relationships between features are applied. Transformation estimation This step estimates the transformation relationship, i.e., extrinsic parameters, for LiDAR–camera calibration, based on feature correspondences provided by feature matching. Singular Value Decomposition (SVD) is a widely applied algorithm for the step. Meanwhile, many methods also combine the steps of feature matching and transformation estimation (Levinson and Thrun 2013; Li et al. 2017; Zhu et al. 2020). They estimate the transformation relationship while looking for the feature correspondences.” ([Li et al., 2023, p. 9960](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9961&annotation=2RK7LZHW) “Table 1 Summary of information theory based methods” ([Li et al., 2023, p. 9961](zotero://select/library/items/PS2ECS24)) #autocalib/method/informationTheory  
#ReferPaper  
#opensource

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9962&annotation=W3QI4QV6) “3.2.1 Feature extraction” ([Li et al., 2023, p. 9962](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=LX8N6IBN) “We collect these pairs into three categories, i.e., both features in the pair are geometric features, semantic features, and motion features, respectively.” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) **Pair here refers to the fact that LiDAR needs a feature extractor and Camera needs a feature extractor**  
#autocalib/method/featureBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=KPZY75Z4) “Points of interest are geometric features that are widely applied in LiDAR–camera calibration. A point of interest may have a special attribute that can be significantly different from its neighbors, such as color or brightness. It may also have an explicit location in the image space, e.g., intersection points of geographic edges (Willis and Sui 2009). Point features can be calculated regularly and reliably to provide effective detection results.” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/POI

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=K9B4FIII) “Förstner operator–Förstner operator” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=5FDZ8G6H) “Corner–Corner” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=AQV8JE8I) “SIFT–SIFT Scale Invariant Feature Transform (SIFT)” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=QQF9QHJ3) “Besides points of interest, edges are another type of geometric feature that is widely applied in LiDAR–camera calibration. These edges in point clouds and images contain geometric information of environments that are useful, especially for environments when point features disclose their instability” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9963&annotation=9J576JM9) “Depth discontinuity—Intensity difference” ([Li et al., 2023, p. 9963](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9964&annotation=BL5HB89F) “Depth discontinuity—Sobel operator” ([Li et al., 2023, p. 9964](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9964&annotation=SNU7KBRV) “3D line detector—LSD” ([Li et al., 2023, p. 9964](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9964&annotation=W7ZYW7FI) “Depth continuity—Canny detector” ([Li et al., 2023, p. 9964](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9964&annotation=VXMXIALM) “Depth continuity—L-CNN” ([Li et al., 2023, p. 9964](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/edges  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9964&annotation=D4XCFLRR) “Notice that, real-world environments often contain a large number of similar geometric features, which would increase the difficulty of LiDAR–camera calibration. On the other hand, semantic features often reflect high-level characteristics that account for semantic-aware constraints of the environments, such as skyline (Hofmann et al. 2014), vehicles (Zhu et al. 2020), and road lanes (Ma et al. 2021). This semantic information is consistent across data modalities. Then they can be extracted from both LiDAR point clouds and camera images and used for LiDAR–camera calibration.” ([Li et al., 2023, p. 9964](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/semanticAware

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9965&annotation=LRK2CKMX) “Skyline–Skyline” ([Li et al., 2023, p. 9965](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/semanticAware  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9965&annotation=RLNNMZI4) “Lane and Pole–Lane and Pole” ([Li et al., 2023, p. 9965](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/semanticAware  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9965&annotation=LD7JBAJX) “3D Semantic Centroid–2D Semantic Centroid” ([Li et al., 2023, p. 9965](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/semanticAware  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9965&annotation=S2GNV8MF) “Object trajectory–Object trajectory” ([Li et al., 2023, p. 9965](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/geometricfeatures/trajectory  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9965&annotation=VL2VGSK8) “3.2.2 Feature matching strategies Feature matching intends to establish the correspondences between the points in LiDAR point clouds and the pixels in images, which are identified by feature extraction. Here we summarise popular feature matching strategies, which are specified for certain kinds of features by considering descriptor similarities and spatial geometric relationships, respectively.” ([Li et al., 2023, p. 9965](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/strategy

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9966&annotation=2RVDAAF6) “Descriptors similarity” ([Li et al., 2023, p. 9966](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/strategy  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9966&annotation=6SHAETSQ) “Spatial geometrical relation” ([Li et al., 2023, p. 9966](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/strategy  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9966&annotation=GF63EX32) “Semantic relation” ([Li et al., 2023, p. 9966](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/strategy  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9966&annotation=6MW9Z5C5) “Trajectory relation” ([Li et al., 2023, p. 9966](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased/strategy  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9966&annotation=SD52H58G) “3.2.3 Summary of feature based methods In Table 2, we summarize feature based methods for LiDAR–camera calibration and group them by categories of their features. Besides the methods listed in Table 2, there exist multiple methods (Bileschi 2009; Banerjee et al. 2018; Blaga and Nedevschi 2017; Xiao et al. 2017; Li et al. 2017; Jiang et al. 2018; Munoz-Banon et al. 2020; Ma et al. 2021) that extract line features in point clouds and images respectively using depth discontinuities with image edge detectors. Besides only considering line features alone, there are also methods that use the combination of line features and depth information from both images and point clouds for calibration. These methods assume that the depth difference between the measured LiDAR data and the image should be minimized. The depth information from images can be obtained either from the point cloud projection (Castorena et al. 2016) or from the monocular depth estimation (Vaida and Nedevschi 2019). For the methods that extract lines using depth continuity in the point cloud, the point cloud is often segmented into uniform size voxels in Yuan et al. (2021). Different from these methods, Liu et al. (2021) implements the adaptive voxelization to dynamically segment the LiDAR point cloud into voxels of different sizes.” ([Li et al., 2023, p. 9966](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9967&annotation=58LX5R4A) “Table 2 Summary of feature based methods” ([Li et al., 2023, p. 9967](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased  
#ReferPaper  
#opensource

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9968&annotation=PIIVCY93) “As an alternative method for extracting feature points, Nieto et al. (2010) used the SIFT extractor automatically and matches the features by looking for the two closest features in the space of SIFT descriptors. As an alternative way to use semantic features, Zhu et al. (2020) applied semantic masks of vehicles in the image and constructs a height map to encourage LiDAR points to fall on the pixels labeled as vehicles. In this work, semantic segmentation is performed only in the image.” ([Li et al., 2023, p. 9968](zotero://select/library/items/PS2ECS24)) #autocalib/method/featureBased

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9968&annotation=A4XDMUD5) “3.3 Ego‐motion based methods Ego-motion based methods exploit the motion of sensors mounted on the traveling vehicle to estimate the extrinsic parameter. In this scope, some methods try to find the correspondence between the trajectories generated by LiDARs and those by cameras, with LiDARs and visual odometry techniques, or IMU and GNSS measurements (Taylor and Nieto 2015; Ishikawa et al. 2018; Park et al. 2020). There are also methods that make use of the structure from motion (SfM) approach to estimate the 3D structure from the image sequences, thus converting the 3D–2D LiDAR–camera data registration into a 3D–3D case (Swart et al. 2011; Nagy et al. 2019a). In accordance with how the ego-motion information between sensors is used, ego-motion based methods can be divided into hand-eye based and 3D structure estimation based ones.” ([Li et al., 2023, p. 9968](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9968&annotation=GAC4HM4B) “3.3.1 Hand‐eye based methods Hand-eye calibration problem is a fundamental and critical issue in robot vision applications. It is a problem in determining the transformation between a robot base and a camera, in the case where the camera (the “eye”) is mounted on an arm (the “hand”) of the robot, or fixed elsewhere other than the arm. The mathematical formulation of this problem also takes the form of AX = XB, where A and B describe the motions of the arm and the camera respectively, and X is the desired unknown transformation matrix. Methods discussed in this section extend the traditional hand-eye calibration to the LiDAR–camera calibration problem, although the rigid-mounted robot sensors should satisfy the same traditional constraints. Given the following notation:” ([Li et al., 2023, p. 9968](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9968&annotation=SNK3K973) “A depiction of the hand-eye calibration problem is shown in Fig. 6. Hand-eye based LiDAR–Camera calibration procedure can be roughly split into three stages:” ([Li et al., 2023, p. 9968](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9969&annotation=QZZPX94B) “Estimation of each sensor’s motion” ([Li et al., 2023, p. 9969](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9969&annotation=8ZY4M8V7) “Estimation of the extrinsic parameter” ([Li et al., 2023, p. 9969](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9969&annotation=F7AKNDBU) “Refinement of extrinsic parameter” ([Li et al., 2023, p. 9969](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9970&annotation=ZTXRXRJ2) “LiDAR motion estimation” ([Li et al., 2023, p. 9970](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9970&annotation=74UF6LW7) “Camera motion estimation” ([Li et al., 2023, p. 9970](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=LQY9K3WC) “Rotation matrix” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=5MTDVVBP) “Angle-axis” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=6WLKEHQE) “Lie algebra” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=I2RSEDTV) “Quaternion” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=56DQZVYG) “Edge alignment” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9971&annotation=YKSPCZKN) “Intensity matching” ([Li et al., 2023, p. 9971](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9972&annotation=VCWNG55P) “Depth matching” ([Li et al., 2023, p. 9972](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9972&annotation=B33ZFGCL) “Color matching” ([Li et al., 2023, p. 9972](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9972&annotation=N27UGA6Y) “3D–2D point matching” ([Li et al., 2023, p. 9972](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9972&annotation=PE2T3H8K) “3.3.2 3D structure estimation based methods Another way for LiDAR–camera calibration based on motion information is to estimate the 3D structure of the surrounding environment from images, one of the most commonly used methods is structure from motion (SfM) (Ullman 1979). SfM is a technique to estimate the 3D structure of a scene from 2D image sequences, that has been applied in many occasions, such as 3D modeling, augmented reality, visual SLAM, etc. 3D structure estimation based approaches use SfM to generate 3D point clouds from a set of images recorded by the camera on the moving vehicle, which converts the LiDAR–camera calibration problem into a registration task in the 3D domain. Swart et al. (2011) described an approach to register panoramic images and LiDAR point clouds. They generate a sparse 3D point cloud from images and match it to a dense 3D point cloud from LiDAR using a non-rigid ICP process. The results were then polished by adding SIFT interest points corresponding to the framework. Moussa et al. (2012) proposed a bundle block adjustment method to determine the accurate 3D–3D correspondences. Corsini et al. (2012) divided the calibration into coarse and fine-grained alignment procedures. After obtaining the intermediate results by applying the ICP algorithm to the LiDAR generated point clouds, they use a global refinement method based on mutual information to improve the accuracy of the fine 2D–3D alignment. Wang et al. (2018) used sequential scene information from the vehicle motion to obtain the initial extrinsic parameter. The method uses the SfM algorithm to calculate 3D points from 2D image sequences, and registers the SfM points with LiDAR points through the ICP algorithm to estimate the primary result. Then by projecting the 3D LiDAR points to the 2D image plane, they use feature points of edges with a combined optimization method to further promote the accuracy of the extrinsic parameter.” ([Li et al., 2023, p. 9972](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/structureEstimation

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9973&annotation=P8CYI65A) “Table 3 Summary of hand-eye based methods” ([Li et al., 2023, p. 9973](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/handeye  
#important

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9974&annotation=PCWWFGIT) “However, the ICP algorithm may fail when the density of SfM cloud points is very different from the LiDAR ones. To address this challenge, Li et al. (2018) designed an automatic registration method based on semantic features extracted from panoramic images and point clouds. They use GPS and IMU aiding the SfM algorithm to obtain rotation parameters, then extract parked vehicles from two modalities to estimate translation parameters by maximizing the overlapping area of corresponding target pairs. Nagy et al. (2019a) proposed an extrinsic calibration method with an object-level registration. First, they use SfM to generate point clouds from consecutive camera images that can be used for alignment and registration, then they introduce a target-level alignment between the generated and the LiDAR point clouds base on object detection results. Nagy et al. (2019b) introduced similar work and used semantic information in the point clouds registration stage. Later, Nagy and Benedek (2020) made an extension to their previous work mainly in terms of optimization for the registration stage. They manage to diminish the registration error using the point-level ICP method after the object-level registration step, then they introduce a curvebased non-rigid point cloud registration refinement step build on the non-uniform rational basis spline approximation.” ([Li et al., 2023, p. 9974](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/structureEstimation

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9974&annotation=NU8CTK4B) “3.3.3 Other methods Besides generating 3D point clouds through the motion trajectory of the sensors and recovering 3D structures from image sequences, there are alternative ideas of motion based methods to solve the LiDAR–camera calibration problem. Bileschi (2009) made an early attempt to associate video streams with LiDAR data from a moving vehicle. The initial calibration parameter is obtained with the help of the IMU motion signal and then is refined by matching 2D and 3D contours in camera images and LiDAR point clouds. Chien et al. (2016) developed a LiDAR–engaged visual odometry framework and embed the ego-motion estimation problem into LiDAR–camera calibration. Their idea is based on the idea that the performance of the estimated ego-motion is directly related to the quality of extrinsic parameters. Specifically, if the extrinsic parameter deviates far from the ground truth, then the ego-motion estimation would also lose effectiveness. Combining the ego-motion estimation problem with LiDAR–camera calibration will form a bi-level optimization structure, this method introduces data constraints such as intensity and discontinuity restrictions to solve such a problem. Under the Gaussian noise assumption, Huang and Stachniss (2017) applied the GaussHelmert model to multi-sensor extrinsic calibration. With constraints between the motions of the individual sensors given, they jointly optimize the extrinsic parameter and reduce the pose observation error using the Gauss-Helmert paradigm. Castorena et al. (2020) proposed a motion-guided method for automatic calibration of the two multi-modal sensors. With a sequence of time-synchronized point clouds from LiDAR and the corresponding images from the camera, they compute the motion vector for each modality independently, then estimated the extrinsic parameter. When using sensor movement information for extrinsic calibration, the motion must satisfy constraints such as moving in all directions and rotating around all the axes. If the sensors are mounted on a mobile robot performing planar motions, some parameters are rendered as unobservable. Zuniga-Noel et al. (2019) estimated the extrinsic parameter of multiple heterogeneous sensors mounted on a mobile robot subjected to such movements. The method computes the 2D parameters (x, y, yaw) from sensors’ incremental motions, and used the observation of the ground plane to estimate the remaining 3 parameters (z, pitch, roll). Horn et al. (2021) used dual quaternions (DQs) to represent translation and rotation with fewer parameters. Based on DQs, they confine the optimization to planar calibration only, and combine a fast local and a global optimization approach for estimating the result.” ([Li et al., 2023, p. 9974](zotero://select/library/items/PS2ECS24)) #autocalib/method/egoMotion/otherMethods

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9975&annotation=KZBPUYET) “3.4 Learning based methods” ([Li et al., 2023, p. 9975](zotero://select/library/items/PS2ECS24)) #autocalib/method/learningBased  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9975&annotation=XCZBSIQ9) “3.4.1 End‐to‐end methods” ([Li et al., 2023, p. 9975](zotero://select/library/items/PS2ECS24)) #autocalib/method/learningBased/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9977&annotation=NACTZAUP) “3.4.2 Hybrid‐learning methods” ([Li et al., 2023, p. 9977](zotero://select/library/items/PS2ECS24)) #autocalib/method/learningBased/algorithms  
#ReferPaper

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9978&annotation=W8M6HCY7) “4 Discussion” ([Li et al., 2023, p. 9978](zotero://select/library/items/PS2ECS24)) #important  
#autocalib/method  
#review

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9980&annotation=QEN2RNJQ) “Table 4 Comparison of automatic targetless LiDAR–camera calibration methods” ([Li et al., 2023, p. 9980](zotero://select/library/items/PS2ECS24)) #ReferPaper  
#important  
#review  
#autocalib/method

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9980&annotation=T68JSMTZ) “Strength” ([Li et al., 2023, p. 9980](zotero://select/library/items/PS2ECS24))

[Go to annotation](zotero://open-pdf/library/items/S5XEU9H6?page=9980&annotation=C93Q9VH4) “Problem” ([Li et al., 2023, p. 9980](zotero://select/library/items/PS2ECS24))