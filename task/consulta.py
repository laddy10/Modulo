import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.espera import esperar_elemento
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager
from dotenv import load_dotenv
from datetime import datetime
from utils.errores_telegram.envio_error_telegram import enviar_a_queue, convertir_imagen_a_base64
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

load_dotenv()

apuntamiento = os.environ.get("BASE_URL", "sin_apuntamiento")

class Consulta: 
    def __init__(self, reporte, driver):
        self.reporte = reporte
        self.driver = driver
        self.vars = {}

    def consulta_aprovisionamiento_ingresar(self, cuenta):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        try:
            # Esperar a que el campo "cuenta" esté presente
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "cuenta"))
            )
            # Limpiar y escribir el valor de la cuenta
            self.driver.find_element(By.ID, "cuenta").clear()
            self.driver.find_element(By.ID, "cuenta").send_keys(cuenta)
            ruta.append(Capturas.tomar_pantallazo(self.driver, "consulta","aprovisionamiento_ingresar", "Consulta"))
            # Hacer clic en el botón de consultar
            self.driver.find_element(By.ID, "consultar").click()
            time.sleep(3)
            ruta.append(Capturas.tomar_pantallazo(self.driver, "consulta_realizada","aprovisionamiento_ingresar", "Consulta"))
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] Error en Aprovidionamiento Ingresar: {str(e)}")
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Aprovisionamiento Ingresar")
            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "aprovisionamiento_ingresar", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error)
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Consulta\nDescripción: Error en la consulta de Aprovisionamiento Ingresar en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img )
        
        return ruta  
        
    def consulta_simulador_regla(self, orden):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        try:
            # Consulta OT
            self.driver.find_element(By.ID, "tabs-1").click()
            self.driver.find_element(By.ID, "origen").click()
            dropdown = self.driver.find_element(By.ID, "origen")
            dropdown.find_element(By.XPATH, "//option[. = 'Orden de trabajo']").click()
            
            self.driver.switch_to.frame(0)
            self.driver.find_element(By.CSS_SELECTOR, "body").click()
            self.driver.switch_to.default_content()
            
            self.driver.find_element(By.ID, "identificador").click()
            self.driver.find_element(By.ID, "identificador").send_keys(orden)
            ruta.append(Capturas.tomar_pantallazo(self.driver, "consulta","simulador_regla", "Consulta"))
            self.driver.find_element(By.ID, "consultar").click()

            time.sleep(8)
            
            ruta.append(Capturas.tomar_pantallazo(self.driver, "consulta_realizada", "simulador_regla", "Consulta"))
            #self.reporte.agregar_evidencia("Consulta Realizada", ruta6)
            #self.reporte.guardar()
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] Error en simulador regla: {str(e)}")
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Aprovisionamiento Ingresar")
            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "simulador_regla", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"PRUEBA\nFecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Consulta\nDescripción Error: Error en la consulta de simulador regla en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje,base64_img)
        return ruta

    def consulta_agendaWFM(self, orden):
        # Buscar orden
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "TBorden"))
        )
        self.driver.find_element(By.ID, "TBorden").send_keys(orden)
        self.driver.find_element(By.ID, "Rbot-O").click()
        self.driver.find_element(By.ID, "button").click()     

    def consulta_actualizacion_datos_WFM(self, ID):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta = []
        try:
            # Ingresar ID
            ingreso_id_xpath = "//input[@id='identificacionbusqueda']"
            ingreso_id = esperar_elemento(self.driver, By.XPATH, ingreso_id_xpath, timeout=10, clickable=True)
            ingreso_id.send_keys(ID)
            time.sleep(2)
            #Capturas.tomar_pantallazo_especial(self.driver, "consulta","actualizacion_datos_WFM", "screenshot")
            # Hacer clic en el botón Consultar
            consultar_xpath = "//input[@id='Consultar']"
            consultarButton = esperar_elemento(self.driver, By.XPATH, consultar_xpath, timeout=10, clickable=True)
            consultarButton.click()
            #Capturas.tomar_pantallazo_especial(self.driver, "consulta_realizada","actualizacion_datos_WFM", "screenshot")
            time.sleep(10)
            ruta.append(Capturas.tomar_pantallazo(self.driver, "consulta_realizada", "actualizacion_datos_WFM", "screenshot"))
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] Error en consulta_actualizacion_datos_WFM: {str(e)}")

            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error", "actualizacion_datos_WFM", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Consulta\nDescripción: Error en consulta actualizacion datos WFM en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje,base64_img)

        return ruta      