#!/usr/bin/env pyhton3
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import Int32

class MyClassNode(Node):
	def __init__(self):
		super().__init__("generator")
		self.get_logger().info('generator node initialized...')
		self.create_timer(0.5, self.timer_callback)
		self.pub = self.create_publisher(Int32, "random", 1)
		
	def timer_callback(self):
		msg = Int32()
		msg.data = random.randint(0,9)
		self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if __name__ == "__main__":
	main()
