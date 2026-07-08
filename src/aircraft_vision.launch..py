import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='aircraft_vision',
            executable='synthetic_spoofer',
            name='spoofer',
            output='screen'
        ),
        Node(
            package='aircraft_vision',
            executable='defect_detector',
            name='detector',
            output='screen',
            parameters=[{
                'canny_threshold1': 80,
                'canny_threshold2': 180,
            }],
            remappings=[
                ('/camera/image_raw', '/camera/image_raw')
            ]
        ),
        Node(
            package='aircraft_vision',
            executable='dataset_logger',
            name='logger',
            output='screen'
        )
    ])
