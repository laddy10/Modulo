# -*- coding: utf-8 -*-
import pytest
import os
import sys
os.environ["GENERAR_REPORTE"] = "False"
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import subprocess
import queue
import time
import logging
from collections import defaultdict
import xml.etree.ElementTree as ET
from datetime import timedelta
import traceback
import tempfile


# Configuración de entorno y logging
load_dotenv()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suprimir mensajes de TensorFlow
logging.basicConfig(level=logging.ERROR)  # Suprimir mensajes de logging
junit_lock = threading.Lock()


# Configuración de Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")  # Suprimir mensajes de DevTools
chrome_options.add_argument("--headless")  # Ejecutar en modo sin cabeza
chrome_options.add_argument("--no-sandbox")

# Crear un Lock para sincronizar las impresiones en la consola
console_lock = threading.Lock()

# Diccionario para registrar el estado de las órdenes
resultados = defaultdict(str)

# Archivo JUnit para resultados
#output_file = "resultados_junit.xml"
output_file = "reports/junit/resultados_junit_aprovisionamiento_ingresar.xml"

# Variables para contar tests
total_tests = 0
total_passed = 0
total_failed = 0

def inicializar_junit():
    
    # Crear la estructura base del archivo JUnit
    testsuites = ET.Element("testsuites")
    testsuite = ET.SubElement(testsuites, "testsuite", {
        "name": "MG_Aprovisionamiento",
        "tests": "0",
        "failures": "0",
        "passed": "0",  # Añadir el campo "passed" si no existe
        "time": "0"
    })
    # Escribir el archivo base, sobrescribiendo cualquier contenido previo
    tree = ET.ElementTree(testsuites)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

# Función para limpiar salida y evitar caracteres problemáticos
def limpiar_salida(salida):


    # Primero, eliminamos el stacktrace y las líneas que contienen información técnica no útil
    lineas = salida.splitlines()
    
    # Filtramos las líneas que contienen información del stacktrace y otros detalles irrelevantes
    lineas_filtradas = [
        line for line in lineas if not (
            "GetHandleVerifier" in line or 
            "No symbol" in line or 
            "BaseThreadInitThunk" in line or 
            "RtlUserThreadStart" in line
        )
    ]
    
    # Devolver la salida limpia
    return "\n".join(lineas_filtradas).strip()

# Función para formatear el tiempo en formato HH:MM:SS
def formatear_tiempo(segundos):
    return str(timedelta(seconds=segundos))

def actualizar_testsuite(testsuite, tiempo, fallo=False, paso=False):
    
    tests = int(testsuite.get("tests", "0")) + 1
    testsuite.set("tests", str(tests))
    
    tiempo_total = float(testsuite.get("time", "0")) + tiempo
    testsuite.set("time", f"{tiempo_total:.2f}")
    
    if fallo:
        fallos = int(testsuite.get("failures", "0")) + 1
        testsuite.set("failures", str(fallos))
    if paso:
        pasados = int(testsuite.get("passed", "0")) + 1
        testsuite.set("passed", str(pasados))

# Función que actualiza el archivo JUnit
def agregar_cuenta_junit(id_cuenta, detalle, resultado, tiempo):
    with junit_lock:
        # Verificación previa al parseo
        if not os.path.exists(output_file):
            print(f"ERROR: El archivo {output_file} no existe. Inicializando archivo base.")
            inicializar_junit()
        else:
            # Leer contenido para revisar si está vacío o corrupto
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                if not contenido:
                    print(f"ERROR: El archivo {output_file} está vacío. Reinicializando archivo base.")
                    inicializar_junit()
            except Exception as e:
                print(f"ERROR al leer {output_file}: {e}. Reinicializando archivo base.")
                inicializar_junit()

        # Intentar parsear el XML (ahora con el archivo ya seguro)
        try:
            tree = ET.parse(output_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"ERROR: ParseError al leer {output_file}: {e}. Reinicializando archivo base.")
            inicializar_junit()
            tree = ET.parse(output_file)
            root = tree.getroot()

        # Obtener o crear el testsuite
        testsuite = root.find("testsuite")
        if testsuite is None:
            testsuite = ET.SubElement(root, "testsuite", {
                "name": "MG_Aprovisionamiento",
                "tests": "0",
                "failures": "0",
                "passed": "0",
                "time": "0"
            })

        fallo = "Fallida" in detalle or "Error" in detalle
        paso = not fallo

        actualizar_testsuite(testsuite, tiempo, fallo=fallo, paso=paso)

        detalle_limpio = limpiar_salida(detalle)
        resultado_limpio = limpiar_salida(resultado)

        testcase = ET.SubElement(testsuite, "testcase", {
            "name": f"cuenta_{id_cuenta}",
            "time": formatear_tiempo(tiempo)
        })
        detail = ET.SubElement(testcase, "system-out")
        detail.text = f"Estado: {detalle_limpio}\nResultados: {resultado_limpio}"

        if fallo:
            failure = ET.SubElement(testcase, "failure", {
                "message": f"Error en la cuenta {id_cuenta}"
            })
            failure.text = detalle_limpio

        tree.write(output_file, encoding="utf-8", xml_declaration=True)



def leer_cuentas(archivo):
    if not os.path.exists(archivo):
        # Crear un archivo de ejemplo si no existe
        with open(archivo, 'w') as f:
            f.write("cuenta1\ncuenta2\ncuenta3")
        raise FileNotFoundError("El archivo {archivo} no existía. Se creó un archivo de ejemplo.")
    
    with open(archivo, 'r') as f:
        cuentas = f.readlines()
    
    return [cuenta.strip() for cuenta in cuentas if cuenta.strip()]

