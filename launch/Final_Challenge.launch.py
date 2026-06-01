import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    mi_paquete_dir = get_package_share_directory('puzzlebot_sim')
    mi_mundo = os.path.join(mi_paquete_dir, 'worlds', 'nuevomaze.world')

    mcr2_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('puzzlebot_gazebo'),
                'launch',
                'bringup_simulation_simple_launch.py'
            )
        ),
        launch_arguments={'world': mi_mundo}.items()
    )

    # 3. Nodo de Visión Manchester
    aruco_tracker_node = Node(
        package='aruco_opencv',
        executable='aruco_tracker_autostart',
        name='aruco_tracker',
        output='screen',
        parameters=[{
            'cam_base_topic': 'camera',
            'marker_size': 0.14
        }]
    )

    # 4. Bug 0
    bug0_node = Node(
        package='puzzlebot_sim',
        executable='bug0_FC_node',
        name='bug0_node',
        output='screen'
    )

    # 5. Nodo EKF
    ekf_node = Node(
        package='puzzlebot_sim',
        executable='ekf_vision_node',
        name='ekf_vision_node',
        output='screen'
    )

    # 6. RVIZ2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}] 
    )

    return LaunchDescription([
        mcr2_sim,
        aruco_tracker_node,
        bug0_node,
        ekf_node,
        rviz_node
    ])