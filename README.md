# Aircraft Panel Defect Detector

ROS 2 computer vision package that detects aircraft-style panel surface defects with OpenCV, publishes annotated images, emits JSON detection metadata, and logs detections to CSV for later dataset work.

This is designed as an entry-level robotics and machine learning portfolio project: it shows ROS 2 nodes, topics, launch files, parameters, OpenCV perception, synthetic data generation, and a basic dataset logging workflow.

## Features

- Detects scratches, dark spots, and surface anomalies with thresholding, edges, morphology, and contour filtering.
- Publishes annotated images on `/defect_detector/annotated_image`.
- Publishes structured JSON metadata on `/defect_detector/detections`.
- Logs bounding boxes, areas, scores, and timestamps to CSV.
- Includes a folder-based image publisher for synthetic camera playback.
- Includes synthetic aircraft panel image generation for demos without a physical camera.

## Architecture

```text
Image folder / camera
        |
        v
/camera/image_raw
        |
        v
DefectDetectorNode
        |
        +--> /defect_detector/annotated_image
        +--> /defect_detector/detections
        +--> defect_detections.csv
```

## Repository Layout

```text
aircraft_panel_detector/
  aircraft_panel_detector/
    defect_detector_node.py
    image_folder_publisher.py
    vision.py
  launch/
    detector.launch.py
    synthetic_demo.launch.py
  scripts/
    generate_synthetic_panels.py
  test/
    test_vision.py
  package.xml
  setup.py
```

## Requirements

- ROS 2 Humble or newer
- Python 3.10+
- OpenCV
- NumPy
- `cv_bridge`
- `sensor_msgs`
- `std_msgs`

On Ubuntu with ROS 2 Humble:

```bash
sudo apt update
sudo apt install ros-humble-cv-bridge ros-humble-image-transport python3-opencv python3-numpy python3-pytest
```

Replace `humble` with your ROS 2 distribution if needed.

## Build

Clone this repository inside a ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone <your-repo-url> aircraft_panel_detector
cd ~/ros2_ws
colcon build --packages-select aircraft_panel_detector
source install/setup.bash
```

## Run a Synthetic Demo

Generate sample images:

```bash
cd ~/ros2_ws/src/aircraft_panel_detector
python3 scripts/generate_synthetic_panels.py --count 12 --seed 7
```

Launch both the folder image publisher and detector:

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch aircraft_panel_detector synthetic_demo.launch.py \
  image_folder:=src/aircraft_panel_detector/datasets/sample_images \
  log_path:=defect_detections.csv
```

View output topics:

```bash
ros2 topic echo /defect_detector/detections
ros2 run rqt_image_view rqt_image_view
```

Select `/defect_detector/annotated_image` in `rqt_image_view`.

## Run With a Real Camera Topic

If another node publishes `sensor_msgs/Image` on `/camera/image_raw`:

```bash
ros2 launch aircraft_panel_detector detector.launch.py
```

Override parameters:

```bash
ros2 launch aircraft_panel_detector detector.launch.py \
  input_topic:=/my_camera/image_raw \
  min_area:=100 \
  log_path:=logs/defect_detections.csv
```

## Topics

| Topic | Type | Description |
| --- | --- | --- |
| `/camera/image_raw` | `sensor_msgs/Image` | Input image stream |
| `/defect_detector/annotated_image` | `sensor_msgs/Image` | Annotated output image |
| `/defect_detector/detections` | `std_msgs/String` | JSON detection metadata |

## Detection Metadata

Example message:

```json
{
  "timestamp": "2026-06-23T14:00:00+00:00",
  "defect_count": 1,
  "detections": [
    {
      "x": 143,
      "y": 87,
      "w": 42,
      "h": 19,
      "area": 612.5,
      "score": 0.613
    }
  ]
}
```

## Test

The OpenCV core can be tested without ROS 2:

```bash
python3 -m pytest test
```

Inside a ROS 2 workspace, run package tests with:

```bash
colcon test --packages-select aircraft_panel_detector
colcon test-result --verbose
```


## Future Improvements

- Add YOLOv8, Detectron2, or ONNX model inference as an alternate detector.
- Record and replay ROS bags for repeatable benchmark runs.
- Add FPS, latency, CPU, and memory metrics.
- Publish `vision_msgs/Detection2DArray` instead of JSON strings.
- Add Docker or dev container support.
