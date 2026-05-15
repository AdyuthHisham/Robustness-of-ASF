# March 23
1. Check diversity of dataset
	1. NDS is not the only thing you gotta give a shit about. The weather, lighting, road type, probability map of classes
	2. Fancier models like [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^96c779|MV2D]] have multiple moving parts,
	3. making it prone to breaking at ADAS levels 3 or higher.
	4. Also harder to add new modules.
	5. Loss of data cuz high level fusion.
2. Selected models
	1. [[Literature Review - Automatic Multi-Sensor Calibration and Unified Perception#^96c779|MV2D]]
	2. BEVFusion
	3.  [Availability-aware Sensor Fusion<br>via Unified Canonical Space](https://github.com/kaist-avelab/K-Radar)
3. ToDo Next week:
	1. BevSensor Map for object
		1. For each object identify which sensors are used for object detection
			1. Apparently KRADAR did something for this
	2. Deploy models to cluster
		1. BEVFusion first
	3. Raw data quality analysis
		1. Get a metric of raw data goodness
	4. After everything is working: Robust testing
		1. Wise tests: Choose only scenarios for testing that are useful
		2. Add noise to sensors
		3. Remove sensors
			1. Partially
			2. Completely
# April 02
1. Write down the actual battle plan
2. BEVFusion train the model and use trained model for inference
	1. Use KRADAR for inference
3. For the text categorization check marimo
