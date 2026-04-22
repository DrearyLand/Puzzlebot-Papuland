import rclpy 

from rclpy.node import Node 

from sensor_msgs.msg import LaserScan 


class LaserScanSub(Node): 

    def __init__(self): 

        super().__init__('laser_scan_subscriber') 

        self.sub = self.create_subscription(LaserScan, "scan", self.lidar_cb, 10) 
        self.lidar = LaserScan() # Data from lidar will be stored here. 
        timer_period = 1.0 
        self.timer = self.create_timer(timer_period, self.timer_callback) 
        self.get_logger().info("Node initialized!!!") 


    def timer_callback(self): 

        print("Add some code to print the required data here:")
        angle_min 
        angle_max 
        range_min 
        range_max 
        header.frame_id 
        The first component inside the ranges[] array.  
        The last component inside the intensities[] array. 
        #### ADD YOUR CODE ### 

 

 

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