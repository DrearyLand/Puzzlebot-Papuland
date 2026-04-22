#!/usr/bin/env pyhton3
import rclpy, random
from rclpy.node import Node
from my_interfaces.msg import HardwareStatus

class MyClassNode(Node):
	def __init__(self):
		super().__init__("hw_status_publisher")
		self.counter = 0
		self.create_timer(0.5, self.timer_callback) #In sec
		self.pub = self.create_publisher(HardwareStatus,"hardware_status", 1)
		
	def timer_callback(self):
		msg = HardwareStatus()
		msg.temperature = random.randint(40, 50)
		msg.are_motors_ready = True
		msg.debug_message = "Everything is ready"
		self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if __name__ == "__main__":
	main()
