#!/usr/bin/env pyhton3
import rclpy
from rclpy.node import Node

class YamlParamReader(Node):
	def __int__(self):
		super().__init__("yaml_reader_parameters")
		self.get_logger().info("Node has been started ...")
		
		self.declare_parameters(namespace = "", parameters = [
			("bool_value", rclpy.Parameter.Type.BOOL),
			("int_value", rclpy.Parameter.Type.INTEGER),
			("float_value", rclpy.Parameter.Type.DOUBLE),
			("str_value", rclpy.Parameter.Type.STRING),
			("nested_param.another_int", rclpy.Parameter.Type.INTEGER),
			("nested_param.another_float", rclpy.Parameter.Type.DOUBLE),
		])

def main(args=None):
	rclpy.init(args=args)
	nodeh = YamlParamReader()
	
	try: rclpy.spin(nodeh)
	except Exception as error: print(error)
	except KeyboardInterrupt: print("Node terminated by user!")
	
if __name__ == "__main__":
	main()
