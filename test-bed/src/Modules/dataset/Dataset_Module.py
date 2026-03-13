import marimo

__generated_with = "0.20.4"
app = marimo.App()


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
        dataroot="/home/adhish/Productivity/AMSCUP/test-bed/src/Datasets/NuScenes",
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

    my_sample = nusc.get("sample", first_sample_token)
    my_sample
    return (my_sample,)


@app.cell
def _(nusc):
    nusc.sensor
    return


@app.cell
def _(my_sample, nusc):
    nusc.render_pointcloud_in_image(
        my_sample["token"], pointsensor_channel="RADAR_FRONT"
    )
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


if __name__ == "__main__":
    app.run()
