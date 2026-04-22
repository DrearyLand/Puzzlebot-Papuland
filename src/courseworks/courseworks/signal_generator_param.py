import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from my_interfaces.msg import SignalParams
from math import sin, pi
from scipy.signal import sawtooth

def sign(x): #para verificar si un valor es positivo o negativo 
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

class MyClassNode(Node):    
    def __init__(self):
        super().__init__('signal_generator_param')
        self.get_logger().info('Initializing signal generator node')  # Imprimir mensaje para indicar que el nodo se está inicializando
        self.declare_parameters(namespace = "",parameters = [
            ("frequency", rclpy.Parameter.Type.DOUBLE),
            ("amplitude", rclpy.Parameter.Type.DOUBLE),
            ("signal_type", rclpy.Parameter.Type.INTEGER),
            ("offset", rclpy.Parameter.Type.DOUBLE),
            ])
        
        self.t = 0.0 #inicia una variable t que va a servir para el tiempo
        
        self.periodo_tiempo1khz = 1.0 / 1000 #calcular el periodo de tiempo equivalente a 1 k Hz
        self.periodo_tiempo10hz = 1.0 / 10 #calcular el periodo de tiempo equivalente a 10 Hz

        self.signal_pub = self.create_publisher(Float32, '/signal', 1)  # Crear un publicador en el tema /signal
        self.signal_params_pub = self.create_publisher(SignalParams, '/signal_params', 1)  # Crear un publicador en el tema /signal_params

        self.timer = self.create_timer(self.periodo_tiempo1khz, self.generate_signal) #Se manda a llamar a la funcino generate signal cada periodo de tiempo
        # Crear un temporizador para verificar si el valor de signal_type ha cambiado
        self.signal_pub_10 = self.create_timer(self.periodo_tiempo10hz, self.publish_signal_params)
        self.prueba=0
        

    def publish_signal_params(self):
         
        # Función para publicar todos los parámetros en el tema /signal_params
        signal_type = self.get_parameter("signal_type").value
        amplitude = self.get_parameter("amplitude").value
        frequency = self.get_parameter("frequency").value
        offset = self.get_parameter("offset").value
        msg = SignalParams()  # Para almacenar y enviar los parámetros de la señal

        #Construir el mensaje con los datos de los parametros
        msg.signal_type = signal_type 
        msg.amplitude = amplitude
        msg.frequency = frequency
        msg.offset = offset
        msg.tiempo = self.t

        #Para mandar datos a 10 Hz (se alenta el temporizador)
        self.signal_params_pub.publish(msg)



    def generate_signal(self):
        # Generar la señal en función del valor actual de signal_type

        #Obtener los valores de los parametros
        self.signal_type = self.get_parameter("signal_type").value
        self.frequency = self.get_parameter("frequency").value
        self.amplitude = self.get_parameter("amplitude").value
        self.offset = self.get_parameter("offset").value

        #Definir la ecuacion dependiendo signal_type
        if self.signal_type == 1:  # senoidal
            signal_func = float(sin(2*pi*self.t))
        elif self.signal_type == 2:  # cuadrada
            signal_func = float(sign(sin(2*pi*self.t)))
        elif self.signal_type == 3:  # diente de sierra
            signal_func = float(sawtooth(2 * pi *self.t))
        elif self.signal_type == 4:  # triangular modificada
            signal_func = float(sawtooth(2 * pi *self.t) * 2)
        elif self.signal_type == 5:  # sinusoidal amortiguada
            decay_factor = 0.1  # Factor de amortiguación (debe estar entre 0 y 1)
            signal_func = float(sin(2*pi* self.t) * decay_factor**self.t)
        else:
            raise ValueError('Invalid signal type')
        
        signal_value = signal_func

        #Pulicar
        self.signal_pub.publish(Float32(data=signal_value)) 
        #Cambiar tiempo
        self.t += self.periodo_tiempo1khz  
    
    


def main(args=None):
    rclpy.init(args=args) #Inicializar el nodo
    nodeh = MyClassNode() #Crear el nodo
    
    try: rclpy.spin(nodeh) #para dejarlo vivo aunque no haga nada 
    except Exception as error: print(error)
    except KeyboardInterrupt: print ("Signal Generator Param Node terminated!")

if __name__ == '__main__':
    main()
