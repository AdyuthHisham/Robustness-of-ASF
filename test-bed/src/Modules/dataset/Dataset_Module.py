import marimo

__generated_with = "0.20.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import subprocess

    return (subprocess,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # UV dependencies
    """
    )
    return


@app.cell
def _(subprocess):
    # This uses uv's Jupyter integration
    #! uv add "numpy<2.0.0"
    subprocess.call(["uv", "add", "numpy<2.0.0"])
    #! uv add nuscenes-devkit --quiet
    subprocess.call(["uv", "add", "nuscenes-devkit", "--quiet"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # NuScenes
    """
    )
    return


@app.cell
def _():
    # '%matplotlib ' command supported automatically in marimo
    from nuscenes.nuscenes import NuScenes

    nusc = NuScenes(
        version="v1.0-mini",
        dataroot="/home/adhish/Productivity/AMSCUP/test-bed/src/Datasets/nuscenes",
        verbose=True,
    )
    return (nusc,)


@app.cell
def _(nusc):
    nusc.list_scenes()
    return


@app.cell
def _(nusc):
    my_scene = nusc.scene[0]
    first_sample_token = my_scene["first_sample_token"]
    print(my_scene["description"])
    my_sample = nusc.get("sample", first_sample_token)
    # my_sample
    return (my_sample,)


@app.cell
def _(nusc):
    nusc.sensor
    return


@app.cell
def _(my_sample, nusc):
    nusc.render_pointcloud_in_image(my_sample["token"], pointsensor_channel="LIDAR_TOP")
    return


@app.cell
def _(my_sample, nusc):
    nusc.render_sample_data(
        my_sample["data"]["LIDAR_TOP"], nsweeps=5, underlay_map=True
    )
    nusc.render_sample_data(
        my_sample["data"]["RADAR_FRONT"], nsweeps=5, underlay_map=True
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Render sensor data
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Fun facts:
    - There is 1 LIDAR
    - There are 5 RADAR
    - There are 6 Cameras
    - There is 1 IMU&GPS
    """
    )
    return


@app.cell
def _(nusc):
    # night_cnt = 0
    # rain_cnt = 0
    for scene in nusc.scene:
        if "night" in scene["description"].lower():
            if "rain" in scene["description"].lower():
                adverse_scene = scene
                break
    print(adverse_scene)
    return (adverse_scene,)


@app.cell
def _():
    # Creating a collection of all calibration sensor tokens
    # calib_sens_tokens = []
    return


@app.cell
def _(adverse_sample):
    sensor_names = list(adverse_sample["data"])
    print(sensor_names)
    return (sensor_names,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### LiDAR
    """
    )
    return


@app.cell
def _(adverse_sample, nusc):
    lidar_data_token = adverse_sample["data"]["LIDAR_TOP"]
    # nusc.render_sample_data(lidar_data_token)
    nusc.render_sample_data(lidar_data_token, with_anns=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### RADAR
    """
    )
    return


@app.cell
def _(adverse_sample, nusc, sensor_names):

    for rad_name in sensor_names:
        if rad_name.startswith("RADAR_"):
            radar_data_token = adverse_sample["data"][rad_name]
            nusc.render_sample_data(radar_data_token, with_anns=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Camera
    """
    )
    return


@app.cell
def _(adverse_sample, nusc, sensor_names):

    for cam_name in sensor_names:
        if cam_name.startswith("CAM_"):
            cam_data_token = adverse_sample["data"][cam_name]
            nusc.render_sample_data(cam_data_token, with_anns=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## where teh sensors at?
    """
    )
    return


@app.cell
def _(adverse_scene, nusc):
    # Get a sample from a scene
    adverse_sample_token = adverse_scene["first_sample_token"]
    adverse_sample = nusc.get("sample", adverse_sample_token)

    sensor_translations = []

    # Go through all sensors in the sample
    for sensor_name, sample_data_token in adverse_sample["data"].items():
        # print(sensor_name)

        # Get sample_data dict
        sample_data = nusc.get("sample_data", sample_data_token)

        # Get calibrated_sensor dict
        calib_sensor = nusc.get(
            "calibrated_sensor", sample_data["calibrated_sensor_token"]
        )

        # Append as a dictionary
        sensor_translations.append(
            {
                "sensor": sensor_name,
                "translation": calib_sensor["translation"],
                "rotation": calib_sensor["rotation"],
            }
        )

    # Show results
    for s in sensor_translations:
        print(s)
    return adverse_sample, sensor_translations


@app.cell
def _(sensor_translations):

    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 8))

    # Plot each sensor
    for sensor in sensor_translations:
        x, y, _ = sensor["translation"]  # take x and y, ignore z
        plt.scatter(x, y, s=100)  # s=100 → marker size
        plt.text(x + 0.05, y + 0.05, sensor["sensor"], fontsize=9)

    # Draw vehicle center
    plt.scatter(0, 0, color="black", marker="x", s=100, label="Vehicle Center")

    plt.xlabel("X (meters)")
    plt.ylabel("Y (meters)")
    plt.title("Birds-Eye View of Sensors")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")  # equal scale for x and y
    plt.show()

    # Add coverage map
    return


@app.cell
def _(nusc):
    nusc.visibility
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Sensor identification
    - [ ] What annotation are there in the scene and how many
        - [ ] What weather etc
        - [ ] What is being identified: Make a list of top keywords from descriptions
    - [x] What sensors are being used

    - [ ] Instance based: How long can everything keep track of it
    - [ ] How much visibility (cameras) / points in bounding box (radar & lidar)
    - [ ] Verbosity - Show renders or not
    - [ ] CPU parallelization
    - [ ] Save as something
    """
    )
    return


@app.cell
def _():
    from example.sample import hello

    return (hello,)


@app.cell
def _(hello):
    hello(5, 7)
    return


@app.cell
def _(nusc):
    sample = nusc.sample[50]
    our_scene = nusc.get("scene", sample["scene_token"])
    print(our_scene["description"])
    verbosity = False
    ann_token = sample["anns"][12]  # pick any annotation
    ann = nusc.get("sample_annotation", ann_token)
    ann
    print("hello")
    print(f"Object {ann['instance_token']} ({ann['category_name']})")
    return ann, ann_token, sample, verbosity


