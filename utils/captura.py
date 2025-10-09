import os
import shutil
from datetime import datetime

class Capturas:
    @staticmethod
    def limpiar_subcarpeta(subcarpeta, carpeta_raiz="screenshot"):
        """
        Limpia (elimina y recrea) una subcarpeta específica dentro de 'screenshot'.
        
        Ejemplo:
            limpiar_subcarpeta("carpeta_a/navegacion")
        """
        try:
            # Construir la ruta absoluta completa
            ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            ruta_completa = os.path.join(ruta_proyecto, carpeta_raiz, subcarpeta)

            # Si existe, eliminarla
            if os.path.exists(ruta_completa):
                shutil.rmtree(ruta_completa)
                #print(f"[INFO] Subcarpeta '{ruta_completa}' eliminada.")

            # Volver a crearla vacía
            os.makedirs(ruta_completa)
            #print(f"[INFO] Subcarpeta '{ruta_completa}' creada nuevamente.")
        except Exception as e:
            print(f"[ERROR] No se pudo limpiar la subcarpeta '{ruta_completa}': {e}")

    @staticmethod
    def tomar_pantallazo(driver, nombre_base="captura", subcarpeta="carpeta_a", categoria="general", carpeta_raiz="screenshot"):
        # Obtener la ruta absoluta del directorio del proyecto
        ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        #driver.maximize_window()  # Maximiza el navegador
         # Forzar zoom al 100%
        driver.execute_script("document.body.style.zoom='100%'")
        # Establecer tamaño fijo adecuado (como en la imagen)
        driver.set_window_size(1280, 720)

        # Construir la ruta final según si hay categoría o no
        if categoria:
            carpeta_final = os.path.join(carpeta_raiz, subcarpeta, categoria)
        else:
            carpeta_final = os.path.join(carpeta_raiz, subcarpeta)

        if not os.path.exists(carpeta_final):
            os.makedirs(carpeta_final)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        nombre_archivo = f"{nombre_base}_{timestamp}.png"
        ruta_completa = os.path.join(carpeta_final, nombre_archivo)

        driver.save_screenshot(ruta_completa)
        return ruta_completa
    
    @staticmethod
    def tomar_pantallazo_especial(driver, nombre_base="captura", subcarpeta="", carpeta_raiz="screenshot"):
        # Obtener la ruta absoluta del directorio del proyecto
        ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        #driver.maximize_window()  # Maximiza el navegador
        driver.execute_script("document.body.style.zoom='100%'")
        # Establecer tamaño fijo adecuado (como en la imagen)
        driver.set_window_size(1280, 720)

        # Construir ruta final
        carpeta_final = os.path.join(ruta_proyecto, carpeta_raiz, subcarpeta)
        os.makedirs(carpeta_final, exist_ok=True)

        # Nombre con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        nombre_archivo = f"{nombre_base}_{timestamp}.png"
        ruta_completa = os.path.join(carpeta_final, nombre_archivo)

        driver.save_screenshot(ruta_completa)
        return ruta_completa
