#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

def euler_from_quaternion(x, y, z, w):
    """Convierte cuaterniones a ángulos de Euler para obtener Theta."""
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)

class Bug0Waypoints(Node):
    def __init__(self):
        super().__init__('bug0_waypoints')
        
        # Estado de Pose del Robot
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # 1. MATRIZ DE WAYPOINTS (Circuito cerrado referenciado al mapa)
        self.waypoints = [
            (2.0, 1.0),   # Waypoint 1 (Coordenadas ajustables según odometría)
            (4.0, 3.0),   # Waypoint 2
            (1.0, 4.0),   # Waypoint 3
            (0.0, 0.0)    # Waypoint 4 (Retorno al origen)
        ]
        self.current_wp_index = 0
        
        # Carga cinemática del objetivo inicial
        self.target_x = self.waypoints[self.current_wp_index][0]
        self.target_y = self.waypoints[self.current_wp_index][1]
        
        # LiDAR - Regiones divididas para el control reactivo
        self.regions = {
            'right': 10.0,
            'fright': 10.0,
            'front': 10.0,
            'fleft': 10.0,
            'left': 10.0,
        }
        
        # Máquina de estados: 0 = Ir a la meta, 1 = Seguir pared, 2 = Detenido
        self.state = 0 
        
        # Parámetros de control algorítmico
        self.d_thresh = 0.4        # Umbral de colisión frontal
        self.goal_thresh = 0.15    # Umbral de llegada (15 cm de tolerancia euclidiana)
        
        # Suscriptores y publicadores
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.create_timer(0.1, self.control_loop)
        self.get_logger().info(f'Iniciando navegación. Objetivo 1: ({self.target_x}, {self.target_y})')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.theta = euler_from_quaternion(q.x, q.y, q.z, q.w)

    def scan_callback(self, msg):
        ranges = msg.ranges
        ranges = [r if not math.isinf(r) and not math.isnan(r) else 10.0 for r in ranges]
        
        length = len(ranges)
        self.regions = {
            'front':  min(min(ranges[0:15] + ranges[-15:]), 10.0),
            'fleft':  min(min(ranges[16:75]), 10.0),
            'left':   min(min(ranges[76:105]), 10.0),
            'right':  min(min(ranges[-105:-76]), 10.0),
            'fright': min(min(ranges[-75:-16]), 10.0),
        }

    def change_state(self, state):
        if state is not self.state:
            self.get_logger().info(f'Transición de estado cinemático: {state}')
            self.state = state

    def control_loop(self):
        msg = Twist()
        
        # Cálculo del vector de error (Distancia y Orientación)
        dist_to_goal = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        angle_to_goal = math.atan2(self.target_y - self.y, self.target_x - self.x)
        
        err_theta = angle_to_goal - self.theta
        err_theta = math.atan2(math.sin(err_theta), math.cos(err_theta))

        # 2. EVALUACIÓN LÓGICA DE WAYPOINTS
        if dist_to_goal < self.goal_thresh:
            self.get_logger().info(f'¡Waypoint {self.current_wp_index + 1} alcanzado exitosamente!')
            self.current_wp_index += 1
            
            # Verificación de completitud del arreglo de ruta
            if self.current_wp_index >= len(self.waypoints):
                self.change_state(2) 
                self.get_logger().info('Circuito cerrado completado. Interrumpiendo tracción.')
                self.cmd_pub.publish(Twist())
                return
            
            # Asignación del nuevo vector objetivo
            self.target_x = self.waypoints[self.current_wp_index][0]
            self.target_y = self.waypoints[self.current_wp_index][1]
            self.get_logger().info(f'Ajustando trayectoria hacia Waypoint {self.current_wp_index + 1}: ({self.target_x}, {self.target_y})')
            
            # Restablecer la máquina de estados a seguimiento directo
            self.change_state(0)
            return

        # Interrupción de seguridad
        if self.state == 2:
            self.cmd_pub.publish(Twist())
            return

        # ---------------------------------------------------------
        # INTEGRACIÓN BUG 0 ORIGINAL
        # ---------------------------------------------------------
        if self.state == 0: 
            if self.regions['front'] < self.d_thresh:
                self.change_state(1)
                
        elif self.state == 1: 
            if self.regions['front'] > self.d_thresh and abs(err_theta) < 0.2:
                self.change_state(0)

        # Matriz de accionamiento (Planta del sistema)
        if self.state == 0:
            if abs(err_theta) > 0.2:
                msg.linear.x = 0.0
                msg.angular.z = 0.3 if err_theta > 0 else -0.3
            else:
                msg.linear.x = 0.2
                msg.angular.z = 0.0
                
        elif self.state == 1:
            if self.regions['front'] < self.d_thresh:
                msg.linear.x = 0.0
                msg.angular.z = 0.5
            elif self.regions['fright'] < self.d_thresh:
                msg.linear.x = 0.1
                msg.angular.z = 0.2
            elif self.regions['right'] < self.d_thresh:
                msg.linear.x = 0.2
                msg.angular.z = 0.0
            else:
                msg.linear.x = 0.1
                msg.angular.z = -0.3

        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = Bug0Waypoints()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()