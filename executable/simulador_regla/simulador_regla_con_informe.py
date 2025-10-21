import os
import sys
os.environ["GENERAR_REPORTE"] = "TRUE"
import pytest
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

# Configuración de entorno y logging
load_dotenv()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suprimir mensajes de TensorFlow
logging.basicConfig(level=logging.ERROR)  # Suprimir mensajes de logging

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
output_file = "reports/junit/resultados_junit_simulador_regla.xml"

# Variables para contar tests
total_tests = 0
total_passed = 0
total_failed = 0

def inicializar_junit():
    """Inicializa el archivo JUnit con una estructura base, sobrescribiendo el archivo existente."""
    # Crear la estructura base del archivo JUnit
    testsuites = ET.Element("testsuites")
    testsuite = ET.SubElement(testsuites, "testsuite", {
        "name": "MG_Simulador_regla",
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
    """
    Filtra la salida para eliminar información no relevante como stacktraces y detalles técnicos.
    """
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
    """Actualiza los atributos del testsuite según los resultados."""
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
def agregar_orden_junit(id_orden, detalle, resultado, tiempo):
    """
    Agrega un nuevo caso de prueba al archivo JUnit con el formato requerido.
    """
    # Cargar y analizar el archivo XML existente
    tree = ET.parse(output_file)
    root = tree.getroot()

    # Obtener o crear el testsuite
    testsuite = root.find("testsuite")
    if testsuite is None:
        testsuite = ET.SubElement(root, "testsuite", {
            "name": "MG_Aprovisionamiento",
            "tests": "0",
            "failures": "0",
            "passed": "0",  # Añadir el campo "passed" si no existe
            "time": "0"
        })

    # Evaluar si la orden ha fallado o fue exitosa
    fallo = "Fallida" in detalle or "Error" in detalle
    paso = not fallo  # Si no falló, se considera como éxito

    # Actualizar la información del testsuite
    actualizar_testsuite(testsuite, tiempo, fallo=fallo, paso=paso)

    # Limpiar la salida
    detalle_limpio = limpiar_salida(detalle)
    resultado_limpio = limpiar_salida(resultado)

    # Crear el testcase para la orden
    testcase = ET.SubElement(testsuite, "testcase", {
        "name": f"orden_{id_orden}",
        "time": formatear_tiempo(tiempo)  # Formateamos el tiempo en HH:MM:SS
    })
    detail = ET.SubElement(testcase, "system-out")
    detail.text = f"Estado: {detalle_limpio}\nResultados: {resultado_limpio}"

    # Si la orden falló, agregar una etiqueta de fallo
    if fallo:
        failure = ET.SubElement(testcase, "failure", {
            "message": f"Error en la orden {id_orden}"
        })
        failure.text = detalle_limpio

    # Guardar los cambios en el archivo JUnit
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def leer_ordens(archivo):
    """Lee las órdenes desde un archivo de texto."""
    if not os.path.exists(archivo):
        # Crear un archivo de ejemplo si no existe
        with open(archivo, 'w') as f:
            f.write("orden1\norden2\norden3")
        raise FileNotFoundError(f"El archivo {archivo} no existía. Se creó un archivo de ejemplo.")
    
    with open(archivo, 'r') as f:
        ordens = f.readlines()
    
    return [orden.strip() for orden in ordens if orden.strip()]

def ejecucion(orden, driver):
    """Ejecuta pruebas con Selenium y pytest para la orden dada."""
    global total_tests, total_passed, total_failed  # Acceder a las variables globales
    with console_lock:
        print(f"Ejecutando test con la orden: {orden}")

    try:
        start_time = time.time()  # Tiempo inicial para la orden

        # Ejecutar el archivo de pruebas con pytest
        ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',".."))
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-s", "-q", "--maxfail=1", "test/test_simulador_regla.py", "--orden", orden],
            #["python", "-m", "pytest", "-s", "-q", "--maxfail=1", "test/test_simulador_regla.py", "--orden", orden],
            #["pytest", "-s", "-q", "--maxfail=1", "test/test_simulador_regla.py", "--orden", orden],
            capture_output=True,
            text=True,
            check=False,
            cwd=ruta_base  # 👈 cambia el directorio de trabajo al raíz del proyecto
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
                print(f"Prueba completada exitosamente para la orden {orden}.")
            resultados[orden] = f"Completada\nResultados: {stdout_filtered}"
            agregar_orden_junit(orden, "Completada", stdout_filtered, elapsed_time)
            total_passed += 1
        else:
            # Caso fallido
            with console_lock:
                print("")
                print(f"Error detectado en la ejecución para la orden {orden}.\n{stdout_filtered}\n{stderr_filtered}")
            resultados[orden] = f"Fallida: {stderr_filtered}\nResultados: {stdout_filtered}"
            agregar_orden_junit(orden, "Fallida", stdout_filtered + "\n" + stderr_filtered, elapsed_time)
            total_failed += 1
        pass
    except subprocess.CalledProcessError as e:
        # Manejo de errores críticos en el subproceso
        elapsed_time = time.time() - start_time
        with console_lock:
            print(f"Error crítico en la ejecución de la orden {orden}: {e.stderr}")
        resultados[orden] = f"Error crítico: {e.stderr}"
        agregar_orden_junit(orden, "Error crítico", e.stderr, elapsed_time)
        total_failed += 1
        sys.exit(1)  # Esto hace que subprocess lo detecte como fallo


def procesar_navegador(ordens_queue):
    """Procesa las órdenes usando Selenium en navegadores Chrome."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo sin cabeza
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        while not ordens_queue.empty():
            orden = ordens_queue.get()
            ejecucion(orden, driver)
        pass
    except Exception as e:
        with console_lock:
            print(f"Error al abrir el navegador: {e}")
            sys.exit(1)  # Esto hace que subprocess lo detecte como fallo
    finally:
        if driver:
            driver.quit()

def abrir_navegador_x_veces(x, archivo_ordens):
    """Abre x instancias de navegadores para procesar órdenes en paralelo."""
    inicializar_junit()  # Asegurar que el archivo JUnit esté listo
    ordens = leer_ordens(archivo_ordens)
    if len(ordens) < x:
        print("")
        print(f"Advertencia: Hay {len(ordens)} órdenes, pero se solicitaron {x} navegadores.")
    
    ordens_queue = queue.Queue()
    for orden in ordens:
        ordens_queue.put(orden)
    
    with ThreadPoolExecutor(max_workers=x) as executor:
        futures = [executor.submit(procesar_navegador, ordens_queue) for _ in range(x)]
        for future in as_completed(futures):
            future.result()

# Configuración inicial
num_threads = int(os.getenv("NUM_THREADS", 4))

# Medir tiempo de ejecución
start_time = time.time()

try:
    abrir_navegador_x_veces(num_threads, "utils/txt/orders_simulador_regla.txt")
    pass
except FileNotFoundError as e:
    print(e)
    sys.exit(1)  # Esto hace que subprocess lo detecte como fallo
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
