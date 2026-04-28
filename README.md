# Sonar 3D-15 ROS Driver

## Overview

This package provides a ROS 2 driver for the **Water Linked Sonar 3D-15**, a real-time multibeam imaging sonar. The sonar streams 3D range images over UDP multicast using the **RIP2** protocol, which are decoded and published as standard ROS messages:

- 3D point clouds with intensity: `sensor_msgs/PointCloud2` on `/sonar_point_cloud`
- Raw range images: `sensor_msgs/Image` on `/sonar_range_image`
- Signal strength images: `sensor_msgs/Image` on `/sonar_signal_image`

Compatible with ROS 2 (tested on **Jazzy**).

---

## Topics

| Topic                 | Message Type              | Description                                             |
|-----------------------|---------------------------|---------------------------------------------------------|
| `/sonar_point_cloud`  | `sensor_msgs/PointCloud2` | 3D point cloud with `x, y, z, intensity` fields         |
| `/sonar_range_image`  | `sensor_msgs/Image`       | float32 range image in meters (`32FC1`)                 |
| `/sonar_signal_image` | `sensor_msgs/Image`       | float32 log signal strength per pixel (`32FC1`, 0–255)  |

For stable color display of `/sonar_point_cloud` in RViz: set **Color Transformer → Intensity**, uncheck **Autocompute Intensity Bounds**, and set **Min = 0 / Max = 255**.

---

## Parameters

| Parameter          | Default            | Description                                         |
|--------------------|--------------------|-----------------------------------------------------|
| `IP`               | `192.168.194.96`   | IP address of the Sonar 3D-15                       |
| `speed_of_sound`   | `1491`             | Speed of sound in m/s (note: changing this takes ~20s on the sonar) |
| `enable_acoustics` | `false`            | Enable sonar acoustics on startup                   |
| `frame_id`         | `sonar_frame`      | TF frame ID stamped on all published messages       |
| `sample_frequency` | `100.0`            | Timer frequency in Hz for the UDP receive loop      |

---

## Setup

### 1. Clone into your ROS 2 workspace

```bash
cd ~/ros2_ws/src
git clone https://github.com/waterlinked/Sonar-3D-15-ROS-driver.git
```

### 2. Install Python dependencies

```bash
pip install -r Sonar-3D-15-ROS-driver/requirements.txt
```

### 3. Build

```bash
cd ~/ros2_ws
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --packages-select sonar3d
source install/local_setup.bash
```

---

## Configuration

Parameters can be set two ways:

### Option A — Edit `config/params.yaml`

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

This package is distributed under the MIT License.
