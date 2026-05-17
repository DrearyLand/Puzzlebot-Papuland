from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch.actions import GroupAction
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('puzzlebot_sim')
    urdf_file = os.path.join(pkg_share, 'urdf', 'puzzlebot.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    robot_name = LaunchConfiguration('robot_name')
    x0 = LaunchConfiguration('x0')
    y0 = LaunchConfiguration('y0')

    # Todos los nodos obedecerán a este Namespace
    robot_group = GroupAction([
        PushRosNamespace(robot_name),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'frame_prefix': [robot_name, '/']}]
        ),
        
        # --- NODOS COMENTADOS (No se usan en Bug 0) ---
        # Node(
        #     package='puzzlebot_sim',
        #     executable='sim_node',
        #     name='puzzlebot_sim_node',
        #     parameters=[{'x0': x0, 'y0': y0}]
        # ),
        # Node(
        #     package='puzzlebot_sim',
        #     executable='ctrl_node',
        #     name='control_node'
        # ),
        # Node(
        #     package='puzzlebot_sim',
        #     executable='traj_node',
        #     name='trajectory_node',
        #     parameters=[{'x0': x0, 'y0': y0}]
        # ),

        # --- NODOS ACTIVOS PARA ESTE RETO ---
        Node(
            package='puzzlebot_sim',
            executable='loc_node',
            name='localisation_node',
            parameters=[{'x0': x0, 'y0': y0}]
        ),
        # AGREGAMOS EL CEREBRO DE BUG 0
        Node(
            package='puzzlebot_sim',
            executable='bug0_node',
            name='bug0_node',
            output='screen'
        )
    ])

    return LaunchDescription([
        # Valores por defecto añadidos para evitar errores
        DeclareLaunchArgument('robot_name', default_value='robot1'),
        DeclareLaunchArgument('x0', default_value='0.0'),
        DeclareLaunchArgument('y0', default_value='0.0'),
        robot_group
    ])