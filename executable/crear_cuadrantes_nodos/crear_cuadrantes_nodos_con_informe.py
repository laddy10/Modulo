# executable/crear_cuadrantes_nodos.py 
import os
import sys
import subprocess
import time
import logging
import xml.etree.ElementTree as ET
from datetime import timedelta
from dotenv import load_dotenv
os.environ["GENERAR_REPORTE"] = "TRUE"
# Configuración
load_dotenv()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.basicConfig(level=logging.ERROR)

output_file = "../reports/junit/resultados_junit_crear_cuadrantes_nodos.xml"
# Crear directorio si no existe
os.makedirs(os.path.dirname(output_file), exist_ok=True)
# Crear estructura básica del XML
testsuites = ET.Element("testsuites")
tree = ET.ElementTree(testsuites)
# Guardar el XML en el archivo
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"[OK] Archivo XML creado en: {output_file}")

def inicializar_junit():
    testsuites = ET.Element("testsuites")
    testsuite = ET.SubElement(testsuites, "testsuite", {
        "name": "MG_crear_cuadrantes_nodos",
        "tests": "0",
        "failures": "0",
        "passed": "0",
        "time": "0"
    })
    tree = ET.ElementTree(testsuites)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def limpiar_salida(salida):
    lineas = salida.splitlines()
    lineas_filtradas = [
        line for line in lineas if not (
            "GetHandleVerifier" in line or 
            "No symbol" in line or 
            "BaseThreadInitThunk" in line or 
            "RtlUserThreadStart" in line
        )
    ]
    return "\n".join(lineas_filtradas).strip()

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

def agregar_resultado_junit(nombre, detalle, resultado, tiempo):
    tree = ET.parse(output_file)
    root = tree.getroot()
    testsuite = root.find("testsuite")
    fallo = "Fallida" in detalle or "Error" in detalle
    paso = not fallo

    actualizar_testsuite(testsuite, tiempo, fallo=fallo, paso=paso)

    detalle_limpio = limpiar_salida(detalle)
    resultado_limpio = limpiar_salida(resultado)

    testcase = ET.SubElement(testsuite, "testcase", {
        "name": nombre,
        "time": formatear_tiempo(tiempo)
    })
    detail = ET.SubElement(testcase, "system-out")
    detail.text = f"Estado: {detalle_limpio}\nResultados: {resultado_limpio}"

    if fallo:
        failure = ET.SubElement(testcase, "failure", {
            "message": f"Error en el caso {nombre}"
        })
        failure.text = detalle_limpio

    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def ejecutar_prueba():
    print("Iniciando ejecución del test...")

    try:
        start_time = time.time()
        ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',".."))
        sys.path.insert(0, ruta_base)
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{ruta_base}:/oracle/python-libs"

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-s", "-q", "test/test_crear_cuadrantes_nodos.py"],
            capture_output=True,
            text=True,
            check=False,
            cwd=ruta_base,
            env=env
        )

        print(result.stdout if result.returncode == 0 else result.stderr)

        agregar_resultado_junit(
            "test_crear_cuadrantes_nodos",
            "Ejecución completada" if result.returncode == 0 else "Fallida",
            result.stdout if result.returncode == 0 else result.stderr,
            time.time() - start_time
        )

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error crítico en la ejecución: {e.stderr}")
        agregar_resultado_junit("test_crear_cuadrantes_nodo", "Error crítico", e.stderr, 0)

        
if __name__ == "__main__":
    inicializar_junit()
    ejecutar_prueba()