def ejecucion(cuenta):

    global total_tests, total_passed, total_failed  # Acceder a las variables globales
    with console_lock:
        print(f"Ejecutando test con la cuenta: {cuenta}")

    try:
        start_time = time.time()  # Tiempo inicial para la cuenta

        # Ejecutar el archivo de pruebas con pytest
        #ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',".."))
        ruta_base = sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))  
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-s", "-q", "--maxfail=1", "test/test_consulta_cuenta.py", "--cuenta", cuenta],
            #["python", "-m", "pytest", "-s", "-q", "--maxfail=1", "test/test_consulta_cuenta.py", "--cuenta", cuenta],
            #["pytest", "-s", "-q", "--maxfail=1", "test/test_consulta_cuenta.py", "--cuenta", cuenta],
            capture_output=True,
            text=True,
            check=False,
            cwd=ruta_base  # ?? cambia el directorio de trabajo al raíz del proyecto
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # Filtrar mensajes irrelevantes
        stdout_filtered = "\n".join(
            line for line in stdout.splitlines() 
            if "page_load_metrics_update_dispatcher" not in line and "TensorFlow Lite" not in line
        )
        stderr_filtered = "\n".join(
            line for line in stderr.splitlines() 
            if "page_load_metrics_update_dispatcher" not in line and "TensorFlow Lite" not in line
        )

        # Eliminar la sección de "Session info" y "Stacktrace"
        stdout_filtered = "\n".join(
            line for line in stdout_filtered.splitlines()
            if not any(keyword in line for keyword in ["Session info", "Stacktrace"])
        )
        stderr_filtered = "\n".join(
            line for line in stderr_filtered.splitlines()
            if not any(keyword in line for keyword in ["Session info", "Stacktrace"])
        )

        # Calcular tiempo transcurrido
        elapsed_time = time.time() - start_time

        # Incrementar el total de pruebas ejecutadas
        total_tests += 1

        # Evaluar el resultado de la ejecución
        if result.returncode == 0 and not ("Error" in stdout_filtered or "Traceback" in stdout_filtered):
            # Caso exitoso
            with console_lock:
                print(f"Prueba completada exitosamente para la cuenta {cuenta}.")
            resultados[cuenta] = f"Completada\nResultados: {stdout_filtered}"
            agregar_cuenta_junit(cuenta, "Completada", stdout_filtered, elapsed_time)
            total_passed += 1
        else:
            # Caso fallido
            with console_lock:
                print("")
                print(f"Error detectado en la ejecución para la cuenta {cuenta}.\n{stdout_filtered}\n{stderr_filtered}")
            resultados[cuenta] = f"Fallida: {stderr_filtered}\nResultados: {stdout_filtered}"
            agregar_cuenta_junit(cuenta, "Fallida", stdout_filtered + "\n" + stderr_filtered, elapsed_time)
            total_failed += 1

    except subprocess.CalledProcessError as e:
        # Manejo de errores críticos en el subproceso
        elapsed_time = time.time() - start_time
        with console_lock:
            print(f"Error crítico en la ejecución de la cuenta {cuenta}: {e.stderr}")
        resultados[cuenta] = f"Error crítico: {e.stderr}"
        agregar_cuenta_junit(cuenta, "Error crítico", e.stderr, elapsed_time)
        total_failed += 1


def procesar_navegador(cuentas_queue):
    # Procesa las órdenes usando Selenium en navegadores Chrome.
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo sin cabeza
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Crear un directorio temporal seguro para Chrome
    temp_user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_user_data_dir}")

    driver = None
    try:
        #chromedriver_path = r"D:\Modulo_Gestion\Nueva carpeta\automatizacion_modulo_gestion-develop\drivers\chromedriver.exe"
        #service = Service(chromedriver_path)
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        

        print("Navegador iniciado correctamente en procesar_navegador.")

        while not cuentas_queue.empty():
            cuenta = cuentas_queue.get()
            try:
                ejecucion(cuenta)
            except Exception as e:
                print(f"Error al procesar cuenta {cuenta}: {e}")
                traceback.print_exc()

    except Exception as e:
        print("Error al abrir el navegador desde consulta cuenta:")
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado correctamente.")

def abrir_navegador_x_veces(x, archivo_cuentas):
    #Abre x instancias de navegadores para procesar órdenes en paralelo.
    inicializar_junit()  # Asegurar que el archivo JUnit esté listo
    cuentas = leer_cuentas(archivo_cuentas)
    if len(cuentas) < x:
        print("")
        print(f"Advertencia: Hay {len(cuentas)} órdenes, pero se solicitaron {x} navegadores.")
    
    cuentas_queue = queue.Queue()
    for cuenta in cuentas:
        cuentas_queue.put(cuenta)
    
    with ThreadPoolExecutor(max_workers=x) as executor:
        futures = [executor.submit(procesar_navegador, cuentas_queue) for _ in range(x)]
        for future in as_completed(futures):
            future.result()

# Configuración inicial
num_threads = int(os.getenv("NUM_THREADS", 4))

# Medir tiempo de ejecución
start_time = time.time()

try:
    abrir_navegador_x_veces(num_threads, "utils/txt/cuentas_aprovisionamiento_ingresar.txt")
except FileNotFoundError as e:
    print(e)
finally:
    # Mostrar resumen después de todas las pruebas
    end_time = time.time()
    total_time = end_time - start_time

        # Convertir tiempo a horas, minutos y segundos
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Imprimir resultados
    print("")
    print("------ Resumen de pruebas: ------")
    print(f"Total de pruebas ejecutadas: {total_tests}")
    print(f"Total de pruebas exitosas: {total_passed}")
    print(f"Total de pruebas fallidas: {total_failed}\n")
    print(f"Tiempo total de ejecución: {int(hours)} horas, {int(minutes)} minutos, {int(seconds)} segundos.")
    print("")
