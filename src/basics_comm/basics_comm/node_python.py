#!/usr/bin/env pyhton3
import rclpy
from rclpy.node import Node

def main(args=None):
    rclpy.init(args=args)
    nodeh = Node("My_Node")
    nodeh.get_logger().info("Hola Mundo")
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "_main_":
	main()
