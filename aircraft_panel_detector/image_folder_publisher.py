"""ROS 2 node that publishes images from a folder as a synthetic camera stream."""

from __future__ import annotations

from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageFolderPublisher(Node):
    """Publish PNG/JPG images repeatedly on a camera topic."""

    def __init__(self) -> None:
        super().__init__("image_folder_publisher")
        self.declare_parameter("image_folder", "datasets/sample_images")
        self.declare_parameter("output_topic", "/camera/image_raw")
        self.declare_parameter("rate_hz", 1.0)

        self.image_folder = Path(str(self.get_parameter("image_folder").value))
        self.publisher = self.create_publisher(Image, str(self.get_parameter("output_topic").value), 10)
        self.bridge = CvBridge()
        self.images = sorted(self.image_folder.glob("*.png")) + sorted(self.image_folder.glob("*.jpg"))
        self.index = 0

        rate_hz = max(0.1, float(self.get_parameter("rate_hz").value))
        self.timer = self.create_timer(1.0 / rate_hz, self.publish_image)
        self.get_logger().info(f"Publishing {len(self.images)} images from {self.image_folder}")

    def publish_image(self) -> None:
        if not self.images:
            self.get_logger().warning("No .png or .jpg images found.")
            return

        image_path = self.images[self.index % len(self.images)]
        frame = cv2.imread(str(image_path))
        if frame is None:
            self.get_logger().warning(f"Skipping unreadable image: {image_path}")
            self.index += 1
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = image_path.stem
        self.publisher.publish(msg)
        self.index += 1


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ImageFolderPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
