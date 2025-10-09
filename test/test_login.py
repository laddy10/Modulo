import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.errores_telegram.envio_error_telegram import convertir_imagen_a_base64, enviar_a_queue
from selenium.common.exceptions import TimeoutException
from datetime import datetime
#variables
GENERAR_REPORTE = os.getenv("GENERAR_REPORTE", "True").lower() == "true"
#task
from abilities.navegar import iniciar_navegador
from utils.descifrar_contrasena import obtener_contrasena
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager
from urllib.parse import urlparse
from utils.errores_telegram.envio_error_telegram import error_persistencia

load_dotenv()# test_login.py
#load_dotenv("/env/modulo_de_gestion/.envLogin")# test_login.py

# Cargar variables de entorno
BASE_URL = os.getenv('BASE_URL')
USUARIO = os.getenv('USUARIO')
CONTRASENA = obtener_contrasena()
def obtener_apuntamiento():
    try:
        base_url = os.getenv("BASE_URL", "")
        parsed_url = urlparse(base_url)
        return parsed_url.hostname or "sin_apuntamiento"
    except Exception:
        return "sin_apuntamiento"
#apuntamiento = os.environ.get("BASE_URL", "sin_apuntamiento")

def esperar_elemento(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

class TestLogin:
    def __init__(self, driver, reporte):
        self.driver = driver
        self.reporte = reporte
        self.inicio_test = time.time()
    
    def teardown_method(self, method):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
    # Calcular duración del test al inicio del teardown
        duracion_total = time.time() - self.inicio_test

      # Ejecutar error_persistencia
       
        try:
            wait = WebDriverWait(self.driver, 10)
            error_persistencia(self.driver, wait, self.reporte, contexto="crear simulador regla")
        except Exception as e:
            print(f"[ERROR] en error_persistencia: {e}")
        
        
        # Control de timeout
        if duracion_total > 60:
            print(f"[ALERTA] Test demoró {duracion_total:.2f} segundos. Enviando alerta...")
            try:
                ruta_timeout = Capturas.tomar_pantallazo(self.driver, "timeout_test", "", "Timeout")
                imagen_base64 = convertir_imagen_a_base64(ruta_timeout)
                mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {BASE_URL}\nError: *Timeout Aprovisionamiento Ingresar*\nDescripción Error: Test superó tiempo esperado en {BASE_URL} (Duración: {duracion_total:.2f}s"
                enviar_a_queue("queue_telegram", mensaje, imagen_base64)
            except Exception as e:
                print(f"[ERROR] Al enviar alerta de timeout: {e}")

        # Cierre del driver
        if self.driver:
            self.driver.quit()
        
    @classmethod
    def teardown_class(cls):
        # Guarda todos los reportes que el manager tenga en memoria
        ReporteManager.guardar_todos()

    def ingresar_datos_login(self, usuario, contrasena):
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[2]/td[2]/input").send_keys(usuario)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[3]/td[2]/input").send_keys(contrasena)
        time.sleep(2.5)
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, "loadSubmitForm")))
        esperar_elemento(self.driver, By.ID, "Submit").click()
        # Verificación de error de persistencia
        wait = WebDriverWait(self.driver, 10)
        

    def test_caso1Ingresoalainterfaz(self):
        self.driver.get(BASE_URL)
        time.sleep(5)
        ruta1 = Capturas.tomar_pantallazo_especial(self.driver, "caso1_ingreso_interfaz", "login", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 1 Ingreso Interfaz", ruta1)
        time.sleep(5)

    def test_caso2ingreso_correcto(self):
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[2]/td[2]/input").send_keys(USUARIO)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[3]/td[2]/input").send_keys(CONTRASENA)
        esperar_elemento(self.driver, By.ID, "Submit").click()
        time.sleep(2)
        # Verificar si el elemento de navegación está presente
        wait = WebDriverWait(self.driver, 10)
        try:
            elemento = wait.until(EC.presence_of_element_located((By.XPATH, "//li[@id='userNavInfo']/label1")))
            print("El elemento está presente.")
            ruta2 = Capturas.tomar_pantallazo_especial(self.driver, "caso2_ingreso_correcto", "login", "screenshot")
            # Agregar evidencia al reporte si existe
            if self.reporte:
                self.reporte.agregar_evidencia("Caso 2 Ingreso Correcto", ruta2)

        except TimeoutException:
            print("El elemento NO está presente. Tomando pantallazo...")
            # Tomar pantallazo principal del caso
            ruta2 = Capturas.tomar_pantallazo_especial(self.driver, "caso2_ingreso_incorrecto", "login", "screenshot")

            # Agregar evidencia al reporte si existe
            if self.reporte:
                self.reporte.agregar_evidencia("Caso 2 Ingreso Incorrecto", ruta2)

            # Convertir imagen a base64 y enviar por cola a Telegram
            base64_img = convertir_imagen_a_base64(ruta2)
            apuntamiento = obtener_apuntamiento()
            mensaje=f"Pruebas\nFecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nDescripción Error: Login - Caso 2 Falló en el nodo {apuntamiento} - Ingreso Incorrecto"
            enviar_a_queue("queue_telegram",mensaje ,base64_img )

        time.sleep(5)

    def test_caso3borrar_campos(self):
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[2]/td[2]/input").send_keys(USUARIO)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[3]/td[2]/input").send_keys(CONTRASENA)
        time.sleep(2)
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, "loadSubmitForm")))
        ruta3 = Capturas.tomar_pantallazo_especial(self.driver, "caso3_borrar_campos", "login", "screenshot")
        esperar_elemento(self.driver, By.ID, "Borrar").click()
        time.sleep(2)
        ruta4 = Capturas.tomar_pantallazo_especial(self.driver, "caso3_borrar_campos", "login", "screenshot")
        
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 3 Ingresar Credenciales", ruta3)
            self.reporte.agregar_evidencia("Caso 3 Borrar Campos", ruta4)

        time.sleep(5)

    def test_caso4USUA_incorrecto(self):
        self.ingresar_datos_login("45110350", CONTRASENA)
        time.sleep(2)
        ruta5 = Capturas.tomar_pantallazo_especial(self.driver, "caso4_usuario_incorrecto", "login", "screenshot")
        #verificar_error_persistencia(self.driver, wait, self.reporte, contexto="caso4_usuario_incorrecto")
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 4 Usuario Incorrecto", ruta5)
        time.sleep(5)

    def test_caso5CONTRA_incorrecta(self):
        self.ingresar_datos_login(USUARIO, "123456789")
        time.sleep(2)
        ruta6 = Capturas.tomar_pantallazo_especial(self.driver, "caso5_contraseña_incorrecta", "login", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 5 Ingresar Contraseña Incorrecta", ruta6)
        time.sleep(5)

    def test_caso6USUA_vacio(self):
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[3]/td[2]/input").send_keys(CONTRASENA)
        esperar_elemento(self.driver, By.ID, "Submit").click()
        time.sleep(2)
        ruta7 = Capturas.tomar_pantallazo_especial(self.driver, "caso6_usuario_vacio", "login", "screenshot")
        
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 6 Usuario Vacio", ruta7)
        
        time.sleep(5)

    def test_caso7CONTRA_vacia(self):
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.XPATH, "//div[@id='formularioIngreso']/center/table/tbody/tr[2]/td[2]/input").send_keys(USUARIO)
        esperar_elemento(self.driver, By.ID, "Submit").click()
        esperar_elemento(self.driver, By.ID, "Submit").click()
        time.sleep(3)
        ruta8 = Capturas.tomar_pantallazo_especial(self.driver, "caso7_contraseña_vacia", "login", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 7 Contraseña Vacia", ruta8)
        time.sleep(5)

    def test_caso8campos_vacios(self):
        self.driver.get(BASE_URL)
        esperar_elemento(self.driver, By.ID, "Submit").click()
        time.sleep(2)
        ruta9 = Capturas.tomar_pantallazo_especial(self.driver, "caso8_campos_vacios", "login", "screenshot")
        
        if self.reporte:
            self.reporte.agregar_evidencia("Caso 8 Campos Vacios", ruta9)
        time.sleep(5)

def ejecutar_pruebas(hilo_id, pruebas_ejecutadas, pruebas_exitosas, pruebas_fallidas, hilos_ejecutados, errores_por_hilo):
    Capturas.limpiar_subcarpeta("Login")
    time.sleep(5)

    driver = iniciar_navegador()
    if not driver:
        print(f"Error al iniciar el navegador en hilo {hilo_id}")
        errores_por_hilo[hilo_id] = (-1, "No se pudo iniciar el navegador")
        pruebas_fallidas[0] += 1
        hilos_ejecutados[0] += 1
        return  # termina aquí para evitar usar driver que es None
    
    if GENERAR_REPORTE:
        reporte = ReporteManager.obtener("Login")  # <-- OBTENER AQUÍ
    else:
      reporte = None

    test = TestLogin(driver, reporte)
    pruebas_exitosas_hilo = 0

    try:
        casos = [
            test.test_caso1Ingresoalainterfaz,
            test.test_caso2ingreso_correcto,
            test.test_caso3borrar_campos,
            test.test_caso4USUA_incorrecto,
            test.test_caso5CONTRA_incorrecta,
            test.test_caso6USUA_vacio,
            test.test_caso7CONTRA_vacia,
            test.test_caso8campos_vacios
        ]

        for i, caso in enumerate(casos):
            pruebas_ejecutadas[0] += 1
            try:
                caso()
                pruebas_exitosas_hilo += 1
            except Exception as e:
                pruebas_fallidas[0] += 1
                errores_por_hilo[hilo_id] = (i, str(e))
                print(f"Test caso {i+1} falló en hilo {hilo_id}: {e}")

                #contexto = f"Fallo en caso {i+1} - {caso.__name__}"
                #error_persistencia_especial(driver, WebDriverWait(driver, 10), reporte, contexto=contexto)
#
                pruebas_exitosas_hilo = 0
                break

        if pruebas_exitosas_hilo == len(casos):
            pruebas_exitosas[0] += 1

    finally:
        wait = WebDriverWait(driver, 10)  # Espera máxima de 10 segundos
        if GENERAR_REPORTE:
            ReporteManager.guardar_todos()  # <-- GUARDAR AL FINAL
        driver.quit()
        hilos_ejecutados[0] += 1
         
