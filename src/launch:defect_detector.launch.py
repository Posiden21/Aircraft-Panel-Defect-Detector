import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('aircraft_vision'),
        'config',
        'params.yaml'
        )

    return LaunchDescription([
        Node(
            package='aircraft_vision',
            executable='defect_node',
            name='defect_detector_node',
            output='screen',
            parameters=[config]
        )
    ])
