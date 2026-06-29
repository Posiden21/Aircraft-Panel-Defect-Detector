#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import random

class SyntheticDataGenerator(Node):
    def __init__(self):
        super().__init__('synthetic_generator_node')
        
        # Declare Parameters
        self.declare_parameter('clean_images_dir', '/home/user/ros2_ws/src/aircraft_vision/clean_panels/')
        self.declare_parameter('output_image_topic', '/camera/image_raw')
        self.declare_parameter('publish_rate_hz', 1.0) # 1 frame per second
        
        # Setup Publisher & Timer
        self.bridge = CvBridge()
        self.image_pub = self.create_publisher(
            Image, 
            self.get_parameter('output_image_topic').value, 
            10
        )
        self.timer = self.create_timer(
            1.0 / self.get_parameter('publish_rate_hz').value, 
            self.timer_callback
        )
        
        # Load Clean Panel Images
        self.image_dir = self.get_parameter('clean_images_dir').value
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            self.get_logger().warn(f"Created empty directory at {self.image_dir}. Add clean images (.jpg/.png) here!")
            
        self.frame_count = 0

    def generate_synthetic_scratch(self, img):
        """Draws a random, jagged dark line simulating a surface scratch."""
        h, w, _ = img.shape
        # Choose random start point
        x1, y1 = random.randint(50, w-100), random.randint(50, h-100)
        # Draw a multi-segment jagged line
        segments = random.randint(3, 6)
        current_x, current_y = x1, y1
        
        for _ in range(segments):
            next_x = current_x + random.randint(-40, 40)
            next_y = current_y + random.randint(-15, 15)
            # Clip bounds
            next_x, next_y = np.clip(next_x, 0, w-1), np.clip(next_y, 0, h-1)
            # Draw dark, thin scratch line
            thickness = random.randint(1, 2)
            cv2.line(img, (current_x, current_y), (next_x, next_y), (20, 20, 20), thickness, cv2.LINE_AA)
            current_x, current_y = next_x, next_y
        return img

    def generate_synthetic_dent(self, img):
        """Draws a gradient circle mimicking light reflection off a surface dent."""
        h, w, _ = img.shape
        cx, cy = random.randint(100, w-100), random.randint(100, h-100)
        radius = random.randint(15, 35)
        
        # Create a shaded gradient overlay for realistic depth distortion
        overlay = img.copy()
        for r in range(radius, 0, -2):
            # Alternate light and dark shading to give a 3D indentation effect
            color_val = int(40 + (r / radius) * 60)
            cv2.circle(overlay, (cx, cy), r, (color_val, color_val, color_val), -1)
            
        # Blend overlay back smoothly into original image
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        return img

    def timer_callback(self):
        # Get list of files in the directory
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        images = [f for f in os.listdir(self.image_dir) if f.lower().endswith(valid_extensions)]
        
        if not images:
            self.get_logger().warn("No source images found in directory. Publishing fallback gray frame.", throttle_duration_sec=5.0)
            # Create a mock metallic/gray background if directory is empty
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 180
        else:
            # Pick a random image from the pool
            chosen_img = random.choice(images)
            frame = cv2.imread(os.path.join(self.image_dir, chosen_img))

        # Randomly decide what type of defect to overlay
        defect_type = random.choice(['scratch', 'dent', 'both', 'clean'])
        
        if defect_type == 'scratch' or defect_type == 'both':
            frame = self.generate_synthetic_scratch(frame)
        if defect_type == 'dent' or defect_type == 'both':
            frame = self.generate_synthetic_dent(frame)

        # Convert to ROS 2 Image Message
        try:
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            img_msg.header.stamp = self.get_clock().now().to_msg()
            img_msg.header.frame_id = f"synthetic_frame_{self.frame_count}"
            
            # Publish out to the pipeline
            self.image_pub.publish(img_msg)
            self.get_logger().info(f"Published frame {self.frame_count} with defect layout: '{defect_type.upper()}'")
            self.frame_count += 1
            
        except Exception as e:
            self.get_logger().error(f"Failed to publish synthetic image: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = SyntheticDataGenerator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
