import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node

def generate_launch_description():
    pkg_puzzlebot_sim = get_package_share_directory('puzzlebot_sim')
    # NUEVO: Importamos las rutas de los paquetes oficiales
    pkg_puzzlebot_gazebo = get_package_share_directory('puzzlebot_gazebo') 
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    algo_arg = DeclareLaunchArgument(
        'algo', 
        default_value='bug0', 
        description='Algoritmo a utilizar: bug0 o bug2'
    )
    algo = LaunchConfiguration('algo')

    # CAMBIO: Ahora apuntamos al mundo oficial de MCR2
    world_file = os.path.join(pkg_puzzlebot_gazebo, 'worlds', 'mcr2_challenge.world') # Asegúrate de poner el nombre exacto del archivo .world que te dieron
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # CAMBIO: Usaremos el lanzador oficial de MCR2 para inyectar al robot con la cámara
    # En lugar de usar tu spawn_robot local, llamaremos al que viene en el description
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_puzzlebot_gazebo, 'launch', 'puzzlebot_spawner.launch.py') # Verifica el nombre exacto de este launch en la carpeta oficial
        ),
        launch_arguments={'x_pose': '0.0', 'y_pose': '0.0'}.items()
    )

    # Tus nodos de navegación se quedan intactos
    bug0_node = Node(
        package='puzzlebot_sim',
        executable='bug0_node',
        name='bug0_node',
        output='screen',
        condition=IfCondition(PythonExpression(["'", algo, "' == 'bug0'"]))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}] 
    )

    return LaunchDescription([
        algo_arg,
        gazebo,
        spawn_robot,
        bug0_node,
        rviz_node
    ])