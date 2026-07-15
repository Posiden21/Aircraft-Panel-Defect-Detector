"""Launch folder image playback and the defect detector together."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("image_folder", default_value="datasets/sample_images"),
            DeclareLaunchArgument("rate_hz", default_value="1.0"),
            DeclareLaunchArgument("log_path", default_value="defect_detections.csv"),
            Node(
                package="aircraft_panel_detector",
                executable="image_publisher",
                name="image_folder_publisher",
                output="screen",
                parameters=[
                    {
                        "image_folder": LaunchConfiguration("image_folder"),
                        "rate_hz": LaunchConfiguration("rate_hz"),
                    }
                ],
            ),
            Node(
                package="aircraft_panel_detector",
                executable="defect_detector",
                name="defect_detector",
                output="screen",
                parameters=[{"log_path": LaunchConfiguration("log_path")}],
            ),
        ]
    )
