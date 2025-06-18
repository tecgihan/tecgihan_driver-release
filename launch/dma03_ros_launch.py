import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    # Setting a coef file path
    param_path_str = LaunchConfiguration('param_path').perform(context)
    if param_path_str == '':
        param_file_path = PathJoinSubstitution([
            FindPackageShare('tecgihan_driver'),
            'config',
            LaunchConfiguration('param_file')
        ])
    else:
        param_file_path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(param_path_str)))

    return [
        Node(
            package='tecgihan_driver',
            executable='dma03_ros_publisher',
            name=LaunchConfiguration('node_name'),
            output='screen',
            parameters=[
                param_file_path,
                {'debug': LaunchConfiguration('debug')},
                {'timer': LaunchConfiguration('timer')},
                {'frequency': LaunchConfiguration('frequency')},
                {'init_zero': LaunchConfiguration('init_zero')},
                {'timeout': LaunchConfiguration('timeout')},
                {'param_file': LaunchConfiguration('param_file')},
                {'param_path': LaunchConfiguration('param_path')},
                {'set_fs': LaunchConfiguration('set_fs')},
                {'set_itf': LaunchConfiguration('set_itf')},
                {'serial_no': LaunchConfiguration('serial_no')},
                {'location': LaunchConfiguration('location')},
                {'frame_id': LaunchConfiguration('frame_id')}
            ]
        )
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name='debug',
            default_value='false',
            description='bool'),
        DeclareLaunchArgument(
            name='timer',
            default_value='-0.01',
            description='double'),
        DeclareLaunchArgument(
            name='frequency',
            default_value='100',
            description='int'),
        DeclareLaunchArgument(
            name='init_zero',
            default_value='false',
            description='bool'),
        DeclareLaunchArgument(
            name='timeout',
            default_value='1.0',
            description='double'),
        DeclareLaunchArgument(
            name='set_fs',
            default_value='false',
            description='bool'),
        DeclareLaunchArgument(
            name='set_itf',
            default_value='false',
            description='bool'),
        DeclareLaunchArgument(
            name='serial_no',
            default_value='',
            description='string'),
        DeclareLaunchArgument(
            name='location',
            default_value='',
            description='string'),
        DeclareLaunchArgument(
            name='frame_id',
            default_value='force_sensor',
            description='string'),
        DeclareLaunchArgument(
            name='node_name',
            default_value='dma03_publisher',
            description='string'),
        DeclareLaunchArgument(
            name='param_file',
            default_value='UL100901.yaml',
            description='string'),
        DeclareLaunchArgument(
            name='param_path',
            default_value='',
            description='string'),
        OpaqueFunction(function=launch_setup)
    ])
