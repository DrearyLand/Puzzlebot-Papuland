#Este nodo nos ayudará a sacar el índice de desempeño de nuestro motor
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import numpy as np

class MyClassNode(Node):
    def __init__(self):
    	super().__init__("ind_des") # Inicializa el nodo
    
    	self.sub_output = self.create_subscription(Float32, "motor_output", self.output_callback, 3) # Suscriptor velocidad
    	self.sub_input = self.create_subscription(Float32, "motor_input", self.input_callback, 3) # Suscriptor Valor deseado
    	self.sub_time = self.create_subscription(Float32, "time", self.time_callback, 3) # Suscriptor tiempo
    	
    	self.time = 0.0
    	self.input = 0.0
    	self.output = 0.0
    	self.valorescalon = 3.0
    	self.mp = 0.0
    	self.tp = 0.0
    	self.ts = 0.0
    	self.tr = 0.0
    	self.tiempo_inicio = 0.0
    	self.binicio = 0.0
    	
    	self.error = 0.0
    	
    	
    	self.sq_error = 0.0
    	
    	self.error_anterior = 0.0
    	self.sq_error_anterior= 0.0
    	
    	
    	self.ise = 0.0
    	self.iae = 0.0
    	
    	self.ts_list = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    	self.time_list = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    	self.indice = 0
    	
    	self.tr_first = True
    	self.ts_first = True
    	self.bprint = True
    	
    	
    def output_callback(self, msg):
    	self.output = msg.data
    	
    	self.ts_list[self.indice] = self.output
    	self.time_list[self.indice] = self.time
    	self.indice += 1
    	
    	if(self.indice > 19):
    		self.indice = 0
    	
    	promedio = sum(self.ts_list) / len(self.ts_list)
    	if(promedio < self.input*1.05 and promedio > self.input*0.95 and self.ts_first):
    		self.ts = self.time_list[0]
    		self.ts_first = False
    	
    	# Máximo sobreimpulso/tiempo pico
    	if(self.output > self.mp and self.output >  self.valorescalon):
    		self.mp = ((self.output*100)/self.valorescalon)-100
    		self.tp = self.time
    		
    		
    	if(self.output > 0.1 and self.binicio):
    		self.tiempo_inicio = self.time
    		self.binicio = False
    	
    	# Tiempo de respuesta
    	if(self.output > self.valorescalon and self.tr_first):
    		self.tr = self.time 
    		self.tr_first = False
    	
    	if(self.ts_first == False and self.bprint):
    	
    		self.ise = (self.ise/2)*0.05
    		self.iae = (self.iae/2)*0.05
    	
    		self.get_logger().info("Mp: " + str(self.mp) + "%")
    		self.get_logger().info("tp: " + str(self.tp))
    		self.get_logger().info("ts: " + str(self.ts))
    		self.get_logger().info("tr: " + str(self.tr))
    		
    		self.get_logger().info("ISE: " + str(self.ise))
    		self.get_logger().info("IAE: " + str(self.iae))
    		
    		self.bprint = False
    	
    	    
       
    def input_callback(self, msg):
    	self.input = msg.data
    
    def time_callback(self, msg):
        self.time = msg.data-3
        
        		
        self.error = self.input - self.output
        self.sq_error = self.error**2
        self.sq_error_anterior = self.error_anterior**2

    	
        self.ise += self.sq_error + self.sq_error_anterior
        
        self.iae += abs(self.error + self.error_anterior)
    	
        self.error_anterior = self.error
    	


def main(args=None):
	rclpy.init(args=args)
	nodeh = MyClassNode()
	
	try: rclpy.spin(nodeh) # Continua el nodo
	except Exception as error: print(error)
	except KeyboardInterrupt: print("Node terminated!") #

if __name__ == '__main__':
    main()

