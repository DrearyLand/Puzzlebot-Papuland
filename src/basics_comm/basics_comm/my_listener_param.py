#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import String

class MyClassNode(Node):
	def _init_(self):
		super()._init_("my_listener")
		self.sub = self.create_subscription(String, "my_chatter", self.callback, 1)
		self.declare_parameter("whos", "Usted")
    	
	def callback(self, msg):
		self.get_logger().info(self.get_parameter("whos").value + " escuchó "+ msg.data)

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "_main_":
    main()
