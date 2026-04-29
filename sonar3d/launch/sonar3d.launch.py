from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'ip',
            default_value='192.168.194.96',
            description='IP address of the Sonar 3D-15'
        ),
        DeclareLaunchArgument(
            'speed_of_sound',
            default_value='1491',
            description='Speed of sound in m/s'
        ),
        Node(
            package='sonar3d',
            executable='sonar_publisher',
            name='sonar_node',
            output='screen',
            parameters=[{
                'IP': LaunchConfiguration('ip'),
                'speed_of_sound': LaunchConfiguration('speed_of_sound'),
            }]
        )
    ])
