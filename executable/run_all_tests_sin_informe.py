import os
import sys
base_path = os.path.dirname(os.path.abspath(__file__))
proyecto_root = os.path.abspath(os.path.join(base_path, ".."))  # Ajusta según tu estructura
sys.path.append(proyecto_root)
import time
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from utils.errores_telegram.envio_error_telegram import enviar_a_queue, convertir_imagen_a_base64

os.environ["GENERAR_REPORTE"] = "FALSE"

# Lista de IPs donde ejecutar las pruebas
IPS = [
    "100.72.132.118",
    "100.72.132.123",
    "100.72.132.122",
    "100.72.132.116",
    "100.72.132.115"
]

# Lista de scripts en el orden exacto
ordered_scripts = [
    "login/login_sin_informe.py",
    "actualizacion_datos_WFM/actualizacion_datos_WFM_sin_informe.py",
    "aprovisionamiento_ingresar/consulta_cuenta_sin_informe.py",
    "simulador_regla/simulador_regla_sin_informe.py",
]

# Diccionario que relaciona IP con nombre de nodo
NODOS = {
    "100.72.132.118": "LNXMODULOGESPR01",
    "100.72.132.123": "LNXMODULOGESPR02",
    "100.72.132.122": "LNXMODULOGESPR03",
    "100.72.132.116": "LNXMODULOGESPR04",
    "100.72.132.115": "LNXMODULOGESPR05"
}

# Función para validar conexión al puerto 8005
def validar_conexion(ip, puerto=8005, timeout=2, log_file_path=None):
    try:
        result = subprocess.run(
            #["nc", "-zv", "-w", str(timeout), ip, str(puerto)],
            capture_output=True,
            text=True
        )
        salida = (result.stdout + result.stderr).strip()

        # Fecha y hora para registro
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")

        if "Connected" in salida:
            print(f"[{ip}] Conexión al puerto {puerto} OK")

            # Log de conexión exitosa
            logs_dir = os.path.join(base_path, "../logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_file_path = os.path.join(logs_dir, f"resultados_executable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(f"Validación de Conexiones\n\n{fecha} / {hora} - [{ip}] Conexión al puerto {puerto} OK\n")

            return True
        else:
            print(f"[{ip}] Conexión fallida: {salida}")

            # Log de fallo
            logs_dir = os.path.join(base_path, "../logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_file_path = os.path.join(logs_dir, f"resultados_executable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(f"Validación de Conexiones\n\n{fecha} / {hora} - [{ip}] Error: Conexión fallida: {salida}\n")

            # Enviar a Telegram
            mensaje=f"PRUEBAS\nFecha y hora: {fecha} / {hora}\nNodo {NODOS.get(ip, ip)}\nError: ** TIMEOUT **\nDescripción Error: Validar que el servicio {NODOS.get(ip, ip)} en nodo {ip} esté arriba"
            enviar_a_queue("queue_telegram", mensaje, imagen_base64=None)
            return False

    except Exception as e:
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        print(f"[{ip}] Error al ejecutar nc: {e}")

        # Log de error al ejecutar nc
        logs_dir = os.path.join(base_path, "../logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, f"resultados_executable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"Validación de Conexiones\n\n{fecha} / {hora} - [{ip}] Error al ejecutar nc: {e}\n")

        # Enviar a Telegram
        mensaje=f"Fecha: {fecha}\nHora: {hora}\nNodo {ip}\nDescripción Error: Error al ejecutar el comando NCAT"
        enviar_a_queue("queue_telegram", mensaje, imagen_base64=None)
        return False



# Función que ejecuta todos los scripts para una IP
def ejecutar_en_ip(ip, log_file_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    proyecto_root = os.path.abspath(os.path.join(base_path, ".."))
    resultados = []

    # Configurar BASE_URL para esta IP
    base_url = f"http://{ip}:8005/index.php"
    env = os.environ.copy()
    env["BASE_URL"] = base_url
    env["PYTHONPATH"] = proyecto_root

    print(f"\nIniciando pruebas en: {base_url}")

    for script_rel in ordered_scripts:
        script_path = os.path.join(base_path, script_rel)
        print("=" * 100)
        print(f"[{ip}] Ejecutando: {script_rel}")

        if not os.path.isfile(script_path):
            print(f"[{ip}] [ERROR] Archivo no encontrado: {script_path}")
            resultados.append((script_rel, "ERROR: archivo no encontrado"))
            continue

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            env=env
        )

        if result.stdout:
            print(f"[{ip}] [STDOUT]:\n{result.stdout}")
        if result.stderr:
            print(f"[{ip}] [STDERR]:\n{result.stderr}")

        if result.returncode == 0:
            if "Traceback" in result.stdout or "Exception" in result.stdout:
                resultados.append((script_rel, "POSIBLE ERROR EN STDOUT"))
            else:
                resultados.append((script_rel, "OK"))

    print("=" * 100)

    # Crear carpeta logs si no existe
    logs_dir = os.path.join(base_path, "../logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Limpiar logs de más de 5 días
    ahora = time.time()
    dias_retencion = 5
    for archivo in os.listdir(logs_dir):
        if archivo.startswith("resultados_executable_") and archivo.endswith(".log"):
            ruta_archivo = os.path.join(logs_dir, archivo)
            if os.path.isfile(ruta_archivo):
                edad_dias = (ahora - os.path.getmtime(ruta_archivo)) / 86400
                if edad_dias > dias_retencion:
                    os.remove(ruta_archivo)

    # Usar modo 'w' si es la primera IP, 'a' para las siguientes
    mode = 'a'
    with open(log_file_path, mode, encoding='utf-8') as f:
        fecha_inicio = datetime.now().strftime("%Y-%m-%d")
        hora_inicio = datetime.now().strftime("%H:%M:%S")
        resumen = f"\nResumen de ejecucion\n\nFecha de ejecución: {fecha_inicio}\nHora de ejecución: {hora_inicio}\n\nResumen IP: {ip}\n"
        print(resumen.strip())
        f.write(resumen)
        for script, estado in resultados:
            linea = f"[{ip}] {script}: {estado}"
            print(linea)
            f.write(linea + "\n")

# Ejecutar en paralelo
if __name__ == "__main__":
    inicio = time.time()
    base_path = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_path, "../logs")

    os.makedirs(logs_dir, exist_ok=True)

    # Nombre único para toda la ejecución
    fecha_log = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(logs_dir, f"resultados_executable_{fecha_log}.log")

    # Filtrar IPs que respondan en el puerto 8005
    IPS_VALIDAS = [ip for ip in IPS if validar_conexion(ip)]

    if not IPS_VALIDAS:
        print("Ninguna IP está disponible. Terminando ejecución.")
        exit(1)

    with ThreadPoolExecutor(max_workers=len(IPS_VALIDAS)) as executor:
        #fecha_log = datetime.now().strftime("%Y%m%d_%H%M%S")
        #log_file_path = os.path.join(logs_dir, f"resultados_executable_{fecha_log}.log")
        executor.map(lambda ip: ejecutar_en_ip(ip, log_file_path), IPS_VALIDAS)

    fin = time.time()
    duracion = fin - inicio

    horas = int(duracion // 3600)
    minutos = int((duracion % 3600) // 60)
    segundos = int(duracion % 60)

    tiempo_total = f"\nTiempo total de ejecución: {horas}h {minutos}m {segundos}s"
    print(tiempo_total)

    # También guardar en el log
    log_file_path = os.path.join(logs_dir, "resultados_executable.log")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(tiempo_total + "\n")
