#!/usr/bin/env pyhton3
import rclpy, time, sys
from rclpy.node import Node
from std_msgs.msg import String

class MyClassNode(Node):
	def __init__(self):
		super()._init_("my_talker")
		self.counter = 0
		period = float(sys.argv[1]) # Convierte a double el arg1
		self.create_timer(period, self.timer_callback) #Se imprime el mensaje cada 0.5s
		self.pub = self.create_publisher(String, "my_chatter", 1)
		
	def timer_callback(self):
		self.counter += 1
		message = "Hello " + sys.argv[2] + " " + str(self.counter)
		self.get_logger().info(message)
		msg = String()
		msg.data = message
		self.pub.publish(msg)


def main(args=None):
    if len(sys.argv) < 3:
        print("Usage : ros2 run <pkg_name> <exe_name> arg1 arg2")
        print("  arg1 = periodo del timer")
        print("  arg2 =  quien saluda")
    rclpy.init(args=args)
    nodeh = MyClassNode()
    try:rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated!")
    
if _name_ == "__main__":
    main()
