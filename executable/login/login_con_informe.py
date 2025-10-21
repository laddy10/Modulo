# pruebas.py

import os
import sys
os.environ["GENERAR_REPORTE"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))  
import threading
import time
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from utils.captura import Capturas  # <-- Capturas importada

#task
from test.test_login import ejecutar_pruebas

# Cargar variables de entorno
load_dotenv()
NUM_THREADS = int(os.getenv("NUM_THREADS", 1))

# Variables globales
pruebas_ejecutadas = [0]
pruebas_exitosas = [0]
pruebas_fallidas = [0]
hilos_ejecutados = [0]
errores_por_hilo = {}

def generar_reporte_junit():
    """Generar un archivo XML JUnit con los resultados"""
    testsuites = ET.Element("testsuites")

    main_testsuite = ET.SubElement(
        testsuites,
        "testsuite",
        name="TestLoginMG",
        tests=str(hilos_ejecutados[0]),
        failures=str(pruebas_fallidas[0]),
        passed=str(pruebas_exitosas[0]),
        time="0"
    )

    test_names = [
        "test_caso1Ingresoalainterfaz",
        "test_caso2ingreso_correcto",
        "test_caso3borrar_campos",
        "test_caso4USUA_incorrecto",
        "test_caso5CONTRA_incorrecta",
        "test_caso6USUA_vacio",
        "test_caso7CONTRA_vacia",
        "test_caso8campos_vacios"
    ]

    for hilo in range(1, hilos_ejecutados[0] + 1):
        if hilo in errores_por_hilo:
            failed_index, error_message = errores_por_hilo[hilo]
            thread_failures = 1
            thread_passed = failed_index
        else:
            thread_failures = 0
            thread_passed = len(test_names)

        hilo_testsuite = ET.SubElement(
            testsuites,
            "testsuite",
            name=f"hilo_{hilo}",
            tests=str(len(test_names)),
            failures=str(thread_failures),
            passed=str(thread_passed)
        )

        for i, name in enumerate(test_names):
            testcase = ET.SubElement(hilo_testsuite, "testcase", name=name)
            if hilo in errores_por_hilo and i == errores_por_hilo[hilo][0]:
                ET.SubElement(testcase, "failure", message=errores_por_hilo[hilo][1])

    tree = ET.ElementTree(testsuites)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Ruta al directorio 'reports' (dos niveles arriba desde executable)
    reports_dir = os.path.abspath(os.path.join(current_dir, "..","..", "reports", "junit"))
    os.makedirs(reports_dir, exist_ok=True)
    # Ruta completa del archivo de resultados
    output_path = os.path.join(reports_dir, "resultados_junit_login.xml")
    # Escribir el archivo
    with open(output_path, "wb") as file:
        tree.write(file)

if __name__ == "__main__":
    start_time = time.time()

    todos_hilos = []
    for i in range(1, NUM_THREADS + 1):
        hilo = threading.Thread(target=ejecutar_pruebas, args=(i, pruebas_ejecutadas, pruebas_exitosas, pruebas_fallidas, hilos_ejecutados, errores_por_hilo))
        todos_hilos.append(hilo)
        hilo.start()
        time.sleep(1)

    for hilo in todos_hilos:
        hilo.join()

    end_time = time.time()
    total_time = end_time - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"\n------ Resumen de pruebas: ------")
    print(f"Total pruebas ejecutadas: {hilos_ejecutados[0]}")
    print(f"Total de pruebas exitosas: {pruebas_exitosas[0]}")
    print(f"Total de pruebas fallidas: {pruebas_fallidas[0]}")
    print(f"\nTiempo total de ejecución: {int(hours)} horas, {int(minutes)} minutos y {seconds:.2f} segundos\n")

    generar_reporte_junit()