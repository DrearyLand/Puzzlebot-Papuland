import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_puzzlebot_sim = get_package_share_directory('puzzlebot_sim')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # 1. Gazebo Classic con tu mapa
    world_file = os.path.join(pkg_puzzlebot_sim, 'worlds', 'nuevomaze.world')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # 2. Inyección del robot e inicialización de localización
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_puzzlebot_sim, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={'x0': '0.0', 'y0': '0.0'}.items()
    )

    # 3. Cerebro Bug 2 (Se lanza fuera del spawn para evitar conflictos)
    bug2_node = Node(
        package='puzzlebot_sim',
        executable='bug2_node',
        name='bug2_node',
        namespace='robot1',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        bug2_node
    ])