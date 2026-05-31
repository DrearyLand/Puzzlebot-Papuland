#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

def euler_from_quaternion(x, y, z, w):
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)

class Bug2Waypoints(Node):
    def __init__(self):
        super().__init__('bug2_waypoints')
        
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # 1. MATRIZ DE WAYPOINTS
        self.waypoints = [
            (2.0, 1.0),
            (4.0, 3.0),
            (1.0, 4.0),
            (0.0, 0.0)
        ]
        self.current_wp_index = 0
        
        # 2. PUNTOS START Y GOAL (Para calcular la M-Line)
        self.start_x = 0.0
        self.start_y = 0.0
        self.target_x = self.waypoints[self.current_wp_index][0]
        self.target_y = self.waypoints[self.current_wp_index][1]
        
        # Memoria de impacto (Distancia a la meta cuando chocó)
        self.hit_distance = 0.0
        
        self.regions = {
            'right': 10.0, 'fright': 10.0, 'front': 10.0, 'fleft': 10.0, 'left': 10.0,
        }
        
        self.state = 0 # 0 = Ir a meta, 1 = Seguir pared, 2 = Detenido
        
        self.d_thresh = 0.4
        self.goal_thresh = 0.15
        
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.create_timer(0.1, self.control_loop)
        self.get_logger().info(f'Navegación BUG 2 Iniciada. M-Line trazada a WP 1.')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.theta = euler_from_quaternion(q.x, q.y, q.z, q.w)

    def scan_callback(self, msg):
        ranges = msg.ranges
        ranges = [r if not math.isinf(r) and not math.isnan(r) else 10.0 for r in ranges]
        self.regions = {
            'front':  min(min(ranges[0:15] + ranges[-15:]), 10.0),
            'fleft':  min(min(ranges[16:75]), 10.0),
            'left':   min(min(ranges[76:105]), 10.0),
            'right':  min(min(ranges[-105:-76]), 10.0),
            'fright': min(min(ranges[-75:-16]), 10.0),
        }

    def change_state(self, state):
        if state is not self.state:
            self.get_logger().info(f'Bug 2 Transición de estado: {state}')
            self.state = state

    def distance_to_mline(self):
        """Calcula la distancia perpendicular del robot a la M-Line actual."""
        A = self.target_y - self.start_y
        B = -(self.target_x - self.start_x)
        C = (self.target_y * self.start_x) - (self.target_x * self.start_y)
        
        denominador = math.sqrt(A**2 + B**2)
        if denominador == 0:
            return 0.0
        
        d_mline = abs(A * self.x + B * self.y + C) / denominador
        return d_mline

    def control_loop(self):
        msg = Twist()
        dist_to_goal = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        angle_to_goal = math.atan2(self.target_y - self.y, self.target_x - self.x)
        
        err_theta = angle_to_goal - self.theta
        err_theta = math.atan2(math.sin(err_theta), math.cos(err_theta))

        # EVALUACIÓN LÓGICA DE WAYPOINTS
        if dist_to_goal < self.goal_thresh:
            self.get_logger().info(f'¡Waypoint {self.current_wp_index + 1} alcanzado!')
            self.current_wp_index += 1
            
            if self.current_wp_index >= len(self.waypoints):
                self.change_state(2) 
                self.get_logger().info('Circuito Bug 2 completado.')
                self.cmd_pub.publish(Twist())
                return
            
            # El punto actual se convierte en el nuevo Start para la M-Line
            self.start_x = self.x
            self.start_y = self.y
            
            self.target_x = self.waypoints[self.current_wp_index][0]
            self.target_y = self.waypoints[self.current_wp_index][1]
            self.change_state(0)
            return

        if self.state == 2:
            self.cmd_pub.publish(Twist())
            return

        # ---------------------------------------------------------
        # LÓGICA ESTRICTA DE BUG 2
        # ---------------------------------------------------------
        if self.state == 0: 
            # Si choca, cambia de estado y GUARDA la distancia al objetivo
            if self.regions['front'] < self.d_thresh:
                self.hit_distance = dist_to_goal
                self.get_logger().info(f'Obstáculo. d_hit = {self.hit_distance:.2f}m')
                self.change_state(1)
                
        elif self.state == 1:
            # CONDICIÓN DE SALIDA BUG 2: Tocar la M-Line estando MÁS CERCA de la meta
            d_mline = self.distance_to_mline()
            
            # Tolerancia de 0.15m para detectar la línea, y debe estar al menos 0.2m más cerca que cuando chocó
            if d_mline < 0.15 and dist_to_goal < (self.hit_distance - 0.2):
                self.get_logger().info('¡M-Line interceptada más cerca de la meta! Abandonando obstáculo.')
                self.change_state(0)

        # Matriz de accionamiento
        if self.state == 0:
            if abs(err_theta) > 0.2:
                msg.linear.x = 0.0
                msg.angular.z = 0.3 if err_theta > 0 else -0.3
            else:
                msg.linear.x = 0.2
                msg.angular.z = 0.0
                
        elif self.state == 1:
            # Wall Following Clásico (Izquierda)
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
    node = Bug2Waypoints()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()