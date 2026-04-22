#!/usr/bin/env pyhton3
import rclpy, cv2
import numpy as np
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class OpenCVBridge(Node):
	def __init__(self):
		super()._init_("webcam_publisher")
		self.get_logger().info("Webcam publisher node started... ")
		self.width, self.height = 360, 240
		self.vid = cv2.VideoCapture(0)
		if not self.vid.isOpened():
		   self.get._logger().error("No Webcam Detected")
		   quit()
		   
		self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
		self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
		self.color_img = np.ndarray((self.width, self.height, 3)) #Empty color image
		self.gray_img = np.ndarray((self.width, self.height)) #Empty grey image
		self.bridge = CvBridge()
		self.pub = self.create_publisher(Image, "/stream", 10)
		self.timer = self.create_timer(0.05, self.timer_callback)
		
	def timer_callback(self):
		self.counter += 1
		message = "Hola Mundo "+ str(self.counter)
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
    
if __name__ == "__main__":
    main()
