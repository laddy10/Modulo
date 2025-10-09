import os
import traceback
import tempfile
import shutil
import atexit
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Cargar variables de entorno
load_dotenv()

def iniciar_navegador():
    temp_profile = None
    try:
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-features=Vulkan,UseChromeOSDirectVideoDecoder,TranslateUI")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--window-size=2280,1720")
        chrome_options.add_argument("--force-device-scale-factor=1")

        # Crear un perfil único por ejecución
        temp_profile = tempfile.mkdtemp(prefix="chrome_profile_")
        chrome_options.add_argument(f"--user-data-dir={temp_profile}")

        # Borrar el perfil temporal al salir, aunque haya error
        atexit.register(lambda: shutil.rmtree(temp_profile, ignore_errors=True))

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        width, height = driver.execute_script("return [window.innerWidth, window.innerHeight];")
        print(f"Viewport aplicado: {width}x{height}")

        return driver

    except Exception:
        print("Error al iniciar el navegador desde navegar:")
        print(traceback.format_exc())
        if temp_profile and os.path.exists(temp_profile):
            shutil.rmtree(temp_profile, ignore_errors=True)
        return None
