import os
import time
from dotenv import load_dotenv
from utils.captura import Capturas  # <-- Capturas importada
from selenium.webdriver.common.by import By

# Cargar variables de entorno si no se han cargado antes
load_dotenv()
# Obtener variables de entorno
CUADRANTE = os.getenv("CUADRANTE")
NODO = os.getenv("NODO")
ESTADO = os.getenv("ESTADO")

if not CUADRANTE:
    raise ValueError("La variable de entorno 'CUADRANTE' no está definida correctamente.")
if not NODO:
    raise ValueError("La variable de entorno 'NODO' no está definida correctamente.")
if not ESTADO:
    raise ValueError("La variable de entorno 'ESTADO' no está definida correctamente.")

class creacion:
    def __init__(self, reporte, driver):
        self.reporte = reporte
        self.driver = driver    

    def crear_cuadrante_nodo(self):  # ← Sin driver aquí
        ruta=[]
        dropdown = self.driver.find_element(By.ID, "id_zona")
        dropdown.find_element(By.XPATH, f"//option[. = '{os.getenv('CUADRANTE')}']").click()
        self.driver.find_element(By.ID, "key").click()
        self.driver.find_element(By.ID, "key").send_keys(os.getenv('NODO'))
        self.driver.find_element(By.ID, "estado").click()
        dropdown = self.driver.find_element(By.ID, "estado")
        dropdown.find_element(By.XPATH, f"//option[. = '{os.getenv('ESTADO')}']").click()
        
        ruta.append(Capturas.tomar_pantallazo(self.driver, "llenado_campos", "cuadrantes_nodos", "Crear"))

        self.driver.find_element(By.ID, "Actualizar").click()

        time.sleep(5)

        return ruta
                    