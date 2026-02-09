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

# 2. Top Surveys
#### Camera, LiDAR, and IMU Spatiotemporal Calibration: Methodological Review and Research Perspectives [[lyuCameraLiDARIMU2025]] - 2025

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
# 3. Taxonomy #taxonomy 

# 4. Papers
*Note: *
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