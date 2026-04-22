#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import Int32, Float32

class MyClassNode(Node):
	def __init__(self):
		super().__init__("counter")
		self.get_logger().info('Counter node initialized...')
		self.sub = self.create_subscription(Int32, "random", self.callback, 1)
		self.sub = self.create_publisher(Float32, "prom", 1)
		self.create_timer(0.1, self.timer_callback) # In sec
		self.sum = 0
		self.number = 0
    	
	def timer_callback(self, msg):
		msg = Float32()
		if self.number > 0:
			msg.data = self.sum/self.number
		self.pub.publish(msg)
		
	def callback(self,msg):
		self.sum += msg.data
		self.number += 1

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if __name__ == "__main__":
	main()
