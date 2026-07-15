"""ROS 2 node that detects aircraft panel defects from camera images."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from .vision import detect_defects, detections_to_json_payload


class DefectDetectorNode(Node):
    """Subscribe to raw images and publish annotated images plus JSON metadata."""

    def __init__(self) -> None:
        super().__init__("defect_detector")
        self.declare_parameter("input_topic", "/camera/image_raw")
        self.declare_parameter("annotated_topic", "/defect_detector/annotated_image")
        self.declare_parameter("detections_topic", "/defect_detector/detections")
        self.declare_parameter("log_path", "defect_detections.csv")
        self.declare_parameter("min_area", 80)
        self.declare_parameter("dark_threshold", 85)

        self.bridge = CvBridge()
        self.log_path = Path(str(self.get_parameter("log_path").value))
        self._ensure_log_header()

        input_topic = str(self.get_parameter("input_topic").value)
        annotated_topic = str(self.get_parameter("annotated_topic").value)
        detections_topic = str(self.get_parameter("detections_topic").value)

        self.image_sub = self.create_subscription(Image, input_topic, self.image_callback, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)
        self.detections_pub = self.create_publisher(String, detections_topic, 10)
        self.get_logger().info(f"Listening on {input_topic}")

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            self.get_logger().error(f"Failed to convert ROS image: {exc}")
            return

        detections, annotated = detect_defects(
            frame,
            min_area=int(self.get_parameter("min_area").value),
            dark_threshold=int(self.get_parameter("dark_threshold").value),
        )
        timestamp = datetime.now(timezone.utc).isoformat()
        frame_id = msg.header.frame_id or "camera_frame"

        payload = detections_to_json_payload(timestamp, frame_id, detections)
        self._append_detections(timestamp, frame_id, detections)

        annotated_msg = self.bridge.cv2_to_imgmsg(annotated, encoding="bgr8")
        annotated_msg.header = msg.header
        self.annotated_pub.publish(annotated_msg)

        metadata_msg = String()
        metadata_msg.data = json.dumps(payload)
        self.detections_pub.publish(metadata_msg)

    def _ensure_log_header(self) -> None:
        if self.log_path.parent != Path("."):
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with self.log_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "frame_id", "defect_id", "x", "y", "w", "h", "area", "score"])

    def _append_detections(self, timestamp: str, frame_id: str, detections) -> None:
        with self.log_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for defect_id, detection in enumerate(detections, start=1):
                writer.writerow(
                    [
                        timestamp,
                        frame_id,
                        defect_id,
                        detection.x,
                        detection.y,
                        detection.w,
                        detection.h,
                        detection.area,
                        detection.score,
                    ]
                )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = DefectDetectorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
