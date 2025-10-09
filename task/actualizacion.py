import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.espera import esperar_elemento
from utils.captura import Capturas  # <-- Capturas importada
from utils.errores_telegram.envio_error_telegram import error_persistencia, convertir_imagen_a_base64,enviar_a_queue
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()


def obtener_apuntamiento():
    try:
        base_url = os.getenv("BASE_URL", "")
        parsed_url = urlparse(base_url)
        return parsed_url.hostname or "sin_apuntamiento"
    except Exception:
        return "sin_apuntamiento"
    
class ActualizacionDatos:
    def __init__(self, driver, archivo_datos="datos.txt"):
        self.driver = driver
        self.archivo_datos = archivo_datos

    def cargar_datos(self):
        """Carga datos desde el archivo TXT y los devuelve como diccionario."""
        datos = {}
        try:
            with open(self.archivo_datos, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=", 1)
                        datos[key] = value
                    else:
                        print(f"⚠️ Línea ignorada (formato incorrecto): {line}")
        except FileNotFoundError:
            print(f"❌ El archivo {self.archivo_datos} no se encontró.")
        return datos

    def actualizar_datos(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        """Actualiza los datos del formulario en la web con la información cargada."""
        datos = self.cargar_datos()

        celular1 = datos.get("TEL", "No disponible")
        celular2 = datos.get("TEL2", "No disponible")
        correo = datos.get("CORREO", "No disponible")

        print(f"TEL: {celular1}, TEL2: {celular2}, CORREO: {correo}")

        try:
            # Campos del formulario
            campo_cel1 = esperar_elemento(self.driver, By.ID, "celular1", timeout=10)
            campo_cel1.clear()
            campo_cel1.send_keys(celular1)

            campo_cel2 = esperar_elemento(self.driver, By.ID, "celular2", timeout=10)
            campo_cel2.clear()
            campo_cel2.send_keys(celular2)

            campo_correo = esperar_elemento(self.driver, By.ID, "correo2", timeout=10)
            campo_correo.clear()
            campo_correo.send_keys(correo)

            # Botón Guardar
            guardar_btn = esperar_elemento(self.driver, By.ID, "Guardar", timeout=10, clickable=True)
            ActionChains(self.driver).move_to_element(guardar_btn).perform()
            guardar_btn.click()
            ruta4 = Capturas.tomar_pantallazo(self.driver, "Actualizacion", "actualizar_datos_WFM", "Actualizar")
            self.reporte.agregar_evidencia("Actualización Realizada", ruta4)
            print("Datos actualizados correctamente.")

        except Exception as e:
            print(f"Error al actualizar datos: {e}")

            # Tomar pantallazo de error
            ruta_error = Capturas.tomar_pantallazo_especial(self.driver, "fallo_actualizacion", "actualizar_datos_WFM", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error)
            apuntamiento = obtener_apuntamiento()
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Actualización\nDescripción Error: Falló Actualización de Datos nodo {apuntamiento}\nTest: actualizar_datos_WFM"
            enviar_a_queue("queue_telegram",mensaje, base64_img)


        time.sleep(20)  # Pausa final (ajustable según necesidad)
