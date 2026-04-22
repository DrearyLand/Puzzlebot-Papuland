#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry

class TrajectoryNode(Node):
    def __init__(self):
        super().__init__('trajectory_node')
        
        # Trayectoria: Cuadrado de 2x2 metros
        self.points = [
            (2.0, 0.0),  # Vértice 1
            (2.0, 2.0),  # Vértice 2
            (0.0, 2.0),  # Vértice 3
            (0.0, 0.0)   # Vértice 4
        ]
        self.current_index = 0
        self.last_flag = False  # <--- LA MAGIA: Memoria para no saltar puntos
        
        self.pub = self.create_publisher(Odometry, 'set_point', 10)
        self.create_subscription(Bool, 'next_point', self.flag_callback, 10)
        
        self.timer = self.create_timer(1.0, self.publish_point)

    def flag_callback(self, msg):
        current_flag = msg.data
        
        # Solo avanzamos si nos dicen "True" Y la última vez nos dijeron "False"
        if current_flag and not self.last_flag: 
            self.current_index += 1
            if self.current_index >= len(self.points):
                self.get_logger().info('¡Trayectoria CUADRADA completada!')
                self.current_index = len(self.points) - 1
            else:
                self.get_logger().info(f'Yendo al vértice {self.current_index + 1} de {len(self.points)}')
        
        # Guardamos el estado actual para la siguiente lectura
        self.last_flag = current_flag

    def publish_point(self):
        if self.current_index < len(self.points):
            x, y = self.points[self.current_index]
            odom_msg = Odometry()
            odom_msg.pose.pose.position.x = x
            odom_msg.pose.pose.position.y = y
            self.pub.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()