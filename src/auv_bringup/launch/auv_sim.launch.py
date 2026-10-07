import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    world = os.path.join(get_package_share_directory('auv_gazebo'), 'worlds', 'ice_ocean_with_land.sdf')
    model = os.path.join(get_package_share_directory('auv_description'), 'models', 'observation_platform', 'model.sdf')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items(),
    )
    spawn_platform = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-file', model, '-name', 'observation_platform', '-z', '0.30'],
        output='screen',
    )
    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/model/observation_platform/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/model/observation_platform/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
            '/camera/image@sensor_msgs/msg/Image[ignition.msgs.Image',
        ],
        output='screen',
    )

    return LaunchDescription([gazebo, spawn_platform, bridge])
