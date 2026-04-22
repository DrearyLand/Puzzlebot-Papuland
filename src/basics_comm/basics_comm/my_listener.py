#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import String

class MyClassNode(Node):
	def __init__(self):
		super().__init__("my_listener")
		self.sub = self.create_subscription(String, "my_chatter", self.callback, 1)
    	
	def callback(self, msg):
		self.get_logger().info("¿Escuche hola mundo? "+ msg.data)

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if __name__ == "__main__":
	main()
