#!/usr/bin/env python3
import numpy as np

# Aquí meterán las mediciones de sus 10-20 pruebas físicas
# Ejemplo: si avanzó 1m, y midieron 0.97, 0.99, 1.02...
datos_x = [0.97, 0.99, 1.02, 0.98, 1.01] 

# Se calcula con grados de libertad (ddof=1) para una muestra, como indicó el profesor
varianza_x = np.var(datos_x, ddof=1)

print("--- Resultados del Experimento Físico ---")
print(f"Varianza obtenida: {varianza_x}")
print("-> Usa este valor para afinar kr o kl en localisation_node.py")