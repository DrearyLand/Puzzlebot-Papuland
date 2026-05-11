#!/usr/bin/env python3
import rclpy
import math
import numpy as np
from rclpy.node import Node
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0; aj /= 2.0; ak /= 2.0
    ci = math.cos(ai); si = math.sin(ai)
    cj = math.cos(aj); sj = math.sin(aj)
    ck = math.cos(ak); sk = math.sin(ak)
    cc = ci*ck; cs = ci*sk; sc = si*ck; ss = si*sk
    q = np.empty((4, ))
    q[0] = cj*sc - sj*cs; q[1] = cj*ss + sj*cc
    q[2] = cj*cs - sj*sc; q[3] = cj*cc + sj*ss
    return q

class LocalisationNode(Node):
    def __init__(self):
        super().__init__('localisation_node')
        
        ns = self.get_namespace().strip('/')
        self.prefix = f"{ns}/" if ns else ""
        
        self.declare_parameter('x0', 0.0)
        self.declare_parameter('y0', 0.0)
        
        self.r = 0.05
        self.l = 0.19
        self.x = float(self.get_parameter('x0').value)
        self.y = float(self.get_parameter('y0').value)
        self.theta = 0.0
        self.wr = 0.0
        self.wl = 0.0
        self.angle_r = 0.0
        self.angle_l = 0.0

        # MINICHALLENGE 4: Inicialización de Covarianza y Constantes de Ruido
        self.P = np.zeros((3, 3)) # Matriz de covarianza Sigma_k (3x3)
        self.kr = 10  # Valor semilla "inventado". SE CAMBIA TRAS EXPERIMENTO FÍSICO.
        self.kl = 10  # Valor semilla "inventado".

        self.create_subscription(Float32, 'wr', self.wr_callback, 10)
        self.create_subscription(Float32, 'wl', self.wl_callback, 10)
        
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.dt = 0.01
        self.create_timer(self.dt, self.update_odometry)

    def wr_callback(self, msg): self.wr = msg.data
    def wl_callback(self, msg): self.wl = msg.data

    def update_covariance(self, v, dt):

        # MINICHALLENGE 4: Propagación de Incertidumbre
        
        # 1. Jacobiano H_k
        J_h = np.array([
            [1.0, 0.0, -v * dt * math.sin(self.theta)],
            [0.0, 1.0,  v * dt * math.cos(self.theta)],
            [0.0, 0.0,  1.0]
        ])

        # 2. Matriz de ruido Q_k
        Sigma_delta = np.array([
            [self.kr * abs(self.wr), 0.0],
            [0.0, self.kl * abs(self.wl)]
        ])
        
        nabla_w = 0.5 * self.r * dt * np.array([
            [math.cos(self.theta), math.cos(self.theta)],
            [math.sin(self.theta), math.sin(self.theta)],
            [2.0/self.l, -2.0/self.l]
        ])
        
        Q = nabla_w @ Sigma_delta @ nabla_w.T

        # 3. Actualización de P (Sigma_k)
        self.P = J_h @ self.P @ J_h.T + Q

    def update_odometry(self):
        v = self.r * (self.wr + self.wl) / 2.0
        w = self.r * (self.wr - self.wl) / self.l
        
        # Actualizamos la matemática de la elipse ANTES de mover al robot
        self.update_covariance(v, self.dt)
        
        self.x += v * math.cos(self.theta) * self.dt
        self.y += v * math.sin(self.theta) * self.dt
        self.theta += w * self.dt
        
        self.angle_r += self.wr * self.dt
        self.angle_l += self.wl * self.dt
        
        current_time = self.get_clock().now().to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.theta)
        
        # Publicación de Odometría
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = f"{self.prefix}odom"
        odom.child_frame_id = f"{self.prefix}base_link"
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        
        # MINICHALLENGE 4: Llenado de matriz 6x6 (36 espacios)
        odom.pose.covariance = [0.0] * 36
        odom.pose.covariance[0]  = self.P[0, 0]  # var x
        odom.pose.covariance[7]  = self.P[1, 1]  # var y
        odom.pose.covariance[35] = self.P[2, 2]  # var theta
        odom.pose.covariance[1]  = self.P[0, 1]  # cov xy
        odom.pose.covariance[6]  = self.P[1, 0]  # cov yx
        odom.pose.covariance[5]  = self.P[0, 2]  # cov x_theta
        odom.pose.covariance[30] = self.P[2, 0]  # cov theta_x
        odom.pose.covariance[11] = self.P[1, 2]  # cov y_theta
        odom.pose.covariance[31] = self.P[2, 1]  # cov theta_y

        self.odom_pub.publish(odom)
        
        # TF
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = f"{self.prefix}odom"
        t.child_frame_id = f"{self.prefix}base_footprint"
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(t)
        
        # Joint States
        js = JointState()
        js.header.stamp = current_time
        js.name = ['wheel_l_joint', 'wheel_r_joint']
        js.position = [self.angle_l, self.angle_r]
        self.joint_pub.publish(js)

def main(args=None):
    rclpy.init(args=args)
    node = LocalisationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()