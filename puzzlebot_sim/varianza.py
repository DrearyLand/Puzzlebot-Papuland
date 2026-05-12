#!/usr/bin/env python3
import numpy as np

# Instrucciones: Captura aquí tus mediciones del mundo real.
# datos_x: Distancia total avanzada (Meta: 1.0m)
# datos_y: Desviación lateral (Meta: 0.0m)
# datos_theta_deg: Ángulo final medido con transportador en GRADOS.

datos_x = [1.02, 0.98, 1.01, 0.99, 1.00] # Ejemplo
datos_y = [0.02, -0.01, 0.01, 0.00, -0.02] # Ejemplo
datos_theta_deg = [1.5, -1.0, 0.5, 0.0, -0.5] # Ejemplo

# Procesamiento estadístico
datos_theta_rad = np.deg2rad(datos_theta_deg)

var_x = np.var(datos_x, ddof=1)
var_y = np.var(datos_y, ddof=1)
var_theta = np.var(datos_theta_rad, ddof=1)

print("-" * 40)
print("RESULTADOS PARA TU CÓDIGO DE ROS 2")
print("-" * 40)
print(f"Varianza lineal (Promedio X e Y) -> self.A = {(var_x + var_y)/2:.8f}")
print(f"Varianza angular (Theta)        -> self.C = {var_theta:.8f}")
print("-" * 40)