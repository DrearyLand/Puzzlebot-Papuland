import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_puzzlebot_sim = get_package_share_directory('puzzlebot_sim')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # 1. Cargamos tu mundo de pruebas con el cubo y el cilindro
    world_file = os.path.join(pkg_puzzlebot_sim, 'worlds', 'bug0_test.world')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # 2. Inyectamos el robot en un área libre (0, 0)
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_puzzlebot_sim, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={'x0': '0.0', 'y0': '0.0'}.items()
    )

    return LaunchDescription([
        gazebo,
        spawn_robot
    ])