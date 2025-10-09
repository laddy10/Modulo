import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
GENERAR_REPORTE = os.getenv("GENERAR_REPORTE", "True").lower() == "true"
from utils.descifrar_contrasena import obtener_contrasena
from utils.espera import esperar_elemento
from task.navMenu import NavMenu
from task.consulta import Consulta
from task.actualizacion import ActualizacionDatos
from abilities.navegar import iniciar_navegador
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager
from utils.errores_telegram.envio_error_telegram import convertir_imagen_a_base64,enviar_a_queue
from datetime import datetime
#reporte = ReporteDocumento("actualizar_datos_WFM")
#reporte = ReporteManager.obtener("actualizar_datos_WFM")

# Cargar variables de entorno
load_dotenv()
BASE_URL = os.getenv('BASE_URL')
USUARIO = os.getenv('USUARIO')
CONTRASENA = obtener_contrasena()
ID = os.getenv('ID')
def obtener_apuntamiento():
    try:
        base_url = os.getenv("BASE_URL", "")
        parsed_url = urlparse(base_url)
        return parsed_url.hostname or "sin_apuntamiento"
    except Exception:
        return "sin_apuntamiento"

if GENERAR_REPORTE:
    reporte = ReporteManager.obtener("actualizar_datos_WFM")
else:
    reporte = None


def obtener_driver():
    """Devuelve una nueva instancia del navegador"""
    return iniciar_navegador()

def validacion_campos(driver):
    fecha = datetime.now().strftime("%d-%m-%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    """Valida que el campo 'aliado' esté presente y no vacío"""
    try:
        campo_aliado = driver.find_element(By.ID, "aliado")
        valor_aliado = campo_aliado.get_attribute("value")
        if valor_aliado.strip():
            print(f"Aliado válido: {valor_aliado}")
        else:
            print("Error: El campo 'aliado' está vacío o no cargó correctamente.")
    except Exception as e:
        print(f"Error al validar campo 'aliado': {e}")
        # Tomar pantallazo con el número de tes
        ruta = Capturas.tomar_pantallazo_especial(driver,f"Error al validar campo 'aliado' ","actualizar_datos_WFM","Error")
        # Convertir imagen a base64 y enviar por cola a Telegram
        base64_img = convertir_imagen_a_base64(ruta)
        apuntamiento = obtener_apuntamiento()
        mensaje=f"Fecha y hora: {fecha} / {hora}\nNodo: {BASE_URL}\nDescripción Error: Error al validar campo 'aliado' - actualizar_datos_WFM en el nodo {apuntamiento} "    
        enviar_a_queue("queue_telegram", mensaje, base64_img)

def ejecutar_flujo_completo():
    """Ejecuta el flujo completo de login, navegación, consulta y actualización"""
    driver = obtener_driver()
 
    try:
        # Importar Login aquí para evitar importación circular
        from task.login import Login

        # Login
        login = Login(reporte, driver, USUARIO, CONTRASENA)
        login.ingresar_actualizacion_datos_WFM()
        

        # Navegación
        nav = NavMenu(reporte, driver)
        nav.menu_actualizacion_datos_WFM()

        # Consulta
        consulta = Consulta(reporte, driver)
        consulta.consulta_actualizacion_datos_WFM(ID)
      
        # Validación de campo
        validacion_campos(reporte, driver)

        # Actualización
        actualizacion = ActualizacionDatos(reporte, driver)
        actualizacion.actualizar_datos()

    finally:
        # Cierre del navegador
        print("🔒 Cerrando navegador...")
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    ejecutar_flujo_completo()
    
    
