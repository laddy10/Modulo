from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

def obtener_contrasena():
    """
    Descifra y retorna la contraseña almacenada en el archivo .env.
    """
    # Cargar las variables desde el archivo .env
    load_dotenv()

    # Obtener ruta absoluta del archivo clave.key
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Ruta a /utils/
    clave_path = os.path.join(base_dir, "clave.key")       # Ruta completa a clave.key

    # Leer la clave desde el archivo clave.key
    with open(clave_path, "rb") as archivo_clave:
        clave = archivo_clave.read()

    # Crear un objeto Fernet con la clave
    fernet = Fernet(clave)

    # Obtener la contraseña cifrada desde el archivo .env
    contrasena_cifrada = os.getenv("CONTRASENA").encode()

    # Descifrar y retornar la contraseña
    return fernet.decrypt(contrasena_cifrada).decode()
