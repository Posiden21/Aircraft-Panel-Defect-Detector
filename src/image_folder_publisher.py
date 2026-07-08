import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageFolderPublisher(Node):
    """Publishes images from a folder to simulate a camera feed."""

    def __init__(self):
        super().__init__('image_folder_publisher')
        self.declare_parameter('image_folder', 'datasets/sample_images')
        self.declare_parameter('rate_hz', 1.0)
        self.image_folder = Path(self.get_parameter('image_folder').value)
        self.rate_hz = float(self.get_parameter('rate_hz').value)
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()
        self.images = sorted(list(self.image_folder.glob('*.png')) + list(self.image_folder.glob('*.jpg')))
        self.index = 0
        self.timer = self.create_timer(1.0 / self.rate_hz, self.publish_image)
        self.get_logger().info(f'Publishing images from {self.image_folder}')

    def publish_image(self):
        if not self.images:
            self.get_logger().warning('No images found.')
            time.sleep(1)
            return
        image_path = self.images[self.index % len(self.images)]
        frame = cv2.imread(str(image_path))
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher.publish(msg)
        self.index += 1


def main(args=None):
    rclpy.init(args=args)
    node = ImageFolderPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
