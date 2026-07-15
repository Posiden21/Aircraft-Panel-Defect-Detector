# Portfolio Walkthrough

Use this walkthrough to demo the project as a compact robotics/computer-vision portfolio piece.

## 1. Explain the Problem

Aircraft panels can develop scratches, dents, and pitting. This package simulates a camera stream, detects surface anomalies with OpenCV, publishes annotated images, and logs structured detection metadata.

## 2. Build in a ROS 2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/Posiden21/Aircraft-Panel-Defect-Detector.git aircraft_panel_detector
cd ~/ros2_ws
colcon build --packages-select aircraft_panel_detector
source install/setup.bash
```

## 3. Generate Demo Images

```bash
cd ~/ros2_ws/src/aircraft_panel_detector
python3 scripts/generate_synthetic_panels.py --count 12 --seed 7
```

## 4. Run the Demo Pipeline

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch aircraft_panel_detector synthetic_demo.launch.py \
  image_folder:=src/aircraft_panel_detector/datasets/sample_images \
  log_path:=defect_detections.csv
```

## 5. Show Outputs

- `/defect_detector/annotated_image` shows the visual inspection result.
- `/defect_detector/detections` publishes JSON metadata.
- `defect_detections.csv` stores a simple dataset log for later ML work.

## 6. Talking Points

- The ROS nodes are thin wrappers around testable OpenCV code.
- The detector uses thresholding, edges, morphology, and contour filtering.
- The package includes synthetic data generation so it can be demonstrated without a physical camera.
- Future work can add a trained detector such as YOLO, ONNX, or `vision_msgs/Detection2DArray`.
