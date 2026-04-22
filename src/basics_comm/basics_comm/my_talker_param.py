#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import String

class MyClassNode(Node):
	def __init__(self):
		super()._init_("my_talker")
		self.counter = 0
		self.declare_parameter("period", 1.0)
		self.declare_parameter("whos", "everybody")
		self.create_timer(self.get_parameter("period").value, self.timer_callback) #Se imprime el mensaje cada 0.5s
		self.pub = self.create_publisher(String, "my_chatter", 1)
		
	def timer_callback(self):
		self.counter += 1
		message = "Hello "+ self.get_parameter("whos").value + " " + str(self.counter)
		self.get_logger().info(message)
		msg = String()
		msg.data = message
		self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "__main__":
    main()
