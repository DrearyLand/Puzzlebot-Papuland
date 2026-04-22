import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math
import numpy as np

periodo_tiempo = 10.0 #Periodo	

class MyClassNode(Node):
    def __init__(self): #constructor
        super().__init__('process') #Construye el nodo    
        self.sub_time = self.create_subscription(Float32, '/time', self.time_callback, 5) #Suscripción a canal time
        self.sub_signal = self.create_subscription(Float32, '/signal', self.signal_callback, 5) #Suscripción a canal signal
        self.pub = self.create_publisher(Float32, '/proc_signal', 5) #Publicar el proc_signal
        self.mover = 1.5  # Mueve la señal de arriba a abajo (offset)
        self.amplitud = 0.5 #Amplitud de señal
        self.desplazamiento = math.pi #Desfase/desplazamiento

        
    def time_callback(self, msg):
        global tiempo
        tiempo= self.tiempo_actual = msg.data  # Obtener el tiempo

    def signal_callback(self, msg):
        arcos = float(math.asin(msg.data))
        processed_sig = float(self.amplitud * np.sin(arcos + self.desplazamiento) + self.mover)  # Desplazamiento en Y y amplitud 

        message = Float32() # Crear un objeto Float32 y asignarle el valor procesado
        message.data = processed_sig
        self.pub.publish(message) # Publicar el mensaje procesado
        self.get_logger().info("Processed Signal: "+ str(processed_sig) + " Tiempo: " + str(tiempo))
        

def main(args=None):
    rclpy.init(args=args)
    nodeh = MyClassNode()
    
    try: rclpy.spin(nodeh) #Lo mantiene activo
    except Exception as error: print(error)
    except KeyboardInterrupt: print ("Node terminated!")

if __name__ == '__main__':
    main()
