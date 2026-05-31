import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Llamamos al simulador oficial de MCR2 usando el nombre REAL del archivo
    mcr2_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('puzzlebot_gazebo'),
                'launch',
                'bringup_simulation_simple_launch.py'
            )
        )
    )

    # 2. Algoritmos de evasión y navegación (Bug 0 y Bug 2 c/waypoints)
    bug0_node = Node(
        package='puzzlebot_sim',
        executable='bug0_FC_node',
        name='bug0_node',
        output='screen'
    )

    bug0_node = Node(
        package='puzzlebot_sim',
        executable='bug2_FC_node',
        name='bug0_node',
        output='screen'
    )

    # 3. Tu algoritmo matemático de Localización EKF
    loc_node = Node(
        package='puzzlebot_sim',
        executable='loc_node',
        name='localisation_node',
        output='screen'
    )

    # 4. RVIZ2 sincronizado
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}] 
    )

    return LaunchDescription([
        mcr2_sim,
        bug0_node,
        loc_node,
        rviz_node
    ])