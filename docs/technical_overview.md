# Technical Overview

## Goal

This project demonstrates a practical aircraft panel inspection workflow:

1. Acquire images from a camera topic or folder-based image stream.
2. Detect likely scratches, dents, and pitting with OpenCV.
3. Publish annotated frames for operators.
4. Publish structured JSON metadata for downstream logging or analytics.
5. Save detection rows to CSV for later dataset creation.

## Detection Pipeline

```text
BGR frame
  -> grayscale conversion
  -> Gaussian blur
  -> dark-region thresholding
  -> Canny edge detection
  -> morphology cleanup
  -> contour filtering by area
  -> bounding boxes + confidence-style score
```

The detector is intentionally transparent. It is not a certified aviation inspection model; it is a portfolio-ready robotics/computer-vision baseline that can be expanded with learned models later.

## ROS 2 Nodes

| Node | Purpose |
| --- | --- |
| `defect_detector` | Subscribes to raw images, runs OpenCV detection, publishes annotations and JSON metadata. |
| `image_folder_publisher` | Publishes local image files as a synthetic camera stream. |

## Topics

| Topic | Type | Description |
| --- | --- | --- |
| `/camera/image_raw` | `sensor_msgs/Image` | Input image stream |
| `/defect_detector/annotated_image` | `sensor_msgs/Image` | Annotated output image |
| `/defect_detector/detections` | `std_msgs/String` | JSON detection metadata |

## Why This Structure

The OpenCV logic lives in `aircraft_panel_detector/vision.py` so it can be tested without ROS. The ROS node wraps that core logic, which keeps the package easier to test, review, and extend.
