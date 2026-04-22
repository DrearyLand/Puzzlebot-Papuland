#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node

class MyClassNode(Node):
	def _init_(self):
		super()._init_("my_node")
		self.counter = 0
		self.create_timer(0.5, self.timer_callback) #Se imprime el mensaje cada 0.5s
    	
	def timer_callback(self):
		self.counter += 1
		self.get_logger().info("Hola Mundo "+ str(self.counter))

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "_main_":
	main()
