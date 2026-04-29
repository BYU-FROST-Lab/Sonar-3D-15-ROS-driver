# Sonar 3D-15 ROS Driver

## Overview

ROS 2 driver for the **Water Linked Sonar 3D-15** multibeam imaging sonar. The sonar streams 3D range images over UDP multicast using the **RIP2** protocol (Snappy-compressed protobuf). This repo contains two packages:

| Package | Description |
|---|---|
| `sonar3d_msgs` | Custom message definitions matching the sonar wire protocol |
| `sonar3d` | Driver node — decodes packets and publishes |

Compatible with ROS 2 (tested on **Jazzy** and **Humble**).

---

## Topics

### Processed outputs

| Topic | Type | Description |
|---|---|---|
| `sonar_point_cloud` | `sensor_msgs/PointCloud2` | 3D point cloud with `x, y, z, intensity` fields |
| `sonar_range_image` | `sensor_msgs/Image` | float32 range image in meters (`32FC1`) |
| `sonar_signal_image` | `sensor_msgs/Image` | float32 log signal strength per pixel (`32FC1`, 0–255) |

`sonar_point_cloud` and `sonar_signal_image` are published together once a matched `RangeImage` + `BitmapImageGreyscale8` pair arrives for the same sequence ID.

For stable color display of `sonar_point_cloud` in RViz: set **Color Transformer → Intensity**, uncheck **Autocompute Intensity Bounds**, and set **Min = 0 / Max = 255**.

### Raw outputs

Raw topics carry the wire-protocol data with no conversion applied, preserving all sonar metadata. They are published as each packet arrives, independent of pair matching.

| Topic | Type | Description |
|---|---|---|
| `sonar_raw_range_image` | `sonar3d_msgs/RangeImage` | Raw range pixel data + sonar metadata |
| `sonar_raw_bitmap_image` | `sonar3d_msgs/BitmapImageGreyscale8` | Raw 8-bit greyscale pixel data (all bitmap types) |

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `IP` | `192.168.194.96` | IP address of the Sonar 3D-15 |
| `speed_of_sound` | `1491` | Speed of sound in m/s (changing this takes ~20 s on the sonar) |
| `enable_acoustics` | `false` | Enable sonar acoustics on startup |
| `frame_id` | `sonar_frame` | TF frame ID stamped on all published messages |
| `sample_frequency` | `100.0` | Timer frequency in Hz for the UDP receive loop |

---

## Setup

### 1. Clone into your ROS 2 workspace

```bash
cd ~/ros2_ws/src
git clone https://github.com/waterlinked/Sonar-3D-15-ROS-driver.git
```

### 2. Install Python dependencies

```bash
pip install -r Sonar-3D-15-ROS-driver/sonar3d/requirements.txt
```

### 3. Build

```bash
cd ~/ros2_ws
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --packages-select sonar3d_msgs sonar3d
source install/setup.bash
```

---

## Configuration

Parameters can be set two ways:

### Option A — Edit `sonar3d/config/params.yaml`

```yaml
sonar_node:
  ros__parameters:
    IP: 192.168.194.96
    speed_of_sound: 1491
    enable_acoustics: false
    frame_id: sonar_frame
    sample_frequency: 100.0
```

Then launch with the config-file launch file:

```bash
ros2 launch sonar3d sonar3d_launch.py
```

A custom config file path can be passed at launch time:

```bash
ros2 launch sonar3d sonar3d_launch.py params_file:=/path/to/your/params.yaml
```

### Option B — Pass arguments directly at launch

```bash
ros2 launch sonar3d sonar3d.launch.py ip:=192.168.2.96 speed_of_sound:=1500
```

---

## License

MIT
