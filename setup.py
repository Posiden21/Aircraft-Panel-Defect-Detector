from setuptools import setup

package_name = 'aircraft_panel_detector'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/detector.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Alexander Alvarez',
    maintainer_email='7alexalvarez@gmail.com',
    description='ROS2 OpenCV aircraft panel defect detector.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'defect_detector = aircraft_panel_detector.defect_detector_node:main',
            'image_publisher = aircraft_panel_detector.image_folder_publisher:main',
        ],
    },
)
