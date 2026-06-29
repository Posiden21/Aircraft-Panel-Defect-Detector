#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

class AircraftDefectDetector(Node):
    def __init__(self):
        super().__init__('defect_detector_node')
        
        # Declare Parameters
        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('annotated_output_topic', '/defect_detector/annotated_image')
        self.declare_parameter('dataset_csv_path', 'defect_log.csv')
        self.declare_parameter('min_contour_area', 500)
        self.declare_parameter('brightness_threshold', 50)
        
        # Setup Publishers & Subscribers
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            Image, 
            self.get_parameter('input_image_topic').value, 
            self.image_callback, 
            10
        )
        self.annotated_pub = self.create_publisher(
            Image, 
            self.get_parameter('annotated_output_topic').value, 
            10
        )
        self.metadata_pub = self.create_publisher(
            String, 
            '/defect_detector/metadata', 
            10
        )
        
        # CSV Initialization
        self.csv_path = self.get_parameter('dataset_csv_path').value
        if not os.path.exists(self.csv_path):
            df = pd.DataFrame(columns=[
                'timestamp', 'frame_id', 'defect_id', 'x', 'y', 'width', 'height', 'area', 'file_name'
            ])
            df.to_csv(self.csv_path, index=False)

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        # --- OpenCV Processing (Mock Surface Defect: Edge & Dark Spot Detection) ---
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Synthetic Overlay or Baseline Defect Detection
        # Here we simulate finding surface cracks by thresholding dark anomalies
        _, thresh = cv2.threshold(gray, self.get_parameter('brightness_threshold').value, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        annotated_image = cv_image.copy()
        timestamp = datetime.now().isoformat()
        frame_id = msg.header.frame_id
        
        min_area = self.get_parameter('min_contour_area').value

        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(annotated_image, f'Defect {i}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Detection metadata
                detection_data = {
                    "defect_id": i,
                    "bbox": [x, y, w, h],
                    "area": area
                }
                detections.append(detection_data)
                
                # Append to CSV
                new_row = pd.DataFrame([{
                    'timestamp': timestamp,
                    'frame_id': frame_id,
                    'defect_id': i,
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'area': area,
                    'file_name': f"{frame_id}_defect_{i}.jpg"
                }])
                new_row.to_csv(self.csv_path, mode='a', header=False, index=False)

        # --- Publishing Outputs ---
        # 1. Publish Annotated Image
        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated_image, 'bgr8')
            annotated_msg.header = msg.header
            self.annotated_pub.publish(annotated_msg)
        except CvBridgeError as e:
            self.get_logger().error(f"Failed to publish annotated image: {e}")

        # 2. Publish JSON Metadata
        meta_msg = String()
        meta_msg.data = json.dumps({
            "timestamp": timestamp,
            "frame_id": frame_id,
            "detections": detections
        })
        self.metadata_pub.publish(meta_msg)

def main(args=None):
    rclpy.init(args=args)
    node = AircraftDefectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
