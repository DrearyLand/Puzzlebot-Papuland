#!/usr/bin/env pyhton3
import rclpy, time, sys
from rclpy.node import Node
from std_msgs.msg import String

class MyClassNode(Node):
	def _init_(self):
		super()._init_("my_listener")
		self.sub = self.create_subscription(String, "my_chatter", self.callback, 1)
    	
	def callback(self, msg):
		self.get_logger().info(sys.argv[1] + " Escuchó: " + msg.data)

def main(args=None):
    if len(sys.argv) < 2:
        print("Usage : ros2 run <pkg_name> <exe_name> arg1 arg2")
        print("  arg1 =  quien saluda")
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "_main_":
    main()
