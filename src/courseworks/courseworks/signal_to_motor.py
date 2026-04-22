#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math

periodo_tiempo = 0.1  # cambiar los 10 Hz a segundos 

class MyClassNode(Node):
    def __init__(self): #constructor
        global periodo_tiempo
        super().__init__('signal_to_motor') #crea el nodo     
        self.tiempo_anterior = 0.0
        self.pub = self.create_publisher(Float32, '/motor_input', 10) # para publicar la senal con canal llamado /signal 
        self.create_timer(periodo_tiempo, self.timer_callback) #se va a llamar la funcion cada que se cumpla el periodo de tiempo
        self.periodo= 4.0 #1 ciclo por x segundos
        self.offset = .5
        self.amplitud= .1

    def timer_callback(self):
        global periodo_tiempo
        signal_dato = Float32() #crear la variable para la senal siendo un float de 32
        time_dato = Float32() #crear la variable para el tiempo siendo un float de 32
        signal_dato.data = self.amplitud*math.sin((2*math.pi*self.periodo)*self.tiempo_anterior) + self.offset# signal_data= sin(t_anterior)



        message = "Signal: " + str(signal_dato.data)
        self.get_logger().info(message) #imprimir el resultado en la terminal 

        self.pub.publish(signal_dato) #publicar el dato de la senal
        self.tiempo_anterior += periodo_tiempo #actualizar el tiempo

def main(args=None):
    rclpy.init(args=args) # comunicarnos con nodo
    nodeh = MyClassNode() 
    try: rclpy.spin(nodeh) #para dejarlo vivo aunque no haga nada 
    except Exception as error: print(error)
    except KeyboardInterrupt: print ("Node terminated!")

if __name__ == '__main__':
    main()
