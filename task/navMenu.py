# nav_Menu.py
import os
import sys
from dotenv import load_dotenv
# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.espera import esperar_elemento
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager
from utils.errores_telegram.envio_error_telegram import enviar_a_queue, convertir_imagen_a_base64
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

load_dotenv()

apuntamiento = os.environ.get("BASE_URL", "sin_apuntamiento")

class NavMenu:
    
    def __init__(self, reporte, driver):
        self.reporte = reporte
        self.driver = driver        

    def menu_aprovisionamiento_consulta_cuenta(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        try:
            time.sleep(5)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/a")
                )
            ).click()
            time.sleep(3)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[11]/a/span[3]")
                )
            ).click()

            time.sleep(3)
            elemento_15 = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[11]/ul/li[8]/a"))
            )
            ruta.append(Capturas.tomar_pantallazo(self.driver, "navegar","aprovisionamiento_ingresar", "Navegacion"))
            #self.reporte.agregar_evidencia("Navegar", ruta4)
            elemento_15.click()
            
            time.sleep(3)
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] No se pudo encontrar o hacer clic en uno de los elementos del menú: {str(e)}")
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Aprovisionamiento Ingresar")
            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "aprovisionamiento_ingresar", "Error")

            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error)
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Navegación\nDescripción Error: Error navegando en menú Aprovisionamiento Ingresar en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img)

        return ruta   

    def menu_simulador_regla(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        try:
            ruta.append(Capturas.tomar_pantallazo(self.driver, "login_exitoso","Login"))
            # Navegar por el menú
            time.sleep(5)

            WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/a/img")
            )
            ).click()
            time.sleep(3)
            WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li/a")
            )
            ).click()
            time.sleep(3)
            elemento = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li/ul/li[15]/a/span[4]")
            ))
            ruta.append(Capturas.tomar_pantallazo(self.driver, "navegar", "Navegacion"))
            elemento.click()
            
            #Capturas.tomar_pantallazo(self.driver, "navegar", "simulador_regla", "Navegacion")    
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] No se pudo encontrar o hacer clic en uno de los elementos del menú: {str(e)}")
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Simulador Regla")
            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "simulador_regla", "Error")

            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Navegación\nDescripción Error: Error navegando en menú Simulador Regla en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img)

        return ruta   
    
    def menu_agendaWFM(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        try:
            # Navegar por el menú
            time.sleep(5)

            # Hacer clic en el primer enlace
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/a")
                )
            ).click()

            time.sleep(3)

            # Hacer clic en el segundo enlace
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[6]/a/span[3]")
                    #(By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[4]/a/span[3]")
                )
            ).click()

            time.sleep(3)

            # Hacer clic en el tercer enlace
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[6]/ul/li[3]/a/span[4]")
                    #(By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[4]/ul/li[3]/a/span[4]")

                )
            ).click()
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] No se pudo encontrar o hacer clic en uno de los elementos del menú: {str(e)}")
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "simulador_regla", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Navegación\nDescripción Error: Error navegando en menú Agendamiento en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img)
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Agenda WFM")

    def menu_actualizacion_datos_WFM(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        try:
            time.sleep(5)
            # Abrir menú lateral
            time.sleep(5)
            WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/a/img")
            )
            ).click()
            #time.sleep(3)
            time.sleep(2)

            # Hacer clic en "MGC: Modulo Gestion Calidad"
            modulo_xpath = "//a[@title='MGC::Modulo Gestion Calidad']"
            modulo = esperar_elemento(self.driver, By.XPATH, modulo_xpath, timeout=10, clickable=True)
            self.driver.execute_script("arguments[0].scrollIntoView();", modulo)
            modulo.click()

            # Hacer clic en "Gestión de Personal"
            gestion_personal_xpath = "//a[@title='Gestion de Personal']"
            gestion_personal = esperar_elemento(self.driver, By.XPATH, gestion_personal_xpath, timeout=10, clickable=True)
            self.driver.execute_script("arguments[0].scrollIntoView();", gestion_personal)
            gestion_personal.click()

            # Buscar y hacer clic en "Actualizar Datos WFM"
            opcion_actualizar_xpath = "//span[contains(text(),'MGC::Modulo Gestion Calidad::Actualizacion de dato')]"
            opcion_actualizar = esperar_elemento(self.driver, By.XPATH, opcion_actualizar_xpath, timeout=10, clickable=True)
            opcion_actualizar.click()

            time.sleep(4)
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] No se pudo encontrar o hacer clic en uno de los elementos del menú: {str(e)}")
            #error_persistencia(self.driver, WebDriverWait(self.driver, 5), contexto="Actualizacion Datos WFM")
            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "Actualizacion_Datos_WFMr", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Navegación\nDescripción Error: Error navegando en menú Actualizacion Datos WFM en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img)

    def menu_cuadrantes_nodo(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        ruta=[]
        ruta.append(Capturas.tomar_pantallazo(self.driver, "login_exitoso", "cuadrantes_nodos", "Login"))
        wait = WebDriverWait(self.driver, 10)
        try:
            # Paso 1
            element = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/a/img")
            ))
            self.driver.execute_script("arguments[0].click();", element)
            
            # Paso 2
            element = WebDriverWait(self.driver, 12).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[52]/a/span[3]")
            ))
            self.driver.execute_script("arguments[0].click();", element)

            # Paso 3
            element = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[52]/ul/li[13]/a/span[4]")
            ))
            self.driver.execute_script("arguments[0].click();", element)

            # Paso 4
            element = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[52]/ul/li[13]/ul/li[20]/a/span[5]")
            ))
            self.driver.execute_script("arguments[0].click();", element)

            # Paso 5
            element = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='contenedor_menu_barra_lateral']/div/ul/li[52]/ul/li[13]/ul/li[20]/ul/li/a/span[6]")
            ))
            self.driver.execute_script("arguments[0].click();", element)
            
            ruta.append(Capturas.tomar_pantallazo(self.driver, "navegar", "cuadrantes_nodos", "Navegacion"))
        
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print(f"[ERROR] No se pudo encontrar o hacer clic en uno de los elementos del menú: {str(e)}")

            # Tomar pantallazo del error
            ruta_error = Capturas.tomar_pantallazo(self.driver, "error_menu", "cuadrantes_nodos", "Error")
            # Convertir a base64
            base64_img = convertir_imagen_a_base64(ruta_error if ruta_error else [])
            mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError:Navegación\nDescripción Error: Error navegando en menú Cuadrantes Nodos en el nodo {apuntamiento}"
            enviar_a_queue("queue_telegram", mensaje, base64_img)
        return ruta
