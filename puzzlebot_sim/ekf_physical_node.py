#!/usr/bin/env python3
import rclpy
from rclpy import qos
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32
from aruco_opencv_msgs.msg import ArucoDetection
import math
import numpy as np

class EKFPhysical(Node):
    def __init__(self):
        super().__init__('ekf_physical_node')
        
        # 1. Suscripciones a los sensores físicos del Puzzlebot
        self.joint_sub = self.create_subscription(JointState, 'joint_states', self.joint_callback, 10)
        self.wr_sub = self.create_subscription(Float32, 'VelocityEncR', self.wr_callback, 10)
        self.wl_sub = self.create_subscription(Float32, 'VelocityEncL', self.wl_callback, 10)
        
        # 2. Suscripción a la cámara (Fase de Actualización)
        self.aruco_sub = self.create_subscription(ArucoDetection, '/aruco_detections', self.vision_callback, 10)
        
        # 3. Publicador de la Odometría Filtrada
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)

        # Parámetros físicos (Extraídos del tuneo original)
        self.kr = 0.01
        self.kl = 0.01
        self.r = 0.05
        self.l = 0.19

        self.wr = 0.0
        self.wl = 0.0
        
        # Estado Inicial
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v = 0.0
        self.w = 0.0
        
        # Covarianza Inicial (Incertidumbre)
        self.sigma = np.zeros((3, 3))
        
        # Ruido de Observación (R)
        self.R = np.array([
            [0.05, 0.0],
            [0.0, 0.05]
        ])

        # EL DICCIONARIO DE LA PISTA FÍSICA
        self.aruco_map = {
            70:  (1.84, -0.30),
            705: (0.90, -1.20),
            706: (2.39, -1.26),
            708: (1.19, -1.21),
            703: (1.23, -2.07),
            702: (0.28, -1.82),
            75:  (2.74, -2.40),
            701: (2.84,  0.0)
        }

        self.dt = 0.05 # 20 Hz
        self.timer = self.create_timer(self.dt, self.update_localisation)
        self.get_logger().info('Cerebro EKF Físico Inicializado. Esperando ArUcos...')

    def joint_callback(self, msg):
        try:
            idx_r = msg.name.index('wheel_r_joint')
            idx_l = msg.name.index('wheel_l_joint')
            self.wr = msg.velocity[idx_r]
            self.wl = msg.velocity[idx_l]
        except ValueError:
            pass

    def wr_callback(self, msg):
        self.wr = msg.data

    def wl_callback(self, msg):
        self.wl = msg.data

    def propagate_covariance(self):
        delta_d = self.v * self.dt
        delta_theta = self.w * self.dt

        # Jacobiano del Sistema
        H = np.array([
            [1.0, 0.0, -delta_d * math.sin(self.theta)],
            [0.0, 1.0,  delta_d * math.cos(self.theta)],
            [0.0, 0.0,  1.0]
        ])

        q_r = self.kr * abs(self.wr * self.dt)
        q_l = self.kl * abs(self.wl * self.dt)

        Q = np.array([
            [q_r, 0.0, 0.0],
            [0.0, q_l, 0.0],
            [0.0, 0.0, abs(delta_theta) * (self.kr + self.kl)]
        ])

        self.sigma = H @ self.sigma @ H.T + Q

    def compute_robot_velocities(self):
        self.v = self.r * (self.wr + self.wl) / 2.0
        self.w = self.r * (self.wr - self.wl) / self.l

    def integrate_odometry(self):
        self.x += (self.v * math.cos(self.theta)) * self.dt
        self.y += (self.v * math.sin(self.theta)) * self.dt
        self.theta += self.w * self.dt
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

    def vision_callback(self, msg):
        for marker in msg.markers:
            m_id = marker.marker_id
            
            if m_id in self.aruco_map:
                m_x, m_y = self.aruco_map[m_id]
                
                # --- AJUSTE DE TRANSFORMACIÓN (Cámara a Centro del Robot) ---
                offset_frontal = 0.08  # 8 cm desde el centro a la cámara
                
                # Z: Medición Euclidiana (Trasladada al centro del robot)
                dx_cam = marker.pose.position.x
                dz_cam = marker.pose.position.z + offset_frontal 
                
                d_medido = math.sqrt(dx_cam**2 + dz_cam**2)
                phi_medido = math.atan2(dx_cam, dz_cam)
                Z = np.array([[d_medido], [phi_medido]])
                
                # Z_esperado: Lo que el filtro espera ver
                dx_map = m_x - self.x
                dy_map = m_y - self.y
                d_esperado = math.sqrt(dx_map**2 + dy_map**2)
                phi_esperado = math.atan2(dy_map, dx_map) - self.theta
                phi_esperado = math.atan2(math.sin(phi_esperado), math.cos(phi_esperado))
                Z_esperado = np.array([[d_esperado], [phi_esperado]])
                
                # Innovación (Error entre medición y expectativa)
                Y = Z - Z_esperado
                Y[1, 0] = math.atan2(math.sin(Y[1, 0]), math.cos(Y[1, 0]))
                
                if d_esperado > 0.01:
                    # Jacobiano de Observación
                    H_obs = np.array([
                        [-(dx_map)/d_esperado,    -(dy_map)/d_esperado,    0.0],
                        [(dy_map)/(d_esperado**2), -(dx_map)/(d_esperado**2), -1.0]
                    ])
                    
                    # Ganancia de Kalman (El factor de confianza)
                    S = H_obs @ self.sigma @ H_obs.T + self.R
                    K = self.sigma @ H_obs.T @ np.linalg.inv(S)
                    
                    # Corrección del Estado
                    correction = K @ Y
                    self.x += float(correction[0, 0])
                    self.y += float(correction[1, 0])
                    self.theta += float(correction[2, 0])
                    self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
                    
                    # Colapso de la Covarianza
                    I = np.eye(3)
                    self.sigma = (I - K @ H_obs) @ self.sigma
                    self.get_logger().info(f'ArUco {m_id} interceptado. Covarianza actualizada.')

    def publish_odometry(self):
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        
        odom_msg.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom_msg.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        # Transmitiendo la matriz a RViz
        pose_covariance = [0.0] * 36
        pose_covariance[0] = self.sigma[0, 0]    
        pose_covariance[7] = self.sigma[1, 1]    
        pose_covariance[35] = self.sigma[2, 2]   
        pose_covariance[1] = self.sigma[0, 1]    
        pose_covariance[6] = self.sigma[1, 0]    
        
        odom_msg.pose.covariance = pose_covariance
        self.odom_pub.publish(odom_msg)

    def update_localisation(self):
        self.compute_robot_velocities()
        self.propagate_covariance()
        self.integrate_odometry()
        self.publish_odometry()

def main(args=None):
    rclpy.init(args=args)
    node = EKFPhysical()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()