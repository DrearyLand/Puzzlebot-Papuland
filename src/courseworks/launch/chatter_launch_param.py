import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
  config = os.path.join(get_package_share_directory("courseworks"),"config","params.yaml")
  
  signal_param_node = Node(
    package='courseworks',
    executable='signal_generator_param', #Generador de ondas
    output='screen',
    emulate_tty = True,
    parameters= [config]
  )
  
  reconstrucion_node = Node(
    package='courseworks',
    executable='reconstruction_param', # Reconstructor
    output='screen',
  )
  graf_node = Node(
    package='rqt_plot',
    executable='rqt_plot',
    arguments=['/signal/data', '/signal_reconstructed/data'],  # Plotear ambas señales
    output='screen',
    )
  graph_node = Node(
    package='rqt_graph',
    executable='rqt_graph', 
    output='screen',
  )
   
  l_d = LaunchDescription([signal_param_node, reconstrucion_node, graf_node, graph_node])
  return l_d
