import rclpy
from ultralytics import YOLO
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from yolo_msgs.msg import InferenceResult
from yolo_msgs.msg import Yolov8Inference

bridge = CvBridge()

class CameraSuscriber(Node):
    def __init__(self):
        super()._init_("yolo_con_object_detector")
        self.get_logger().info("Node has started...")
        
        self.img_pub = self.create_publisher(Image, "/image_inference_result", 1)
        self.img_sub = self.create_subscription(IMage,'/image_raw', self.camera_callback,10)
        self.model = YOLO('home/jp/ro2_ws/src/yolov8_ros2/yolov8_ros2/yolov8n.pt')
        self.yolov8_inference = Yolov8Inference()
        self.yolov8_pub = self.create_publisher(Yolov8Inference, "/yolov8_inference",1)
        self.minimal_valid_confidance = 0.5
        
    def camera_callback(self, data):
        img = bridge.imgmsg_to_cv2(data, "bgr8")
        result = self.model(img, verbose=False, conf=self.minimal_valid_confidance)
        self.yolov8_inference.header.frame_id = "inference"
        self.yolov8_inference.header.stamp = self.get_clock().now().to_msg()
        
        boxes = result[0].boxes
        for box in boxes:
             bounding_box = box.xyxy[0]
             name_class_detectes = self.model.names[int(box.cls)]
             confidence = float(box.conf[0])
             print(name_class_detectes + "detected with " + str(confidence) + " of confidence")
             
             self.inference_result = InferenceResult()
             self.inference_result.class_name = name_class_detected
             self.inference_result.confidence = confidence
             self.inference_result.top = int(bounding_box[0])
             self.inference_result.left = int(bounding_box[1])
             self.inference_result.bottom = int(bounding_box[2])
             self.inference_result.right = int(bounding_box[3])
             self.yolov8_inference.yolov8_inference.append(self.inference_result)
             
        annotated_frame = result[0].plot()
        img_msg = bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
        
        self.img_pub.publish(img_msg)
        self.yolov8_pub.publish(self.yolov8_inference)
        self.yolov8_inference.yolov8_inference.clear()
        
def main(args=None):
    rclpy.init(args=args)
    nodeh=CameraSubscriber()
    try: rclpy.spin(nodeh)
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node Terminated")
    
if __name__ == "__main__":
    main()
