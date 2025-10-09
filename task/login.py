import os
import time
import inspect
import re
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from utils.espera import esperar_elemento
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager
from utils.errores_telegram.envio_error_telegram import error_persistencia, convertir_imagen_a_base64,enviar_a_queue
from urllib.parse import urlparse

load_dotenv()


def obtener_apuntamiento():
    try:
        base_url = os.getenv("BASE_URL", "")
        parsed_url = urlparse(base_url)
        return parsed_url.hostname or "sin_apuntamiento"
    except Exception:
        return "sin_apuntamiento"
    
class Login:
    def __init__(self, reporte, driver, usuario, contrasena):
        self.reporte = reporte
        self.driver = driver
        self.usuario = usuario
        self.contrasena = contrasena

    def ingresar(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        try:
            # Ingresar usuario y contraseña
            self.driver.find_element(By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[2]/td[2]/input").send_keys(self.usuario)
            self.driver.find_element(By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[3]/td[2]/input").send_keys(self.contrasena)
            time.sleep(4)
            #ruta.append(Capturas.tomar_pantallazo(self.driver,"aprovisionamiento_ingresar", "Login"))
            ruta.append(Capturas.tomar_pantallazo(self.driver, "simulador_regla", "Login"))
            #self.reporte.agregar_evidencia("Ingresar Credenciales", ruta2)
            #self.reporte.guardar()
            time.sleep(2)

            # Obtener el select de tipoRed
            tipoRed = self.driver.execute_script(
                "return document.evaluate(\"//div[@id='divTipoRed']/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            )

            return ruta, tipoRed  # Devuelve el WebElement directamente

        except Exception as e:
            print(f"Error al intentar ingresar: {e}")
            apuntamiento = obtener_apuntamiento()
            ruta_login = Capturas.tomar_pantallazo(self.driver, "fallo_ingreso", "Errores", "Errores")
            imagen_base64 = convertir_imagen_a_base64(ruta_login)
            mensaje=f"PRUEBAS\nFecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError: **Ingreso**\nDescripción Error: Error en el ingreso en el nodo {apuntamiento}",
            enviar_a_queue("queue_telegram", mensaje, imagen_base64)
            

    def ingresar_actualizacion_datos_WFM(self, max_intentos=3, test=None):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        # Detectar número del test automáticamente si no fue pasado
        if test is None:
            caller_name = inspect.stack()[1].function
            match = re.search(r'test_(\d+)', caller_name)
            if match:
                test = match.group(1)
            else:
                test = "N/A"

        for intento in range(1, max_intentos + 1):
            try:
                print(f"Intento {intento} de inicio de sesión... (Test {test})")

                # Esperar que el formulario de login esté visible
                esperar_elemento(self.driver, By.ID, "formularioIngreso")

                # Buscar el campo de usuario
                usuario_input = esperar_elemento(self.driver, By.XPATH, "//input[@type='text']")
                usuario_input.clear()
                usuario_input.send_keys(self.usuario)

                # Buscar el campo de contraseña
                contrasena_input = esperar_elemento(self.driver, By.XPATH, "//input[@type='password']")
                contrasena_input.clear()
                contrasena_input.send_keys(self.contrasena)
                time.sleep(2)
                
                # Botón ingresar
                boton_ingresar = esperar_elemento(
                    self.driver, By.XPATH, "//input[@type='submit' and @value='Ingresar']", clickable=True
                )
                boton_ingresar.click()
                time.sleep(2)
                time.sleep(3)
                
                # Confirmar login exitoso
                if esperar_elemento(self.driver, By.ID, "imgAtrasMenu", timeout=5):
                    print(f"✅ Inicio de sesión exitoso (Test {test})")
                    return True

            except Exception as e:
                print(f"❌ Error en el intento {intento} del Test {test}: {e}")
                if intento == max_intentos:
                    print(f"⛔ No se pudo iniciar sesión después de varios intentos. Test {test}")
                    
                    # Tomar pantallazo con el número de test
                    ruta = Capturas.tomar_pantallazo_especial(
                        self.driver,
                        f"fallo_ingreso_WFM_test{test}",
                        "actualizar_datos_WFM",
                        "Error"
                    )

                    # Convertir imagen a base64 y enviar por cola a Telegram
                    base64_img = convertir_imagen_a_base64(ruta)
                    apuntamiento = obtener_apuntamiento()
                    mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError: **Ingreso**\nDescripción Error: Error ingreso en el nodo {apuntamiento}  - actualizar_datos_WFM Test {test}",
                    enviar_a_queue("queue_telegram", mensaje, base64_img)
                    return False    