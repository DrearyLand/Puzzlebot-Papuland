import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
  
  signal_node = Node(
    package='courseworks',
    executable='signal_generator',
    output='screen',
  )
  
  process_node = Node(
    package='courseworks',
    executable='process',
    output='screen',
  )
  graph_node = Node(
    package='rqt_graph',
    executable='rqt_graph',
    output='screen',
  )

  graf_node = Node(
    package='rqt_plot',
    executable='rqt_plot',
    arguments=['/signal/data', '/proc_signal/data'],  # Grafica ambas señales
    output='screen',
    )
    
  l_d = LaunchDescription([signal_node, process_node, graph_node, graf_node])
  return l_d