@app.cell
def _(ann_token, nusc, sample, verbosity):
    camera_names = [
        "CAM_FRONT",
        "CAM_FRONT_LEFT",
        "CAM_FRONT_RIGHT",
        "CAM_BACK",
        "CAM_BACK_LEFT",
        "CAM_BACK_RIGHT",
    ]

    print("Cameras that see this object:")
    for cam_name_t in camera_names:
        cam_token = sample["data"][cam_name_t]
        data_path, boxes, camera_intrinsic = nusc.get_sample_data(
            cam_token, selected_anntokens=[ann_token]
        )
        if len(boxes) > 0:  # box was successfully projected into this camera's FOV
            print(f"  → {cam_name_t} (visible in this image)")
            if verbosity:
                test_cam_data_token = sample["data"][cam_name_t]
                nusc.render_sample_data(test_cam_data_token, with_anns=True)
    return


@app.cell(hide_code=True)
def _(nusc):
    from nuscenes.utils.geometry_utils import transform_matrix
    from pyquaternion import Quaternion
    import numpy as np
    from nuscenes.utils.data_classes import (
        PointCloud,
    )  # base class (works for both LidarPointCloud and RadarPointCloud)

    def transform_pointcloud_to_global(self, pointsensor: dict, pc: PointCloud):
        """
        Transform a PointCloud (LiDAR or Radar) from its sensor frame to the global frame.

        Parameters
        ----------
        pointsensor : dict
            The record from nusc.get('sample_data', token) for the point sensor
            (must contain 'calibrated_sensor_token' and 'ego_pose_token').
        pc : PointCloud
            The point cloud object (LidarPointCloud or RadarPointCloud).

        Returns
        -------
        pc : PointCloud
            The point cloud transformed **in-place** to global coordinates.
        sensor_to_global : np.ndarray (4x4)
            The final homogeneous transformation matrix (sensor → global).
        """

        # Step 1: Transform from sensor frame → ego vehicle frame
        cs_record = nusc.get(
            "calibrated_sensor", pointsensor["calibrated_sensor_token"]
        )

        # Use built-in helper for cleaner & safer transformation
        sensor_to_ego = transform_matrix(
            cs_record["translation"], Quaternion(cs_record["rotation"]), inverse=False
        )

        # Apply rotation then translation (matches original order)
        pc.rotate(Quaternion(cs_record["rotation"]).rotation_matrix)
        pc.translate(np.array(cs_record["translation"]))

        # Step 2: Transform from ego vehicle frame → global frame
        pose_record = nusc.get("ego_pose", pointsensor["ego_pose_token"])

        ego_to_global = transform_matrix(
            pose_record["translation"],
            Quaternion(pose_record["rotation"]),
            inverse=False,
        )

        # Apply rotation then translation
        pc.rotate(Quaternion(pose_record["rotation"]).rotation_matrix)
        pc.translate(np.array(pose_record["translation"]))

        # Final combined matrix: sensor → global
        sensor_to_global = ego_to_global @ sensor_to_ego

        return pc, sensor_to_global

    return np, transform_pointcloud_to_global


@app.cell(hide_code=True)
def _():
    # import os
    # import numpy as np
    # from nuscenes.utils.data_classes import RadarPointCloud
    # from nuscenes.utils.geometry_utils import points_in_box, BoxVisibility   # ← ADD THIS LINE
    # from pyquaternion import Quaternion

    # # Get the 3D bounding box object (in GLOBAL coordinates)
    # box = nusc.get_box(ann['token'])

    # radar_names = ['RADAR_FRONT', 'RADAR_FRONT_LEFT', 'RADAR_FRONT_RIGHT',
    #                'RADAR_BACK_LEFT', 'RADAR_BACK_RIGHT']

    # print(f"  Total radar points (summed): {ann['num_radar_pts']}")

    # for radar_name in radar_names:
    #     radar_token = sample['data'][radar_name]
    #     # 2. Get the full record for this radar capture
    #     sd_rec = nusc.get('sample_data', radar_token)

    #     # Load raw radar points
    #     pcl_path = os.path.join(nusc.dataroot, sd_rec['filename'])
    #     pc = RadarPointCloud.from_file(pcl_path)

    #     # Transform points from sensor frame → global frame
    #     cs_rec   = nusc.get('calibrated_sensor', sd_rec['calibrated_sensor_token'])
    #     pose_rec = nusc.get('ego_pose', sd_rec['ego_pose_token'])

    #     points = pc.points[:3, :]                    # only x,y,z  → shape (3, N)
    #     points = np.vstack((points, np.ones(points.shape[1])))  # make homogeneous

    #     # Sensor → ego
    #     sensor_to_ego = np.eye(4)
    #     sensor_to_ego[:3, :3] = Quaternion(cs_rec['rotation']).rotation_matrix
    #     sensor_to_ego[:3, 3]  = cs_rec['translation']
    #     points_ego = sensor_to_ego @ points

    #     # Ego → global
    #     ego_to_global = np.eye(4)
    #     ego_to_global[:3, :3] = Quaternion(pose_rec['rotation']).rotation_matrix
    #     ego_to_global[:3, 3]  = pose_rec['translation']
    #     points_global = ego_to_global @ points_ego   # shape (4, N)

    #     # Count how many fall inside the 3D box
    #     inside = points_in_box(box, points_global[:3, :])   # ← FIXED LINE
    #     count = int(np.sum(inside))

    #     if count > 0:
    #         print(f"  → {radar_name}: {count} points")
    #         if verbosity == True:
    #             test_radar_data_token = adverse_sample["data"][radar_name]
    #             nusc.render_sample_data(test_radar_data_token, with_anns=True)
    return


