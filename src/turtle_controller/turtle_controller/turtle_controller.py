#!/usr/bin/env python3
import rclpy, time, math
import numpy as np 
from rclpy.node import Node
from geometry_msgs.msg import Twist # LIBRERIAS 
from turtlesim.msg import Pose

class TurtleController(Node): # Como en arduino el setup
    def __init__(self):
        super().__init__("turtle_controller")
        self.get_logger().info("Turtle controller node started!...")
      # self.t0 = time.time()
        self.sub = self.create_subscription(Pose, "/turtle1/pose", self.callback_turtle_pose, 1)
        self.pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 1)
        self.pose = None #Espacio en donde se puede declarar el tipo de valor que quieras.
        self.Kv = 2.0
        self.tolerance = 0.2
        self.L = 0.5
        rclpy.spin_once(self)
        
    def callback_turtle_pose(self, msg):
       self.pose = msg # Cada que cambie la pose se recibe el dato
        
    def go_to_point(self, target_x, target_y):
       msg = Twist()
       while True:
          if self.pose is not None:
             Dx, Dy = target_x - self.pose.x, target_y - self.pose.y
             e_dist = math.sqrt(Dx**2 + Dy**2)
             if abs(e_dist) < self.tolerance: self.pub.publish(Twist()); print("Target reached"); break
             e_ang = math.atan2(Dy,Dx) - self.pose.theta # Cálculo de la orientación deseada
             e_ang = math.atan2(math.sin(e_ang),math.cos(e_ang))
             msg.linear.x = 1.0
             msg.angular.z = self.Kv * e_ang
             self.pub.publish(msg)
             rclpy.spin_once(self) #Checa los mensajes
             time.sleep(0.02)  # Para ahorar ciclos del CPU
             print("Getting closer to position")
             
             
    def go_to_angle(self, target_theta):
       msg = Twist()
       while True:
          if self.pose is not None:
             e_ang = target_theta - self.pose.theta
             if abs(e_ang) < self.tolerance: self.pub.publish(Twist()); print("Orientation reached"); break
             e_ang = math.atan2(math.sin(e_ang),math.cos(e_ang))
             msg.angular.z = self.Kv * e_ang
             self.pub.publish(msg)
             rclpy.spin_once(self) #Checa los mensajes
             time.sleep(0.02)  # Para ahorar ciclos del CPU
             print("Getting closer to angle" + str(e_ang))
             
    def go_to_pursuite(self, target_x, target_y):
       msg = Twist()
       while True:
          if self.pose is not None:
             Dx, Dy = target_x - self.pose.x, target_y - self.pose.y
             e_dist = math.sqrt(Dx**2 + Dy**2)
             if abs(e_dist) < self.tolerance: self.pub.publish(Twist()); print("Target reached"); break
             sq = math.sin(self.pose.theta)
             cq = math.cos(self.pose.theta)
             w = ((Dy**cq)-(Dx**sq))/self.L
             v = (Dx+self.L*w*sq)/cq
             msg.linear.x = v
             msg.angular.z = w
             self.pub.publish(msg)
             rclpy.spin_once(self) #Checa los mensajes
             time.sleep(0.02)  # Para ahorar ciclos del CPU
             print("Position on pursuite")
       
    def principal(self):
       self.go_to_pursuite(2,2)
       self.go_to_pursuite(2,8)
       self.go_to_pursuite(8,8)
       self.go_to_pursuite(8,2)
       self.go_to_pursuite(2,2)
       
def main(args=None): # Como arduino el loop
    rclpy.init(args=args)
    nodeh = TurtleController()
    try: nodeh.principal()
    except Exception as error: print(error)
    except KeyboardInterrupt: print("Node terminated by user!")

if __name__ == "__main__":
    main()
