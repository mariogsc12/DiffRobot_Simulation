import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch.actions import (DeclareLaunchArgument, EmitEvent, ExecuteProcess,
                            LogInfo, RegisterEventHandler, TimerAction)
from launch.event_handlers import (OnExecutionComplete, OnProcessExit,
                                OnProcessIO, OnProcessStart, OnShutdown)

from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    package_name = 'mario_robot'
    custom_world_path = '/home/mario/REPOS/robot_ros/worlds/custom.world'

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py')]),
                    launch_arguments={'use_sim_time':'true'}.items()
    )

   
    # Include the gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'world': custom_world_path  
        }.items(),
    )

    # Run the spawner node from the gazebo_ros package. The entity name does not really matter fi you only have a single robot
    spawn_entity = Node(package='gazebo_ros',executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description', 
                                   '-entity', 'my_robot'])
    
    use_sim_time = LaunchConfiguration('use_sim_time')

    joy_params = os.path.join(get_package_share_directory('mario_robot'),'config','joystick.yaml')

    joy_node = Node(
            package='joy',
            executable='joy_node',
            parameters=[joy_params, {'use_sim_time': use_sim_time}],
         )

    teleop_node = Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            parameters=[joy_params, {'use_sim_time': use_sim_time}],
        )

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),
        joy_node,
        teleop_node,
        # twist_stamper 
    ])