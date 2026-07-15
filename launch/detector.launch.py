"""Launch the aircraft panel defect detector node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("input_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument("min_area", default_value="80"),
            DeclareLaunchArgument("dark_threshold", default_value="85"),
            DeclareLaunchArgument("log_path", default_value="defect_detections.csv"),
            Node(
                package="aircraft_panel_detector",
                executable="defect_detector",
                name="defect_detector",
                output="screen",
                parameters=[
                    {
                        "input_topic": LaunchConfiguration("input_topic"),
                        "min_area": LaunchConfiguration("min_area"),
                        "dark_threshold": LaunchConfiguration("dark_threshold"),
                        "log_path": LaunchConfiguration("log_path"),
                    }
                ],
            ),
        ]
    )
