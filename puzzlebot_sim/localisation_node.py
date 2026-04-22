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

# Función auxiliar para convertir Euler a Cuaterniones (necesario para RViz)
def quaternion_from_euler(ai, aj, ak):
    ai /= 2.0
    aj /= 2.0
    ak /= 2.0
    ci = math.cos(ai)
    si = math.sin(ai)
    cj = math.cos(aj)
    sj = math.sin(aj)
    ck = math.cos(ak)
    sk = math.sin(ak)
    cc = ci*ck
    cs = ci*sk
    sc = si*ck
    ss = si*sk
    q = np.empty((4, ))
    q[0] = cj*sc - sj*cs
    q[1] = cj*ss + sj*cc
    q[2] = cj*cs - sj*sc
    q[3] = cj*cc + sj*ss
    return q

class LocalisationNode(Node):
    def __init__(self):
        super().__init__('localisation_node')
        
        # Parámetros del Puzzlebot
        self.r = 0.05
        self.l = 0.19
        
        # Estado estimado (Odometría)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # Lectura de "encoders" simulados
        self.wr = 0.0
        self.wl = 0.0
        
        # Ángulos acumulados de las ruedas (Para que giren visualmente en RViz)
        self.angle_r = 0.0
        self.angle_l = 0.0

        # Suscriptores a las velocidades de las ruedas
        self.create_subscription(Float32, 'wr', self.wr_callback, 10)
        self.create_subscription(Float32, 'wl', self.wl_callback, 10)
        
        # Publicadores: Odometría, Transformadas y Estado de Articulaciones
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.dt = 0.01
        self.create_timer(self.dt, self.update_odometry)

    def wr_callback(self, msg):
        self.wr = msg.data

    def wl_callback(self, msg):
        self.wl = msg.data

    def update_odometry(self):
        # 1. Cinemática directa: Calcular v y w del chasis
        v = self.r * (self.wr + self.wl) / 2.0
        w = self.r * (self.wr - self.wl) / self.l
        
        # 2. Integrar posición (Dead Reckoning)
        self.x += v * math.cos(self.theta) * self.dt
        self.y += v * math.sin(self.theta) * self.dt
        self.theta += w * self.dt
        
        # Integrar ángulos de las llantas para la animación 3D
        self.angle_r += self.wr * self.dt
        self.angle_l += self.wl * self.dt
        
        current_time = self.get_clock().now().to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.theta)
        
        # 3. Publicar Odometry
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        self.odom_pub.publish(odom)
        
        # 4. Publicar Transformada (TF) odom -> base_footprint
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(t)
        
        # 5. Publicar JointStates para RViz (Asegúrate de que los nombres coincidan con tu URDF)
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