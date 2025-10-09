import os
import time
import base64
import requests
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils import captura
from utils.captura import Capturas  # <-- Capturas importada
from datetime import datetime
load_dotenv()

apuntamiento = os.environ.get("BASE_URL", "sin_apuntamiento")

def error_persistencia(driver, wait, reporte=None, contexto="", duracion=None):
    fecha = datetime.now().strftime("%d-%m-%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    ruta_error = None
    error_detectado = False
    try:
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='DvActividad']/table/tbody/tr[3]/td/b/font"))
        )
        print(f"Error de persistencia detectado en: {contexto}")
        if contexto == "simulador_regla":
            Capturas.limpiar_subcarpeta("simulador_regla")
            ruta_error = captura.Capturas.tomar_pantallazo(driver, "Error_inicio_sesion", "simulador_regla", "Error")
        elif contexto == "Aprovisionamiento Ingresar":
            Capturas.limpiar_subcarpeta("aprovisionamiento_ingresar")
            ruta_error = captura.Capturas.tomar_pantallazo(driver, "Error_inicio_sesion", "aprovisionamiento_ingresar", "Error")
        elif contexto == "Crear Cuadrantes Nodos":
            Capturas.limpiar_subcarpeta("cuadrantes_nodos")
            ruta_error = captura.Capturas.tomar_pantallazo(driver, "Error_inicio_sesion", "cuadrantes_nodos", "Error")
        else:
            print(f"[ADVERTENCIA] Contexto no reconocido: '{contexto}'. No se tomará pantallazo.")
        
        time.sleep(5)
        print(f"[DEBUG] Ruta del pantallazo: {ruta_error}")
        base64_img = convertir_imagen_a_base64(ruta_error)
        mensaje=f"PRUEBAS\nFecha y hora: {fecha} / {hora}\nNodo: {apuntamiento}\nError: **Ingreso**\nDescripción Error: Error en el ingreso en el nodo {apuntamiento}"
        
        if duracion:
          mensaje += f" (Duracion: {duracion:.2f}s)"
        
        enviar_a_queue("queue_telegram", mensaje, base64_img)
       
    except TimeoutException:
        pass  # No se encontró el error, continuar normalmente


def convertir_imagen_a_base64(ruta_imagen, tipo_mime="image/png"):
        with open(ruta_imagen, "rb") as imagen_file:
            imagen_bytes = imagen_file.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        data_uri = f"data:{tipo_mime};base64,{imagen_base64}"
        return data_uri

def enviar_a_queue(nombre_cola, mensaje, imagen_base64):
    url = 'http://100.123.246.169:443/InventoriesOFSC/RS/cache/queue'
    token = 'Bearer QXBpLmNhY2hlQXBp'

    payload = {
        "name_queue": nombre_cola,
        "message": mensaje,
        "image_path": imagen_base64
    }
    headers = {
        'token': token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        #print(f"[DEBUG] Código de respuesta: {response.status_code}")
        #print(f"[DEBUG] Respuesta: {response.text}")
    except Exception as e:
        print(f"[ERROR] Falló el envío a Telegram: {e}")

    #response = requests.put(url, json=payload, headers=headers)
    #if response.status_code == 200:
    #    print("Proceso Exitoso")
    #else:
    #    print(f"Error al enviar a la cola. Código: {response.status_code} - Respuesta: {response.text}")


#def enviar_a_queue(nombre_cola, mensaje, imagen_base64):
#        url = 'http://100.123.246.169:443/InventoriesOFSC/RS/cache/queue'
#        token = 'Bearer QXBpLmNhY2hlQXBp'
#        
#    
#        payload = {
#            "name_queue": nombre_cola,
#            "message": mensaje,
#            "image_path": imagen_base64
#        }
#    
#        headers = {
#            'token': token,
#            'Content-Type': 'application/json'
#        }
#    
#        response = requests.put(url, json=payload, headers=headers)
#        print("Proceso Exitoso")