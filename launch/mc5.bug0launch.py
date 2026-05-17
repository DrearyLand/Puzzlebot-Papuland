import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_mcr2_gazebo = get_package_share_directory('puzzlebot_gazebo')

    # 1. Lanzar Gazebo con el entorno y robot oficial de MCR2 (USANDO EL ARCHIVO SIMPLE)
    gazebo_and_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_mcr2_gazebo, 'launch', 'bringup_simulation_simple_launch.py')
        )
    )

    # 2. Tu cerebro reactivo: Bug 0
    bug0_node = Node(
        package='puzzlebot_sim',
        executable='bug0_node',
        name='bug0_node',
        namespace='robot1',
        output='screen'
    )

    # 3. Tu nodo de localización
    loc_node = Node(
        package='puzzlebot_sim',
        executable='loc_node',
        name='localisation_node',
        namespace='robot1',
        parameters=[{'x0': 0.0, 'y0': 0.0}],
        output='screen'
    )

    return LaunchDescription([
        gazebo_and_robot,
        loc_node,
        bug0_node
    ])