import os
import sys

# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def esperar_elemento(driver, by, value, timeout=10, clickable=False):
    """Espera a que un elemento esté presente o clickeable"""
    wait = WebDriverWait(driver, timeout)
    if clickable:
        # Espera hasta que el elemento sea clickeable
        return wait.until(EC.element_to_be_clickable((by, value)))
    else:
        # Espera hasta que el elemento esté presente
        return wait.until(EC.presence_of_element_located((by, value)))
