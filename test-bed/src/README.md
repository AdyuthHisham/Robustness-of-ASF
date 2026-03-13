# Directories
1. SFModels: Models used for testing
2. Datasets: Datasets used for testing
3. Modules: Modules of testbed

# Tips and tricks

## Datasets

|Dataset|N. Camera|N. LiDAR|N. RADAR|Time/Scene(seconds)|Total Time(min)|Number of Scenes|
|-------|---------|--------|--------|----------|----------|----------|
|Waymo|5|5|0|20|333|1000|
|nuScenes|6|1|5|20|330|1000|
|KRADAR|---------|--------|--------|----------|----------|----------|
|NVIDIA|---------|--------|--------|----------|----------|----------|

![AV dataset comparison](file:///home/adhish/Pictures/Screenshots/screenshot-2026-03-02-160938.png)
### Waymo
#### Source(Streaming/MIMER)
Available in MIMER

#### Sensor Specs
![Sensor Layout and Coordinate System](file:///home/adhish/Pictures/Screenshots/screenshot-2026-03-02-150209.png)
#### Docs

### nuScenes
- [ ] Nuscenes has maps, dafuq is dat
#### Sensor Specs
![Sensor Layout and Coordinate System](file:///home/adhish/Pictures/Screenshots/screenshot-2026-03-02-161157.png)
#### Source(Streaming/MIMER)
Available in MIMER
#### Docs

### K-RADAR
#### Source(Streaming/MIMER)
#### Docs
#### Notes
``` text
We provide two sample sequences to help researchers get started with the K-Radar dataset:

    Sequence 1: Sequence collected under normal weather conditions
    Sequence 58: Sequence collected under heavy snow conditions
```

### NVIDIA
#### Source(Streaming/MIMER)
[Hugging face allows data streaming](https://huggingface.co/docs/datasets/en/stream)
#### Docs
