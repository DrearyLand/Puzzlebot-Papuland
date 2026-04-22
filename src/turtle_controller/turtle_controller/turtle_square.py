#!/usr/bin/env pyhton3
import rclpy, time, math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class NodoCuadrado(Node):
    def __init__(self, vel_angular):
        super().__init__("NodoCuadrado")
        self.get_logger().info("¡Iniciando el nodo del cuadrado!...")
        self.vel_angular = vel_angular  # Velocidad Angular para rotación
        self.t0 = time.time()  # Tiempo inicial
        self.timer = self.create_timer(0.01, self.callback_controlador)  # Temporizador para el controlador
        self.pub = self.create_publisher(Twist, "/cmd_vel", 1)  # Publicador para enviar comandos de velocidad
        self.pose = Pose()  # Pose actual del robot
        self.tiempo_giro = (math.pi / 2) / self.vel_angular  # Tiempo necesario para girar 90 grados
        self.longitud_lado = 2.8  # Longitud del lado del cuadrado
        self.lado_actual = 0  # Lado actual del cuadrado
        self.tiempo_transcurrido = 0  # Tiempo transcurrido

    def callback_controlador(self):
        msg = Twist()
        self.tiempo_transcurrido = time.time() - self.t0  # Calcular el tiempo transcurrido

        if self.lado_actual < 8:  # Verificar si aún no se ha completado el cuadrado
            if self.tiempo_transcurrido < self.tiempo_giro - 2 / 1.0 and self.lado_actual % 2 == 0:
                msg.linear.x = self.vel_angular # Avanzar longitud_lado
            elif self.tiempo_transcurrido < self.tiempo_giro - 2 and self.lado_actual % 2 != 0:
                msg.angular.z = self.vel_angular # Giro de 90 grados
            else:
                self.lado_actual += 1
                self.t0 = time.time()  # Reiniciar el tiempo inicial
        else:
            # Se pone en 0 la velocidad lineal y la velocidad angular
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            print("Se ha completado la tarea!")
            rclpy.shutdown()

        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    try:
        # Solicitar al usuario que ingrese la velocidad angular desde la terminal
        vel_angular = float(input("Ingrese la velocidad angular para el giro (en rad/s): "))
    except ValueError:
        print("Error: Ingrese un número válido para la velocidad angular.")
        return

    nodo_cuadrado = NodoCuadrado(vel_angular)  # Inicializar el nodo del cuadrado
    try:
        rclpy.spin(nodo_cuadrado)  # Ejecutar el nodo
    except KeyboardInterrupt:
        print("Nodo terminado por el usuario!")
    finally:
        nodo_cuadrado.destroy_node()  # Destruir el nodo
        rclpy.shutdown()  # Cerrar ROS

if __name__ == "__main__":
    main()

