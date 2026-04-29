#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry

class TrajectoryNode(Node):
    def __init__(self):
        super().__init__('trajectory_node')
        
        # Extracción segura de parámetros como flotantes
        self.declare_parameter('x0', 0.0)
        self.declare_parameter('y0', 0.0)
        
        x0 = float(self.get_parameter('x0').value)
        y0 = float(self.get_parameter('y0').value)
        
        # Lado del cuadrado (2 metros)
        L = 2.0
        
        # Coordenadas relativas al punto de inicio
        self.points = [
            (x0 + L, y0),         
            (x0 + L, y0 + L),     
            (x0, y0 + L),         
            (x0, y0)              
        ]
        
        self.current_index = 0
        self.last_flag = False 
        
        self.pub = self.create_publisher(Odometry, 'set_point', 10)
        self.create_subscription(Bool, 'next_point', self.flag_callback, 10)
        
        self.timer = self.create_timer(1.0, self.publish_point)

    def flag_callback(self, msg):
        current_flag = msg.data
        if current_flag and not self.last_flag: 
            self.current_index += 1
            if self.current_index >= len(self.points):
                self.get_logger().info('Rutina cuadrada completada.')
                self.current_index = len(self.points) - 1
            else:
                self.get_logger().info(f'Transitando al vértice {self.current_index + 1}')
        
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