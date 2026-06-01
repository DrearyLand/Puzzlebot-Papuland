#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from nav_msgs.msg import Odometry
import math

class WaypointManager(Node):
    def __init__(self):
        super().__init__('waypoint_manager')
        
        self.publisher_ = self.create_publisher(Pose2D, 'goal', 10)
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        
        # RUTA DEL LABERINTO (Extraída de las "X" rojas de la libreta)
        # Formato: (X, Y)
        self.waypoints = [
            (0.30, -1.20),  # X1: Primer pasillo, abajo al centro (Cerca del ArUco 708/F)
            (0.90, -1.50),  # X2: Centro del laberinto (Debajo del ArUco 706/C)
            (0.60, -2.70),  # X3: Pasillo del extremo derecho (Cerca del ArUco 75/G)
            (2.70, -0.60),  # X4: Salida superior izquierda (Cerca del ArUco 701/H)
        ]
        
        self.current_index = 0
        self.goal_tolerance = 0.20 # Tolerancia ampliada a 20cm para la vida real
        self.goal_published = False

    def odom_callback(self, msg):
        if self.current_index >= len(self.waypoints):
            return

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        target_x, target_y = self.waypoints[self.current_index]

        dist = math.sqrt((target_x - x)**2 + (target_y - y)**2)

        if dist < self.goal_tolerance:
            self.get_logger().info(f'¡Marca X{self.current_index + 1} alcanzada!')
            self.current_index += 1
            self.goal_published = False

        if self.current_index < len(self.waypoints) and not self.goal_published:
            goal_msg = Pose2D()
            goal_msg.x = self.waypoints[self.current_index][0]
            goal_msg.y = self.waypoints[self.current_index][1]
            self.publisher_.publish(goal_msg)
            self.get_logger().info(f'>>> Imán activado hacia X{self.current_index + 1}: X={goal_msg.x}, Y={goal_msg.y}')
            self.goal_published = True

def main(args=None):
    rclpy.init(args=args)
    node = WaypointManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()