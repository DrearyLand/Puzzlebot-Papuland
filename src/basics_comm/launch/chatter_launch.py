import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

	talker_node = Node(
		package='basics_comm',
		executable= 'my_talker',
		output= 'screen',
	)
	
	listener_node = Node(
		package='basics_comm',
		executable='my_listener',
		output='screen',
	)
	
	rqt_graph_node = Node(
		package='rqt_graph',
		executable='rqt_graph',
		output='screen',
	)
	
	l_d = LaunchDescription([talker_node, listener_node, rqt_graph_node])
	
	return l_d
