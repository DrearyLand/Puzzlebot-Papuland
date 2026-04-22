import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO

class TrafficSignDetector(Node):
    def __init__(self):
        super().__init__('traffic_sign_detector')
        self.publisher_ = self.create_publisher(Image, 'camera/image_detected', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.cap = cv2.VideoCapture(0)  # Abrir la cámara
        self.bridge = CvBridge()
        self.model = YOLO('/home/jp/RED_Neuronal_30Epochs/runs/detect/train/weights/best.pt')  # Carga el modelo YOLOv8

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error('No se pudo capturar la imagen de la cámara.')
            return

        results = self.model(frame)
        # results es una lista de resultados, vamos a iterar sobre ellos y renderizar
        for result in results:
            detected_frame = result.plot()  # Obtener la imagen con las detecciones

            # Publicar la imagen detectada en un tópico ROS2
            msg = self.bridge.cv2_to_imgmsg(detected_frame, 'bgr8')
            self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TrafficSignDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

