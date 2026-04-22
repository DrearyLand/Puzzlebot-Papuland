#!/usr/bin/env python3
#import rclpy
#import time
#import math
#from rclpy.node import Node
#from geometry_msgs.msg import Twist

#class ControladorCoordenadas(Node):
#    def __init__(self):
#        super().__init__("Controlador_coordenadas")
#        self.registrador = self.get_logger()  # OBTENER EL REGISTRO PARA IMPRIMIR MENSAJES
#        self.registrador.info("¡Nodo de coordenadas iniciado! ...")
#        self.tiempo_inicio = time.time()  # TIEMPO DE INICIO DEL CONTROLADOR
#        self.editor = self.create_publisher(Twist, "/cmd_vel", 1)  # PUBLICADOR PARA ENVIAR COMANDOS DE VELOCIDAD
#        self.posicion_inicial = (5.54, 5.54)  # POSICIÓN INICIAL DE LA TORTUGA
#        self.angulo_actual = 0.0  # ÁNGULO ACTUAL DE LA TORTUGA

#    def obtener_coordenadas_usuario(self):
#        coordenadas_x = []
#        coordenadas_y = []
#
#        for i in range(1, 5):
#            x = float(input(f"Ingrese X{i}: "))  # SOLICITAR AL USUARIO LA COORDENADA X
#            y = float(input(f"Ingrese Y{i}: "))  # SOLICITAR AL USUARIO LA COORDENADA Y
#            coordenadas_x.append(x)  # AGREGAR LA COORDENADA X A LA LISTA
#            coordenadas_y.append(y)  # AGREGAR LA COORDENADA Y A LA LISTA
#
#        return coordenadas_x, coordenadas_y  # DEVOLVER LAS LISTAS DE COORDENADAS X Y Y

#    def rotar_tortuga(self, velocidad_angular, angulo_objetivo, mensaje):
#       mensaje.linear.x = 0.0  # ESTABLECER LA VELOCIDAD LINEAL EN 0
#        tiempo_transcurrido = 0.0  # TIEMPO TRANSCURRIDO DESDE EL INICIO DE LA ROTACIÓN
#        diferencia_angulo = angulo_objetivo - self.angulo_actual  # DIFERENCIA ENTRE EL ÁNGULO OBJETIVO Y EL ÁNGULO ACTUAL

#        if diferencia_angulo > math.pi:
#            diferencia_angulo -= math.pi * 2  # MANTENER LA DIFERENCIA EN EL RANGO [-PI, PI]
#        if diferencia_angulo < 0:
#            velocidad_angular_negativa = velocidad_angular * -1  # VELOCIDAD ANGULAR NEGATIVA PARA GIRAR EN SENTIDO CONTRARIO
#        else:
#            velocidad_angular_negativa = velocidad_angular  # MANTENER LA VELOCIDAD ANGULAR POSITIVA
#        tiempo_para_rotar = abs(diferencia_angulo) / velocidad_angular  # CALCULAR EL TIEMPO NECESARIO PARA ROTAR

#        while tiempo_transcurrido < tiempo_para_rotar:
#           tiempo_transcurrido = time.time() - self.tiempo_inicio  # ACTUALIZAR EL TIEMPO TRANSCURRIDO

#            if tiempo_transcurrido < tiempo_para_rotar:
#                mensaje.angular.z = velocidad_angular_negativa  # ESTABLECER LA VELOCIDAD ANGULAR EN EL MENSAJE
#                self.editor.publish(mensaje)  # PUBLICAR EL MENSAJE
#            else:
#                mensaje.angular.z = 0.0  # DETENER LA ROTACIÓN
#                self.editor.publish(mensaje)  # PUBLICAR 
#                self.tiempo_inicio = time.time()  # ACTUALIZAR EL TIEMPO DE INICIO
#                self.angulo_actual = angulo_objetivo  # ACTUALIZAR EL ÁNGULO ACTUAL

#   def avanzar_tortuga(self, velocidad_lineal, distancia, mensaje):
#        mensaje.angular.z = 0.0  # ESTABLECER LA VELOCIDAD ANGULAR EN 0
#        tiempo_transcurrido = 0.0  # TIEMPO TRANSCURRIDO DESDE EL INICIO DEL AVANCE

#        while tiempo_transcurrido < distancia:
#            tiempo_transcurrido = time.time() - self.tiempo_inicio  # ACTUALIZAR EL TIEMPO TRANSCURRIDO
#            if tiempo_transcurrido < distancia:
#                mensaje.linear.x = velocidad_lineal  # ESTABLECER LA VELOCIDAD LINEAL EN EL MENSAJE
#                self.editor.publish(mensaje)  # PUBLICAR EL MENSAJE
#           else:
#                mensaje.linear.x = 0.0  # DETENER 
#                self.editor.publish(mensaje)  # PUBLICAR 
#                self.tiempo_inicio = time.time()  # ACTUALIZAR EL TIEMPO DE INICIO

#    def ejecutar_trayectoria(self):
#        coordenadas_x, coordenadas_y = self.obtener_coordenadas_usuario()  # OBTENER LAS COORDENADAS DEL USUARIO
#        coordenadas = list(zip(coordenadas_x, coordenadas_y))  # COMBINAR LAS COORDENADAS X Y Y EN UNA LISTA DE TUPLAS
#        mensaje = Twist()  # CREAR UN MENSAJE DE TWIST PARA ENVIAR COMANDOS DE VELOCIDAD
#        velocidad_lineal = 1.0  # VELOCIDAD LINEAL DE AVANCE DE LA TORTUGA
#        velocidad_angular = 1.0  # VELOCIDAD ANGULAR DE ROTACIÓN DE LA TORTUGA

#        for coord in coordenadas:
#            diferencia_x = (coord[0] - self.posicion_inicial[0])  # CALCULAR LA DIFERENCIA EN LA COORDENADA X
#            diferencia_y = (coord[1] - self.posicion_inicial[1])  # CALCULAR LA DIFERENCIA EN LA COORDENADA Y
#            angulo_objetivo = math.atan2(diferencia_y, diferencia_x)  # CALCULAR EL ÁNGULO OBJETIVO
#            if angulo_objetivo < 0:
#                angulo_objetivo += 2 * math.pi
#            distancia_a_viajar = math.sqrt(math.pow(diferencia_x, 2) + math.pow(diferencia_y, 2))  # CALCULAR LA DISTANCIA A VIAJAR
#            self.rotar_tortuga(velocidad_angular, angulo_objetivo, mensaje)  # ROTAR LA TORTUGA HACIA EL ÁNGULO OBJETIVO
#            self.avanzar_tortuga(velocidad_lineal, distancia_a_viajar, mensaje)  # AVANZAR LA TORTUGA HACIA LA POSICIÓN OBJETIVO
#            self.posicion_inicial = (coord[0], coord[1])  # ACTUALIZAR LA POSICIÓN INICIAL DE LA TORTUGA
#        rclpy.shutdown()  # CERRAR EL CONEXION CON ROS

#def main(args=None):
#    rclpy.init(args=args)  # INICIALIZAR EL CONTEXTO DE ROS
#    controlador = ControladorCoordenadas()  # CREAR UNA INSTANCIA DEL CONTROLADOR DE TORTUGA
#    try: controlador.ejecutar_trayectoria()  # EJECUTAR LA TRAYECTORIA DE LA TORTUGA
#    except Exception as error:

#if __name__ == "__main__":
#    main()

