#!/usr/bin/env pyhton3
import cv2, rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class OpenCVBridge(Node):
   def __init__(self):
   super()._init_("image_processing")
   self.get_logger().info("Image subscription node started... ")
   self.img = None
   self.bridge = CvBridge()
   self.sub = self.create_subscription(Image, '/image_video/raw', self.camera_callback, 10)
   self.timer = self.create_timer(0.05, self.timer_callback)
   
   def camera_callback(self, msg):
      self.img = self.bridge.imgmsg_to_cv2(msg, "bgr8") # brg8

   def timer_callback(self):
      if self.img is not None:
         cv2.imshow("Received image", self.img)
         cv2.waitKey(1)s
         
def main(args=None):
   rclpy.init(args=args)
   nodeh = OpenCVBridge()
   try:rclpy.spin(nodeh)
   except Exception as error: print(error)
   except KeyboardInterrupt: print("Node Terminated!")
    
if __name__ == "__main__":
    main()