@app.cell(hide_code=True)
def _():
    # from nuscenes.utils.data_classes import LidarPointCloud

    # print(f"Object: {ann['instance_token']} | Category: {ann['category_name']}")
    # print(f"Ground-truth num_lidar_pts (from annotation): {ann['num_lidar_pts']}\n")

    # # Get the 3D box in global coordinates
    # ann_box = nusc.get_box(ann['token'])          # renamed from 'box'

    # # LiDAR sensor setup
    # lidar_channel = 'LIDAR_TOP'
    # test_lidar_data_token = sample['data'][lidar_channel]
    # lidar_sd_rec = nusc.get('sample_data', test_lidar_data_token)   # renamed from 'sd_rec'

    # # Load raw LiDAR point cloud
    # lidar_pcl_path = os.path.join(nusc.dataroot, lidar_sd_rec['filename'])
    # lidar_pc = LidarPointCloud.from_file(lidar_pcl_path)       # renamed from 'pc'

    # # Transform points from sensor frame → global frame
    # lidar_calib = nusc.get('calibrated_sensor', lidar_sd_rec['calibrated_sensor_token'])
    # ego_pose_rec = nusc.get('ego_pose', lidar_sd_rec['ego_pose_token'])   # renamed

    # # Extract x, y, z and make homogeneous
    # lidar_points = lidar_pc.points[:3, :].copy()                    # renamed from 'points'
    # lidar_points_hom = np.vstack((lidar_points, np.ones(lidar_points.shape[1])))

    # # 1. Sensor → Ego vehicle frame
    # sensor_to_ego_mat = np.eye(4)
    # sensor_to_ego_mat[:3, :3] = Quaternion(lidar_calib['rotation']).rotation_matrix
    # sensor_to_ego_mat[:3, 3] = lidar_calib['translation']
    # lidar_points_ego = sensor_to_ego_mat @ lidar_points_hom         # renamed

    # # 2. Ego → Global frame
    # ego_to_global_mat = np.eye(4)
    # ego_to_global_mat[:3, :3] = Quaternion(ego_pose_rec['rotation']).rotation_matrix
    # ego_to_global_mat[:3, 3] = ego_pose_rec['translation']
    # lidar_points_global = ego_to_global_mat @ lidar_points_ego      # renamed

    # # Count how many points fall inside the 3D box
    # points_inside_box = points_in_box(ann_box, lidar_points_global[:3, :])   # renamed
    # lidar_point_count = int(np.sum(points_inside_box))                       # renamed from 'count'

    # print(f"→ {lidar_channel}: {lidar_point_count} points inside the box")

    # # Compare with official annotation count
    # if lidar_point_count != ann['num_lidar_pts']:
    #     print(f"   (Note: Official annotation reports {ann['num_lidar_pts']} points — "
    #           f"small difference may occur due to precision)")

    #     # Optional: Render the LiDAR view with annotations for visual check
    #     if verbosity == True:
    #         nusc.render_sample_data(test_lidar_data_token,
    #                                 box_vis_level=BoxVisibility.ANY,
    #                                 with_anns=True)
    return


@app.cell
def _(ann, np, nusc, sample, transform_pointcloud_to_global, verbosity):
    import os
    from nuscenes.utils.data_classes import LidarPointCloud, RadarPointCloud
    from nuscenes.utils.geometry_utils import points_in_box, BoxVisibility

    # ====================== HELPER FUNCTION (defined above) ======================

    print(f"Object: {ann['instance_token']} | Category: {ann['category_name']}")
    print(f"Ground-truth num_lidar_pts: {ann['num_lidar_pts']}")
    print(f"Ground-truth num_radar_pts: {ann['num_radar_pts']}\n")

    # Get the 3D bounding box in global coordinates
    ann_box = nusc.get_box(ann["token"])

    # ==================== RADAR COUNTING ====================
    print("=== Radar Point Counts ===")
    radar_names = [
        "RADAR_FRONT",
        "RADAR_FRONT_LEFT",
        "RADAR_FRONT_RIGHT",
        "RADAR_BACK_LEFT",
        "RADAR_BACK_RIGHT",
    ]

    for radar_name in radar_names:
        radar_token = sample["data"][radar_name]
        sd_rec = nusc.get("sample_data", radar_token)

        # Load radar point cloud
        pcl_path = os.path.join(nusc.dataroot, sd_rec["filename"])
        pc = RadarPointCloud.from_file(pcl_path)

        # Transform to global using the helper function
        pc, sensor_to_global = transform_pointcloud_to_global(nusc, sd_rec, pc)

        # Extract x,y,z (after transformation, pc.points is now in global frame)
        radar_points = pc.points[:3, :].copy()

        # Count points inside the box
        inside = points_in_box(ann_box, radar_points)
        radar_count = int(np.sum(inside))

        if radar_count > 0:
            print(f" → {radar_name}: {radar_count} radar points")

            # Optional rendering
            if "verbosity" in locals() and verbosity is True:
                nusc.render_sample_data(radar_token, with_anns=True)

    # ==================== LIDAR COUNTING ====================
    print("\n=== LiDAR Point Count ===")
    lidar_channel = "LIDAR_TOP"
    lidar_token = sample["data"][lidar_channel]
    lidar_sd_rec = nusc.get("sample_data", lidar_token)

    # Load LiDAR point cloud
    lidar_pcl_path = os.path.join(nusc.dataroot, lidar_sd_rec["filename"])
    pc = LidarPointCloud.from_file(lidar_pcl_path)

    # Transform to global using the SAME helper function
    pc, sensor_to_global = transform_pointcloud_to_global(nusc, lidar_sd_rec, pc)

    # Count LiDAR points inside the box
    lidar_points = pc.points[:3, :].copy()
    inside = points_in_box(ann_box, lidar_points)
    lidar_point_count = int(np.sum(inside))

    print(f" → {lidar_channel}: {lidar_point_count} LiDAR points inside the box")

    # Compare with official count
    if lidar_point_count != ann["num_lidar_pts"]:
        print(
            f"   (Note: Official reports {ann['num_lidar_pts']} points — small difference is normal)"
        )

    # Optional rendering for LiDAR
    if "verbosity" in locals() and verbosity is True:
        nusc.render_sample_data(
            lidar_token, box_vis_level=BoxVisibility.ANY, with_anns=True
        )
    return


@app.cell
def _(nusc, sample):
    nusc.render_pointcloud_in_image(
        sample["token"],
        pointsensor_channel="RADAR_FRONT",  # or 'LIDAR_TOP'
        camera_channel="CAM_FRONT_LEFT",
        # render_intensity=True,               # for radar: shows RCS as color
        show_lidarseg=False,
    )
    return


