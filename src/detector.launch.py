from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='aircraft_panel_detector',
            executable='defect_detector',
            name='aircraft_panel_defect_detector',
            parameters=[{
                'input_topic': '/camera/image_raw',
                'min_area': 60,
                'log_path': 'defect_detections.csv',
            }],
        ),
    ])
