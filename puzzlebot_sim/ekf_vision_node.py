#!/usr/bin/env python3
import rclpy
import math
import numpy as np
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from geometry_msgs.msg import TransformStamped
from aruco_opencv_msgs.msg import ArucoDetection # Mensaje oficial del paquete de MCR2

def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0; aj /= 2.0; ak /= 2.0
    ci = math.cos(ai); si = math.sin(ai)
    cj = math.cos(aj); sj = math.sin(aj)
    ck = math.cos(ak); sk = math.sin(ak)
    return [cj*sc - sj*cs, cj*ss + sj*cc, cj*cs - sj*sc, cj*cc + sj*ss]

class EKFLocalisation(Node):
    def __init__(self):
        super().__init__('ekf_vision_node')
        
        # Parámetros mecánicos
        self.r = 0.05
        self.l = 0.19
        
        # 1. VECTOR DE ESTADO (X, Y, Theta)
        self.mu = np.zeros((3, 1))
        
        # 2. MATRIZ DE COVARIANZA P (Incertidumbre inicial)
        self.P = np.eye(3) * 0.01 
        
        # 3. MATRIZ DE RUIDO DEL SISTEMA Q (Ruido de las llantas, probablemente hay que cambiarlos en el físico)
        self.Q = np.array([
            [0.005, 0.0,   0.0],
            [0.0,   0.001, 0.0],
            [0.0,   0.0,   0.01]
        ])
        
        # 4. MATRIZ DE RUIDO DE MEDICIÓN R (Ruido de la cámara)
        self.R = np.array([
            [0.05, 0.0],  # Ruido midiendo la distancia
            [0.0,  0.05]  # Ruido midiendo el ángulo
        ])

        # 5. EL DICCIONARIO DEL MAPA ABSOLUTO 
        # Hay que modificar las coordenadas según corresponda (están de ejemplo)
        self.aruco_map = {
            70:  (1.0, 1.0),
            706: (2.0, 4.0),
            75:  (5.0, 5.0),
            701: (6.0, 2.0),
            703: (4.0, 1.5),
            705: (3.0, -1.0),
            708: (5.0, -2.0),
            702: (1.0, -3.0)
        }

        self.wr = 0.0
        self.wl = 0.0
        self.dt = 0.1 # 10 Hz

        # Suscripciones
        self.create_subscription(Float32, '/VelocityEncR', self.wr_callback, 10)
        self.create_subscription(Float32, '/VelocityEncL', self.wl_callback, 10)
        
        # Suscripción a la visión (El paquete de MCR2)
        self.create_subscription(ArucoDetection, '/aruco_detections', self.vision_callback, 10)
        
        # Publicador de la Odometría corregida
        self.odom_pub = self.create_publisher(Odometry, '/odom_est', 10)
        
        self.create_timer(self.dt, self.ekf_predict_step)
        self.get_logger().info('Filtro Extendido de Kalman ONLINE.')

    def wr_callback(self, msg):
        self.wr = msg.data

    def wl_callback(self, msg):
        self.wl = msg.data

    def ekf_predict_step(self):
        """FASE 1: PREDICCIÓN (Basada en la cinemática de las llantas)"""
        v = self.r * (self.wr + self.wl) / 2.0
        w = self.r * (self.wr - self.wl) / self.l
        
        theta = self.mu[2, 0]
        
        # 1. Predecir nuevo estado
        self.mu[0, 0] += v * math.cos(theta) * self.dt
        self.mu[1, 0] += v * math.sin(theta) * self.dt
        self.mu[2, 0] += w * self.dt
        
        # 2. Jacobiano del sistema (H)
        J_F = np.array([
            [1.0, 0.0, -v * math.sin(theta) * self.dt],
            [0.0, 1.0,  v * math.cos(theta) * self.dt],
            [0.0, 0.0,  1.0]
        ])
        
        # 3. Predecir nueva covarianza (La elipse crece)
        distancia_paso = abs(v) * self.dt
        self.P = J_F @ self.P @ J_F.T + (self.Q * distancia_paso)
        
        self.publish_odometry()

    def vision_callback(self, msg):
        """FASE 2: ACTUALIZACIÓN (Ocurre solo cuando detecta un ArUco)"""
        for marker in msg.markers:
            m_id = marker.marker_id
            
            if m_id in self.aruco_map:
                # Coordenadas reales del marcador en el mapa
                m_x, m_y = self.aruco_map[m_id]
                
                # Posición actual estimada del robot
                rx = self.mu[0, 0]
                ry = self.mu[1, 0]
                rtheta = self.mu[2, 0]
                
                # Z: Medición de la cámara (Distancia Euclidiana 2D)
                # Extraemos la posición relativa desde el mensaje pose
                dx_cam = marker.pose.position.x
                dz_cam = marker.pose.position.z 
                d_medido = math.sqrt(dx_cam**2 + dz_cam**2)
                phi_medido = math.atan2(dx_cam, dz_cam) # Ángulo relativo
                
                Z = np.array([[d_medido], [phi_medido]])
                
                # Z_esperado: Lo que el robot DEBERÍA ver según sus cálculos
                dx_map = m_x - rx
                dy_map = m_y - ry
                d_esperado = math.sqrt(dx_map**2 + dy_map**2)
                phi_esperado = math.atan2(dy_map, dx_map) - rtheta
                
                # Normalizar ángulo
                phi_esperado = math.atan2(math.sin(phi_esperado), math.cos(phi_esperado))
                Z_esperado = np.array([[d_esperado], [phi_esperado]])
                
                # Innovación (El error visual)
                Y = Z - Z_esperado
                Y[1, 0] = math.atan2(math.sin(Y[1, 0]), math.cos(Y[1, 0])) # Normalizar
                
                # Jacobiano de observación (H)
                if d_esperado > 0.01:
                    H = np.array([
                        [-(dx_map)/d_esperado,    -(dy_map)/d_esperado,    0.0],
                        [(dy_map)/(d_esperado**2), -(dx_map)/(d_esperado**2), -1.0]
                    ])
                    
                    # Calcular Ganancia de Kalman (K)
                    S = H @ self.P @ H.T + self.R
                    K = self.P @ H.T @ np.linalg.inv(S)
                    
                    # Actualizar Estado (Corregir posición)
                    self.mu = self.mu + (K @ Y)
                    self.mu[2, 0] = math.atan2(math.sin(self.mu[2, 0]), math.cos(self.mu[2, 0]))
                    
                    # Actualizar Covarianza (La elipse se encoje)
                    I = np.eye(3)
                    self.P = (I - K @ H) @ self.P
                    
                    self.get_logger().info(f'¡ArUco {m_id} fusionado! Elipse colapsada.')

    def publish_odometry(self):
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        
        odom.pose.pose.position.x = float(self.mu[0, 0])
        odom.pose.pose.position.y = float(self.mu[1, 0])
        q = quaternion_from_euler(0.0, 0.0, float(self.mu[2, 0]))
        
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        
        # Publicar la matriz de covarianza P aplanada para RVIZ
        odom.pose.covariance = [0.0] * 36
        odom.pose.covariance[0]  = self.P[0, 0]  
        odom.pose.covariance[7]  = self.P[1, 1]  
        odom.pose.covariance[35] = self.P[2, 2]  
        odom.pose.covariance[1]  = self.P[0, 1]  
        odom.pose.covariance[6]  = self.P[1, 0]  
        
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = EKFLocalisation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()