@app.cell
def _(nusc):
    # 2. Extract scene descriptions into Polars DataFrame
    from sklearn.feature_extraction.text import TfidfVectorizer
    import polars as pl

    df = pl.DataFrame(nusc.scene)

    # Keep only non-empty descriptions
    df = df.filter(pl.col("description").is_not_null() & (pl.col("description") != ""))

    scene_descriptions = df["description"].to_list()

    print(f"Loaded {len(scene_descriptions)} descriptions")

    # 3. TF-IDF with n-grams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), stop_words="english", max_features=500, min_df=2, max_df=0.8
    )

    X = vectorizer.fit_transform(scene_descriptions)
    # print(X)
    # 4. Convert result back to Polars DataFrame
    feature_names = vectorizer.get_feature_names_out()

    tfidf_df = pl.DataFrame(X.toarray(), schema=feature_names.tolist())

    print(tfidf_df.head())
    tfidf_df.write_parquet("tfidf.parquet")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### For all scenes
    - Instance token
    - Visibility
    - No. of lidar points
    - No. of radar points
    - Camera visibility (unfortunately tis all cameras)
    - Which Lidar (I mean....)
    - Which camera
    - Which radar
    - Annotation name
    - Location
    - Add a bigger bounding box (x % such as 5-10% extra )
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### For all scenes
    - What is the most common terms for each scene
    - They are all comma seperated
    - Get list after TV-something and ask chatgpt to categorize based on metadata such as road_type, weather, crowdedness, time_of_day
    """
    )
    return


@app.cell
def _():
    # from sklearn.feature_extraction.text import TfidfVectorizer
    # from sklearn.preprocessing import normalize
    # from scipy.sparse import csr_matrix
    # import polars as pl

    # # =================== EXTRACT SCENE DESCRIPTIONS ===================
    # df = pl.DataFrame(nusc.scene)
    # df = df.filter(pl.col("description").is_not_null() & (pl.col("description") != ""))

    # scene_tokens = df["token"].to_list()
    # scene_descriptions = df["description"].to_list()

    # print(f"Loaded {len(scene_descriptions)} descriptions")

    # # =================== COMPUTE TF-IDF (SPARSE) ===================
    # vectorizer = TfidfVectorizer(
    #     ngram_range=(1, 2),
    #     stop_words='english',
    #     max_features=500,
    #     min_df=2,
    #     max_df=0.8
    # )

    # X = vectorizer.fit_transform(scene_descriptions)  # sparse CSR
    # feature_names = vectorizer.get_feature_names_out().tolist()
    # print(f"TF-IDF matrix shape: {X.shape}, type: {type(X)}")

    # # =================== NORMALIZE FEATURES ===================
    # # Each feature column is a vector of TF-IDF values across scenes
    # X_norm = normalize(X.T, axis=1)  # shape: (num_features, num_scenes)

    # # =================== COMPUTE COSINE SIMILARITY ===================
    # # Cosine similarity = dot product of normalized sparse vectors
    # # This gives values between 0 and 1 (positive similarity)
    # cos_sim = X_norm @ X_norm.T  # shape: (num_features, num_features)

    # # Convert sparse matrix to dense temporarily to extract top correlations
    # cos_sim_dense = cos_sim.toarray()

    # # =================== FIND TOP POSITIVE AND NEGATIVE CORRELATIONS ===================
    # top_n = 5
    # feature_corr_dict = {}

    # for idx, feature in enumerate(feature_names):
    #     sims = cos_sim_dense[idx].copy()
    #     sims[idx] = 0  # ignore self-similarity

    #     # Top positive: largest cosine similarity
    #     pos_idx = np.argsort(-sims)[:top_n]
    #     pos_features = [(feature_names[i], sims[i]) for i in pos_idx]

    #     # Top negative: smallest cosine similarity
    #     neg_idx = np.argsort(sims)[:top_n]
    #     neg_features = [(feature_names[i], sims[i]) for i in neg_idx]

    #     feature_corr_dict[feature] = {
    #         "top_positive": pos_features,
    #         "top_negative": neg_features
    #     }

    # # =================== EXAMPLE OUTPUT ===================
    # for feature, corr_info in list(feature_corr_dict.items())[:5]:
    #     print(f"\nFeature: {feature}")
    #     print(" Top positive correlations:", corr_info["top_positive"])
    #     print(" Top negative correlations:", corr_info["top_negative"])
    return


@app.cell
def _():
    # import numpy as np
    # from collections import defaultdict, Counter
    # from sentence_transformers import SentenceTransformer
    # from sklearn.preprocessing import StandardScaler
    # from sklearn.feature_extraction.text import TfidfVectorizer
    # import umap
    # import hdbscan
    # import json

    # # -----------------------------
    # # CATEGORY MAPPING
    # # -----------------------------
    # def map_to_high_level(category_name):
    #     """
    #     Maps nuScenes categories into structured semantic groups.
    #     """

    #     # -------------------------
    #     # HEAVY VEHICLES
    #     # -------------------------
    #     heavy_vehicles = [
    #         "vehicle.truck",
    #         "vehicle.trailer",
    #         "vehicle.bus.rigid",
    #         "vehicle.bus.bendy"
    #     ]

    #     # -------------------------
    #     # LIGHT VEHICLES
    #     # -------------------------
    #     light_vehicles = [
    #         "vehicle.car",
    #         "vehicle.motorcycle",
    #         "vehicle.bicycle"
    #     ]

    #     # -------------------------
    #     # EMERGENCY + CONSTRUCTION
    #     # -------------------------
    #     emergency_construction = [
    #         "vehicle.emergency.police",
    #         "vehicle.emergency.ambulance",
    #         "vehicle.construction"
    #     ]

    #     # -------------------------
    #     # HUMAN
    #     # -------------------------
    #     if category_name.startswith("human"):
    #         return "pedestrian"

    #     # -------------------------
    #     # ANIMAL
    #     # -------------------------
    #     if category_name.startswith("animal"):
    #         return "animal"

    #     # -------------------------
    #     # STATIC OBJECT
    #     # -------------------------
    #     if category_name.startswith("static_object"):
    #         return "static"

    #     # -------------------------
    #     # MOVABLE OBJECT
    #     # -------------------------
    #     if category_name.startswith("movable_object"):
    #         return "movable"

    #     # -------------------------
    #     # VEHICLE GROUPING
    #     # -------------------------
    #     if category_name in heavy_vehicles:
    #         return "heavy_vehicle"

    #     if category_name in light_vehicles:
    #         return "light_vehicle"

    #     if category_name in emergency_construction:
    #         return "emergency_construction"

    #     return "other"

    # # -----------------------------
    # # SAMPLE PROCESSING
    # # -----------------------------
    # def process_sample(sample):
    #     """
    #     sample should contain:
    #     - annotations: list of dicts with 'category_name'
    #     """

    #     categories = [ann["category_name"] for ann in sample["annotations"]]
    #     high_level = [map_to_high_level(c) for c in categories]

    #     counter = Counter(high_level)

    #     # Combine all vehicle-related categories
    #     num_vehicles = (
    #         counter["heavy_vehicle"]
    #         + counter["light_vehicle"]
    #         + counter["emergency_construction"]
    #     )

    #     num_pedestrians = counter["pedestrian"]
    #     total_objects = len(categories)
    #     diversity = len(set(high_level))

    #     # Description string
    #     description = (
    #         f"{num_vehicles} vehicles, "
    #         f"{num_pedestrians} pedestrians, "
    #         f"{total_objects} objects"
    #     )

    #     return {
    #         "description": description,
    #         "num_vehicles": num_vehicles,
    #         "num_pedestrians": num_pedestrians,
    #         "total_objects": total_objects,
    #         "diversity": diversity,
    #         "high_level_counts": counter
    #     }

    # # -----------------------------
    # # SCENE AGGREGATION
    # # -----------------------------
    # def aggregate_scene(scene_samples, sample_embeddings):
    #     embeddings = np.array(sample_embeddings)

    #     mean_emb = np.mean(embeddings, axis=0)
    #     var_emb = np.var(embeddings, axis=0)

    #     avg_vehicles = np.mean([s["num_vehicles"] for s in scene_samples])
    #     avg_pedestrians = np.mean([s["num_pedestrians"] for s in scene_samples])
    #     avg_objects = np.mean([s["total_objects"] for s in scene_samples])
    #     avg_diversity = np.mean([s["diversity"] for s in scene_samples])

    #     return {
    #         "embedding": np.concatenate([mean_emb, var_emb]),
    #         "avg_vehicles": avg_vehicles,
    #         "avg_pedestrians": avg_pedestrians,
    #         "avg_objects": avg_objects,
    #         "diversity": avg_diversity
    #     }

    # # -----------------------------
    # # MAIN PIPELINE
    # # -----------------------------
    # def run_pipeline(dataset):
    #     """
    #     dataset format:
    #     [
    #         {
    #             "scene_id": str,
    #             "samples": [
    #                 {
    #                     "annotations": [
    #                         {"category_name": "..."}
    #                     ]
    #                 }
    #             ]
    #         }
    #     ]
    #     """

    #     model = SentenceTransformer("all-MiniLM-L6-v2")

    #     all_scene_embeddings = []
    #     scene_ids = []
    #     scene_data = {}
    #     sample_data = []

    #     # -----------------------------
    #     # STEP 1: Process samples + embeddings
    #     # -----------------------------
    #     for scene in dataset:
    #         scene_id = scene["scene_id"]
    #         samples = scene["samples"]

    #         processed_samples = []
    #         descriptions = []

    #         for sample in samples:
    #             processed = process_sample(sample)
    #             processed_samples.append(processed)
    #             descriptions.append(processed["description"])

    #         # Embed descriptions
    #         embeddings = model.encode(descriptions)

    #         # Aggregate scene
    #         scene_features = aggregate_scene(processed_samples, embeddings)

    #         scene_data[scene_id] = {
    #             "samples": processed_samples,
    #             "embedding": scene_features["embedding"],
    #             "avg_vehicles": scene_features["avg_vehicles"],
    #             "avg_pedestrians": scene_features["avg_pedestrians"],
    #             "avg_objects": scene_features["avg_objects"],
    #             "diversity": scene_features["diversity"],
    #             "descriptions": descriptions
    #         }

    #         all_scene_embeddings.append(scene_features["embedding"])
    #         scene_ids.append(scene_id)

    #     all_scene_embeddings = np.array(all_scene_embeddings)

    #     # -----------------------------
    #     # STEP 2: Normalize features
    #     # -----------------------------
    #     scaler = StandardScaler()
    #     all_scene_embeddings = scaler.fit_transform(all_scene_embeddings)

    #     # -----------------------------
    #     # STEP 3: UMAP
    #     # -----------------------------
    #     reducer = umap.UMAP(n_components=10)
    #     reduced_embeddings = reducer.fit_transform(all_scene_embeddings)

    #     # -----------------------------
    #     # STEP 4: HDBSCAN clustering
    #     # -----------------------------
    #     clusterer = hdbscan.HDBSCAN(min_cluster_size=10, prediction_data=True)
    #     cluster_labels = clusterer.fit_predict(reduced_embeddings)
    #     cluster_probs = clusterer.probabilities_

    #     # -----------------------------
    #     # STEP 5: Assign cluster info
    #     # -----------------------------
    #     for i, scene_id in enumerate(scene_ids):
    #         scene_data[scene_id]["cluster_id"] = int(cluster_labels[i])
    #         scene_data[scene_id]["cluster_probability"] = float(cluster_probs[i])

    #     # -----------------------------
    #     # STEP 6: Cluster grouping
    #     # -----------------------------
    #     clusters = defaultdict(list)

    #     for scene_id in scene_ids:
    #         cid = scene_data[scene_id]["cluster_id"]
    #         clusters[cid].append(scene_id)

    #     # -----------------------------
    #     # STEP 7: Cluster centroids
    #     # -----------------------------
    #     cluster_centroids = {}

    #     for cid, sids in clusters.items():
    #         emb = np.array([scene_data[s]["embedding"] for s in sids])
    #         cluster_centroids[cid] = np.mean(emb, axis=0)

    #     # -----------------------------
    #     # STEP 8: Cluster keywords (TF-IDF)
    #     # -----------------------------
    #     cluster_keywords = {}

    #     for cid, sids in clusters.items():
    #         texts = []
    #         for sid in sids:
    #             texts.extend(scene_data[sid]["descriptions"])

    #         if len(texts) == 0:
    #             continue

    #         vectorizer = TfidfVectorizer(max_features=20)
    #         X = vectorizer.fit_transform(texts)

    #         scores = np.mean(X.toarray(), axis=0)
    #         words = vectorizer.get_feature_names_out()

    #         top_words = [words[i] for i in scores.argsort()[-5:]]
    #         cluster_keywords[cid] = top_words

    #     # -----------------------------
    #     # STEP 9: Sample-level outputs
    #     # -----------------------------
    #     for scene_id in scene_ids:
    #         cid = scene_data[scene_id]["cluster_id"]
    #         prob = scene_data[scene_id]["cluster_probability"]

    #         for desc in scene_data[scene_id]["descriptions"]:
    #             words = desc.split()[:5]

    #             sample_data.append({
    #                 "scene_id": scene_id,
    #                 "cluster_id": cid,
    #                 "cluster_probability": prob,
    #                 "top_words": words
    #             })

    #     # -----------------------------
    #     # FINAL OUTPUT
    #     # -----------------------------
    #     output = {
    #         "global": {
    #             "clusters": {
    #                 int(cid): {
    #                     "size": len(sids),
    #                     "keywords": cluster_keywords.get(cid, []),
    #                     "centroid": cluster_centroids[cid].tolist()
    #                 }
    #                 for cid, sids in clusters.items()
    #             }
    #         },
    #         "scenes": scene_data,
    #         "samples": sample_data
    #     }

    #     return output

    # # -----------------------------
    # # RUN (example)
    # # -----------------------------
    # if __name__ == "__main__":
    #     # Replace with real nuScenes parsing
    #     dummy_dataset = [
    #         {
    #             "scene_id": "scene_1",
    #             "samples": [
    #                 {"annotations": [{"category_name": "vehicle.car"}, {"category_name": "human.pedestrian"}]},
    #                 {"annotations": [{"category_name": "vehicle.truck"}]}
    #             ]
    #         }
    #     ]

    #     results = run_pipeline(dummy_dataset)

    #     with open("output.json", "w") as f:
    #         json.dump(results, f, indent=2)

    #     print("Pipeline complete. Results saved to output.json")
    return


