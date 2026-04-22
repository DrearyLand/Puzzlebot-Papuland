#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import Float32

class PuzzlebotSim(Node):
    def __init__(self):
        super().__init__('puzzlebot_sim_node')
        
        # Parámetros del Puzzlebot según el Mini Challenge 2
        self.r = 0.05  # Radio de la rueda (5 cm)
        self.l = 0.19  # Distancia entre ruedas (19 cm)
        
        # Estado inicial del robot
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # Velocidades actuales
        self.v = 0.0
        self.w = 0.0
        
        # Suscriptor al tópico cmd_vel (Twist)
        self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, 10)
        
        # Publicadores: Pose simulada y velocidades de llantas
        self.pose_pub = self.create_publisher(PoseStamped, 'pose_sim', 10)
        self.wr_pub = self.create_publisher(Float32, 'wr', 10)
        self.wl_pub = self.create_publisher(Float32, 'wl', 10)
        
        # Timer para el solver numérico (100 Hz -> dt = 0.01s)
        self.dt = 0.01
        self.create_timer(self.dt, self.update_kinematics)

    def cmd_vel_callback(self, msg):
        # Recibir comandos del controlador
        self.v = msg.linear.x
        self.w = msg.angular.z

    def update_kinematics(self):
        # 1. Resolver ecuaciones diferenciales (Método de Euler)
        self.x += self.v * math.cos(self.theta) * self.dt
        self.y += self.v * math.sin(self.theta) * self.dt
        self.theta += self.w * self.dt
        
        # 2. Publicar pose_sim (PoseStamped)
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = "world"
        pose_msg.pose.position.x = self.x
        pose_msg.pose.position.y = self.y
        pose_msg.pose.position.z = 0.0
        self.pose_pub.publish(pose_msg)
        
        # 3. Calcular y publicar velocidades de las ruedas separadas
        wr = (self.v + (self.w * self.l / 2.0)) / self.r
        wl = (self.v - (self.w * self.l / 2.0)) / self.r
        
        self.wr_pub.publish(Float32(data=wr))
        self.wl_pub.publish(Float32(data=wl))

def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotSim()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
