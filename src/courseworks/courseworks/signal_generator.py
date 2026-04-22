#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math

periodo_tiempo = 1.0 / 10  # Cambia los 10 Hz a segundos

class MyClassNode(Node):
    def __init__(self): #Constructor
        global periodo_tiempo
        super().__init__('signal_generator') #Crea el nodo     
        self.tiempo_anterior = 0.0 
        self.pub = self.create_publisher(Float32, '/signal', 5) # Publica la señal con nuestro canal /signal 
        self.time_pub = self.create_publisher(Float32, '/time', 5) #Publica el tiempo con nuestro canal /time
        self.create_timer(periodo_tiempo, self.timer_callback) #Se va a llamar la funcion cada que se cumpla el periodo de tiempo
        self.periodo=5 #1 ciclo por x segundos

    def timer_callback(self):
        global periodo_tiempo
        signal_dato = Float32() #Crea la variable para la senal siendo un float de 32
        time_dato = Float32() #Crea la variable para el tiempo siendo un float de 32
        signal_dato.data = 1*math.sin((2*math.pi)/10*self.tiempo_anterior+0)+0 # signal_data= sin(t_anterior) 1 es amplitud 10 es periodo 0 es desfase 0 es offset
        time_dato.data = self.tiempo_anterior #Obtiene el valor del tiempo
        self.pub.publish(signal_dato) #Publica el dato de la senal
        self.time_pub.publish(time_dato) #Publica el tiempo
        
        message = "Signal: " + str(signal_dato.data) + " Time: " + str(time_dato.data)
        self.get_logger().info(message) #Imprime el resultado 
        self.tiempo_anterior += periodo_tiempo #Actualiza el tiempo

def main(args=None):
    rclpy.init(args=args) #Comunicación con el nodo
    nodeh = MyClassNode() 
    try: rclpy.spin(nodeh) #La mantiene activa
    except Exception as error: print(error)
    except KeyboardInterrupt: print ("Node terminated!")

if __name__ == '__main__':
    main()