@app.cell
def _():
    # import numpy as np
    # from collections import defaultdict, Counter
    # from sentence_transformers import SentenceTransformer
    # from sklearn.preprocessing import StandardScaler
    # from sklearn.feature_extraction.text import TfidfVectorizer
    # from sklearn.metrics.pairwise import cosine_distances
    # from nuscenes.nuscenes import NuScenes
    # import umap
    # import hdbscan
    # import json
    # import pandas as pd
    # import argparse
    # import os

    # # -----------------------------
    # # CATEGORY KEYS
    # # -----------------------------

    # CATEGORY_KEYS = [
    #     "heavy_vehicle",
    #     "light_vehicle",
    #     "emergency_construction",
    #     "pedestrian",
    #     "animal",
    #     "static",
    #     "movable",
    #     "other",
    # ]

    # # -----------------------------
    # # CATEGORY MAPPING
    # # -----------------------------

    # def map_to_high_level(category_name: str) -> str:
    #     heavy_vehicles         = {"vehicle.truck", "vehicle.trailer", "vehicle.bus.rigid", "vehicle.bus.bendy"}
    #     light_vehicles         = {"vehicle.car", "vehicle.motorcycle", "vehicle.bicycle"}
    #     emergency_construction = {"vehicle.emergency.police", "vehicle.emergency.ambulance", "vehicle.construction"}

    #     if category_name.startswith("human"):          return "pedestrian"
    #     if category_name.startswith("animal"):         return "animal"
    #     if category_name.startswith("static_object"):  return "static"
    #     if category_name.startswith("movable_object"): return "movable"
    #     if category_name in heavy_vehicles:            return "heavy_vehicle"
    #     if category_name in light_vehicles:            return "light_vehicle"
    #     if category_name in emergency_construction:    return "emergency_construction"
    #     return "other"

    # # -----------------------------
    # # NUSCENES DATASET LOADER
    # # -----------------------------

    # def load_nuscenes_dataset(nusc: NuScenes) -> list[dict]:
    #     """
    #     Converts a NuScenes instance into the pipeline's expected format:

    #     [
    #       {
    #         "scene_id":   str,           # scene["token"]
    #         "description": str,          # scene["description"]
    #         "samples": [
    #           {
    #             "sample_token": str,
    #             "annotations": [{"category_name": str}]
    #           }
    #         ]
    #       }
    #     ]

    #     NuScenes scene → sample chain
    #     ─────────────────────────────
    #     scene["first_sample_token"]
    #       └─ sample["next"]  (repeat until empty string)
    #            └─ sample["anns"]  →  sample_annotation["category_name"]
    #     """
    #     dataset = []

    #     for scene in nusc.scene:
    #         samples = []

    #         sample_token = scene["first_sample_token"]

    #         while sample_token:
    #             sample_record = nusc.get("sample", sample_token)

    #             annotations = [
    #                 {"category_name": nusc.get("sample_annotation", ann_token)["category_name"]}
    #                 for ann_token in sample_record["anns"]
    #             ]

    #             samples.append({
    #                 "sample_token": sample_token,
    #                 "annotations":  annotations,
    #             })

    #             sample_token = sample_record["next"]   # empty string at end of scene

    #         dataset.append({
    #             "scene_id":    scene["token"],
    #             "description": scene["description"],   # single nuScenes description per scene
    #             "samples":     samples,
    #         })

    #     return dataset

    # # -----------------------------
    # # CATEGORY DENSITY RATIOS
    # # -----------------------------

    # def compute_density_ratios(high_level_counts: dict, total_objects: int) -> dict[str, float]:
    #     """
    #     Normalises raw category counts by the total number of objects,
    #     producing a composition profile invariant to scene size.

    #     Example
    #     -------
    #     10 objects: 6 light_vehicle, 3 pedestrian, 1 heavy_vehicle
    #     → {"light_vehicle": 0.6, "pedestrian": 0.3, "heavy_vehicle": 0.1, ...rest 0.0}
    #     """
    #     if total_objects == 0:
    #         return {k: 0.0 for k in CATEGORY_KEYS}

    #     return {
    #         k: round(high_level_counts.get(k, 0) / total_objects, 6)
    #         for k in CATEGORY_KEYS
    #     }

    # # -----------------------------
    # # SAMPLE PROCESSING
    # # -----------------------------

    # def process_sample(sample: dict) -> dict:
    #     """
    #     Structural counts only — no description at sample level in nuScenes.
    #     """
    #     categories = [ann["category_name"] for ann in sample["annotations"]]
    #     high_level = [map_to_high_level(c) for c in categories]
    #     counter    = Counter(high_level)

    #     counts             = {k: counter.get(k, 0) for k in CATEGORY_KEYS}
    #     total              = len(categories)
    #     categorical_vector = np.array([counts[k] for k in CATEGORY_KEYS], dtype=np.float32)
    #     density_ratios     = compute_density_ratios(counts, total)

    #     return {
    #         **{f"num_{k}": counts[k] for k in CATEGORY_KEYS},
    #         "total_objects":      total,
    #         "diversity":          len(set(high_level)),
    #         "high_level_counts":  dict(counter),
    #         "categorical_vector": categorical_vector,
    #         "density_ratios":     density_ratios,
    #     }

    # # -----------------------------
    # # SCENE AGGREGATION
    # # -----------------------------

    # def aggregate_scene(scene_samples: list[dict], scene_embedding: np.ndarray) -> dict:
    #     """
    #     scene_embedding : (sbert_dim,) vector from the nuScenes scene description.
    #     All other statistics are averaged over the scene's samples.
    #     """
    #     mean_categorical = np.mean(
    #         np.stack([s["categorical_vector"] for s in scene_samples]), axis=0
    #     )

    #     avg_density_ratios = {
    #         k: round(float(np.mean([s["density_ratios"][k] for s in scene_samples])), 6)
    #         for k in CATEGORY_KEYS
    #     }

    #     return {
    #         "sbert_embedding":    scene_embedding,
    #         "mean_categorical":   mean_categorical,
    #         "avg_density_ratios": avg_density_ratios,
    #         **{f"avg_{k}": float(np.mean([s[f"num_{k}"] for s in scene_samples]))
    #            for k in CATEGORY_KEYS},
    #         "avg_objects":   float(np.mean([s["total_objects"] for s in scene_samples])),
    #         "avg_diversity": float(np.mean([s["diversity"]     for s in scene_samples])),
    #     }

    # # -----------------------------
    # # DISTANCE-WEIGHTED TF-IDF KEYWORDS
    # # -----------------------------

    # def weighted_tfidf_keywords(
    #     cluster_scene_ids: list[str],
    #     scene_data: dict,
    #     centroid: np.ndarray,
    #     top_n: int = 5,
    #     max_features: int = 50,
    # ) -> list[str]:
    #     """
    #     Collects the nuScenes description for each scene in the cluster,
    #     weights it by exp(-cosine_distance_to_centroid), and returns the
    #     top TF-IDF terms under that weighting.
    #     Scenes closer to the cluster core contribute more strongly.
    #     """
    #     texts, weights = [], []

    #     for sid in cluster_scene_ids:
    #         emb    = scene_data[sid]["combined_embedding"]
    #         dist   = float(cosine_distances([emb], [centroid])[0][0])
    #         weight = float(np.exp(-dist))

    #         desc = scene_data[sid]["scene_description"]
    #         if desc.strip():
    #             texts.append(desc)
    #             weights.append(weight)

    #     if not texts:
    #         return []

    #     vectorizer      = TfidfVectorizer(max_features=max_features, stop_words="english")
    #     X               = vectorizer.fit_transform(texts).toarray()           # (n_scenes, vocab)
    #     weighted_scores = (X * np.array(weights).reshape(-1, 1)).sum(axis=0) # (vocab,)

    #     words = vectorizer.get_feature_names_out()
    #     return [words[i] for i in weighted_scores.argsort()[-top_n:][::-1]]

    # # -----------------------------
    # # NEAREST-NEIGHBOUR RETRIEVAL
    # # -----------------------------

    # def _nearest_neighbors(
    #     query_idx: int,
    #     all_embeddings: np.ndarray,
    #     scene_ids: list[str],
    #     top_k: int = 5,
    # ) -> list[tuple[str, float]]:
    #     """Returns (scene_id, cosine_distance) for the top-k nearest scenes."""
    #     dists   = cosine_distances([all_embeddings[query_idx]], all_embeddings)[0]
    #     indices = np.argsort(dists)
    #     return [
    #         (scene_ids[i], float(dists[i]))
    #         for i in indices
    #         if i != query_idx
    #     ][:top_k]

    # # -----------------------------
    # # MAIN PIPELINE
    # # -----------------------------

    # def run_pipeline(dataset: list[dict]) -> dict:
    #     """
    #     Pipeline
    #     --------
    #     1.  Process every sample (category counts + density ratios).
    #     2.  Embed the single nuScenes scene description with SBERT.
    #     3.  Aggregate to scene level.
    #     4.  UMAP (30-D) on SBERT embeddings.
    #     5.  Append normalised categorical feature vector after reduction → (38-D).
    #     6.  HDBSCAN clustering.
    #     7.  Distance-weighted TF-IDF keywords per cluster.
    #     8.  Nearest-neighbour retrieval per scene.
    #     """

    #     model = SentenceTransformer("all-MiniLM-L6-v2")

    #     sbert_scene_embeddings:    list[np.ndarray] = []
    #     categorical_scene_vectors: list[np.ndarray] = []
    #     scene_ids:  list[str]  = []
    #     scene_data: dict       = {}
    #     sample_data: list[dict] = []

    #     # ------------------------------------------------------------------
    #     # STEP 1 – process samples + SBERT scene embedding
    #     # ------------------------------------------------------------------
    #     for scene in dataset:
    #         scene_id    = scene["scene_id"]
    #         description = scene["description"]
    #         samples     = scene["samples"]

    #         processed_samples = [process_sample(s) for s in samples]

    #         scene_embedding = model.encode(
    #             description,
    #             show_progress_bar=False,
    #             normalize_embeddings=True,
    #         )  # (sbert_dim,)

    #         agg = aggregate_scene(processed_samples, scene_embedding)

    #         scene_data[scene_id] = {
    #             "samples":            processed_samples,
    #             "sbert_embedding":    agg["sbert_embedding"],
    #             "mean_categorical":   agg["mean_categorical"],
    #             "scene_description":  description,
    #             "avg_density_ratios": agg["avg_density_ratios"],
    #             **{f"avg_{k}": agg[f"avg_{k}"] for k in CATEGORY_KEYS},
    #             "avg_objects":        agg["avg_objects"],
    #             "avg_diversity":      agg["avg_diversity"],
    #         }

    #         sbert_scene_embeddings.append(agg["sbert_embedding"])
    #         categorical_scene_vectors.append(agg["mean_categorical"])
    #         scene_ids.append(scene_id)

    #     sbert_arr       = np.array(sbert_scene_embeddings)    # (N, sbert_dim)
    #     categorical_arr = np.array(categorical_scene_vectors) # (N, 8)

    #     # ------------------------------------------------------------------
    #     # STEP 2 – UMAP on SBERT embeddings  (already L2-normalised)
    #     # ------------------------------------------------------------------
    #     reducer = umap.UMAP(n_components=2, random_state=42)
    #     reduced = reducer.fit_transform(sbert_arr)             # (N, 2)

    #     # ------------------------------------------------------------------
    #     # STEP 3 – append normalised categorical features
    #     # ------------------------------------------------------------------
    #     cat_scaler         = StandardScaler()
    #     categorical_normed = cat_scaler.fit_transform(categorical_arr) # (N, 8)
    #     combined           = np.concatenate([reduced, categorical_normed], axis=1) # (N, 10)

    #     for i, scene_id in enumerate(scene_ids):
    #         scene_data[scene_id]["combined_embedding"] = combined[i]

    #     # ------------------------------------------------------------------
    #     # STEP 4 – HDBSCAN
    #     # ------------------------------------------------------------------
    #     clusterer      = hdbscan.HDBSCAN(min_cluster_size=2, prediction_data=True)
    #     cluster_labels = clusterer.fit_predict(combined)
    #     cluster_probs  = clusterer.probabilities_

    #     for i, scene_id in enumerate(scene_ids):
    #         scene_data[scene_id]["cluster_id"]          = int(cluster_labels[i])
    #         scene_data[scene_id]["cluster_probability"] = float(cluster_probs[i])

    #     # ------------------------------------------------------------------
    #     # STEP 5 – cluster grouping + centroids
    #     # ------------------------------------------------------------------
    #     clusters: dict[int, list[str]] = defaultdict(list)
    #     for scene_id in scene_ids:
    #         clusters[scene_data[scene_id]["cluster_id"]].append(scene_id)

    #     cluster_centroids: dict[int, np.ndarray] = {
    #         cid: np.mean([scene_data[s]["combined_embedding"] for s in sids], axis=0)
    #         for cid, sids in clusters.items()
    #     }

    #     # ------------------------------------------------------------------
    #     # STEP 6 – distance-weighted TF-IDF keywords
    #     # ------------------------------------------------------------------
    #     cluster_keywords: dict[int, list[str]] = {
    #         cid: weighted_tfidf_keywords(sids, scene_data, cluster_centroids[cid])
    #         for cid, sids in clusters.items()
    #     }

    #     # ------------------------------------------------------------------
    #     # STEP 7 – nearest-neighbour retrieval
    #     # ------------------------------------------------------------------
    #     for i, scene_id in enumerate(scene_ids):
    #         scene_data[scene_id]["nearest_neighbors"] = _nearest_neighbors(
    #             i, combined, scene_ids, top_k=5
    #         )

    #     # ------------------------------------------------------------------
    #     # STEP 8 – sample-level output records
    #     # ------------------------------------------------------------------
    #     for scene_id in scene_ids:
    #         cid  = scene_data[scene_id]["cluster_id"]
    #         prob = scene_data[scene_id]["cluster_probability"]

    #         for sample in scene_data[scene_id]["samples"]:
    #             sample_data.append({
    #                 "scene_id":            scene_id,
    #                 "cluster_id":          cid,
    #                 "cluster_probability": prob,
    #                 **{f"num_{k}": sample[f"num_{k}"] for k in CATEGORY_KEYS},
    #                 "total_objects":  sample["total_objects"],
    #                 "diversity":      sample["diversity"],
    #                 "density_ratios": sample["density_ratios"],
    #             })

    #     # ------------------------------------------------------------------
    #     # SERIALISE TO DATAFRAMES
    #     # ------------------------------------------------------------------
    #     def serialise_scene(sid: str) -> dict:
    #         d = scene_data[sid]
    #         return {
    #             "scene_id":            sid,
    #             "cluster_id":          d["cluster_id"],
    #             "cluster_probability": d["cluster_probability"],
    #             "scene_description":   d["scene_description"],
    #             # Flatten avg_density_ratios into individual columns
    #             **{f"avg_density_{k}": d["avg_density_ratios"][k] for k in CATEGORY_KEYS},
    #             **{f"avg_{k}":         d[f"avg_{k}"] for k in CATEGORY_KEYS},
    #             "avg_objects":       d["avg_objects"],
    #             "avg_diversity":     d["avg_diversity"],
    #             # Serialise variable-length / nested fields as JSON strings
    #             "nearest_neighbors": json.dumps(d["nearest_neighbors"]),
    #         }

    #     scenes_df = pd.DataFrame([serialise_scene(sid) for sid in scene_ids])

    #     clusters_rows = []
    #     for cid, sids in clusters.items():
    #         clusters_rows.append({
    #             "cluster_id": int(cid),
    #             "size":       len(sids),
    #             "keywords":   json.dumps(cluster_keywords.get(cid, [])),
    #             "centroid":   json.dumps(cluster_centroids[cid].tolist()),
    #         })
    #     clusters_df = pd.DataFrame(clusters_rows)

    #     # Flatten density_ratios dict into columns for the samples table
    #     flat_samples = []
    #     for row in sample_data:
    #         dr = row.pop("density_ratios")
    #         flat_row = {
    #             **row,
    #             **{f"density_{k}": dr[k] for k in CATEGORY_KEYS},
    #         }
    #         flat_samples.append(flat_row)
    #     samples_df = pd.DataFrame(flat_samples)

    #     return {
    #         "clusters_df": clusters_df,
    #         "scenes_df":   scenes_df,
    #         "samples_df":  samples_df,
    #     }

    # # -----------------------------
    # # ENTRY POINT
    # # -----------------------------

    # if __name__ == "__main__":
    #     parser = argparse.ArgumentParser(description="NuScenes preprocessing pipeline")

    #     parser.add_argument(
    #         "--version",
    #         type=str,
    #         default="v1.0-mini",
    #         help="NuScenes dataset version (e.g., v1.0-mini, v1.0-trainval)"
    #     )

    #     parser.add_argument(
    #         "--dataroot",
    #         type=str,
    #         required=True,
    #         help="Path to NuScenes dataset root"
    #     )

    #     parser.add_argument(
    #         "--out-dir",
    #         type=str,
    #         required=True,
    #         help="Output directory for parquet files"
    #     )

    #     args = parser.parse_args()

    #     # Create output dir if needed
    #     os.makedirs(args.out_dir, exist_ok=True)

    #     nusc = NuScenes(
    #         version=args.version,
    #         dataroot=args.dataroot,
    #         verbose=True,
    #     )

    #     dataset = load_nuscenes_dataset(nusc)
    #     results = run_pipeline(dataset)

    #     # Write outputs to chosen directory
    #     results["clusters_df"].to_parquet(
    #         os.path.join(args.out_dir, "output_clusters.parquet"),
    #         index=False
    #     )

    #     results["scenes_df"].to_parquet(
    #         os.path.join(args.out_dir, "output_scenes.parquet"),
    #         index=False
    #     )

    #     results["samples_df"].to_parquet(
    #         os.path.join(args.out_dir, "output_samples.parquet"),
    #         index=False
    #     )

    #     print(
    #         f"Pipeline complete — {len(dataset)} scenes processed.\n"
    #         f"  clusters: {len(results['clusters_df'])}\n"
    #         f"  scenes:   {len(results['scenes_df'])}\n"
    #         f"  samples:  {len(results['samples_df'])}\n"
    #         f"  saved to: {args.out_dir}"
    #     )
    return


if __name__ == "__main__":
    app.run()
