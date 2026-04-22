import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from my_interfaces.msg import SignalParams
from math import sin, pi
from scipy.signal import sawtooth


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    
class MyClassNode(Node):    
    def __init__(self):
        super().__init__('reconstruction_param')
        self.get_logger().info('Initializing reconstruction param node')

        self.periodo_tiempo1khz = 1.0 / 1000
        self.t = 0.0
        self.signal_func = None  # Crear la variable signal_func
        self.amplitude =0.0
        self.frequency =0.0
        self.offset=0.0
        self.signal_type=0

        # Definir al canal al que se suscribe el nodo
        self.signal_sub = self.create_subscription(SignalParams, '/signal_params', self.signal_callback, 1)

        # Crear un publicador con canal llamado /signal_reconstructed
        self.signal_pub = self.create_publisher(Float32, '/signal_reconstructed', 1)

        # Crear un temporizador específico para la publicación de la señal reconstruida
        self.reconstruction_timer = self.create_timer(self.periodo_tiempo1khz, self.publish_reconstructed_signal)



    def signal_callback(self, msg):
        # Obtener los valores que vienen en msg del canal
        self.amplitude = msg.amplitude
        self.frequency = msg.frequency
        self.offset = msg.offset
        self.signal_type = msg.signal_type
        self.t=msg.tiempo


        
    def publish_reconstructed_signal(self):
        # Definir la ecuación dependiendo de signal_type
        if self.signal_type == 1:  # senoidal
            signal_func = float(self.amplitude * sin(2 * pi * self.frequency * self.t) + self.offset)
        elif self.signal_type == 2:  # cuadrada
            signal_func = float(self.amplitude * sign(sin(2 * pi * self.frequency * self.t)) + self.offset)
        elif self.signal_type == 3:  # diente de sierra
            signal_func = float(self.amplitude * sawtooth(2 * pi * self.frequency * self.t) + self.offset)
        elif self.signal_type == 4:  # triangular modificada
            signal_func = float(self.amplitude * sawtooth(2 * pi * self.frequency * self.t) * 2 + self.offset)
        elif self.signal_type == 5:  # sinusoidal amortiguada
            decay_factor = 0.1  # Factor de amortiguación (debe estar entre 0 y 1)
            signal_func = float(self.amplitude * sin(2 * pi * self.frequency * self.t) * decay_factor**self.t + self.offset)
        else:
            signal_func=0.0
            self.get_logger().info("No se recibio infromacion")
        
        signal_value = signal_func

        #Pulicar
        self.signal_pub.publish(Float32(data=signal_value)) 
        self.t += self.periodo_tiempo1khz
        
def main(args=None):
    rclpy.init(args=args) #Inicializar el nodo
    nodeh = MyClassNode() #Crear el nodo
    
    try: rclpy.spin(nodeh) #para dejarlo vivo aunque no haga nada 
    except Exception as error: print(error)
    except KeyboardInterrupt: print ("Reconstruction param Node terminated!")

if __name__ == '__main__':
    main()
