import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import LaserScan 
from geometry_msgs.msg import Twist
import numpy as np

class LaserScanSub(Node): 

    def __init__(self): 

        super().__init__('laser_scan_subscriber') 

        self.sub = self.create_subscription(LaserScan, "scan", self.lidar_cb, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.lidar = LaserScan() # Data from lidar will be stored here. 
        self.d_safety = 0.3 # Distance to keep from the closest object [m]
        self.kv = 1.0 # Linear speed proportional gain
        self.kw = 1.0 # Angular speed proportional gain
        self.robot_vel = Twist() # The required robot velocity
        timer_period = 0.1 #10hz
        self.timer = self.create_timer(timer_period, self.timer_callback) 
        self.get_logger().info("Node initialized!!!") 


    def timer_callback(self): 
        if self.lidar.ranges: #Check that you've received at least one message from Lidar
            #Hacer algo
            closest_range, theta_closest = self.get_closest_object()
            if np.isinf(closest_range):
                print("There are no objects around")
            else:
                print("closest_range", closest_range)
                print("theta_closest", theta_closest)
                d_diff = closest_range - self.d_safety
                # Create the closest object follower controllers
                v= self.kv*d_diff #Linear speed controller
                w= self.kw*theta_closest
                self.robot_vel.linear.x = v
                self.robot_vel.angular.z = w


        else:
            print("No Lidar data received")
    
    def get_closest_object(self):
        closest_range = min(self.lidar.ranges)
        closest_index = self.lidar.ranges.index(closest_range)
        theta_closest = self.lidar.angle_min + closest_index*self.lidar.angle_increment
        #Crop this angle to (-pi,pi)
        theta_closest = np.arctan2(np.sin(theta_closest), np.cos(theta_closest))
        return closest_range, theta_closest

    def lidar_cb(self, lidar_msg): 

        ## This function receives the ROS LaserScan message 

        self.lidar =  lidar_msg  

def main(args=None): 

    rclpy.init(args=args) 
    m_p=LaserScanSub() 
    rclpy.spin(m_p) 
    m_p.destroy_node() 
    rclpy.shutdown() 
 

if __name__ == '__main__': 

    main()