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
        
        # Configuración de Namespace para TF
        ns = self.get_namespace().strip('/')
        self.prefix = f"{ns}/" if ns else ""
        
        self.declare_parameter('x0', 0.0)
        self.declare_parameter('y0', 0.0)
        
        self.r = 0.05
        self.l = 0.19
        self.x = self.get_parameter('x0').value
        self.y = self.get_parameter('y0').value
        self.theta = 0.0
        self.wr = 0.0
        self.wl = 0.0
        self.angle_r = 0.0
        self.angle_l = 0.0

        self.create_subscription(Float32, 'wr', self.wr_callback, 10)
        self.create_subscription(Float32, 'wl', self.wl_callback, 10)
        
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.dt = 0.01
        self.create_timer(self.dt, self.update_odometry)

    def wr_callback(self, msg): self.wr = msg.data
    def wl_callback(self, msg): self.wl = msg.data

    def update_odometry(self):
        v = self.r * (self.wr + self.wl) / 2.0
        w = self.r * (self.wr - self.wl) / self.l
        
        self.x += v * math.cos(self.theta) * self.dt
        self.y += v * math.sin(self.theta) * self.dt
        self.theta += w * self.dt
        
        self.angle_r += self.wr * self.dt
        self.angle_l += self.wl * self.dt
        
        current_time = self.get_clock().now().to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.theta)
        
        # Odometry
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