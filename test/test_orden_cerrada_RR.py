import pytest
import time
import os
import csv
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException,ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#task
from abilities.navegar import iniciar_navegador
from utils.descifrar_contrasena import obtener_contrasena
from abilities.navegar import iniciar_navegador
from task.login import Login
from task.navMenu import NavMenu
from task.consulta import Consulta
from task.validarResultados import resultados
from utils.descifrar_contrasena import obtener_contrasena


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables definidas en el archivo .env 
BASE_URL = os.getenv('BASE_URL')
USUARIO = os.getenv('USUARIO')
CONTRASENA = obtener_contrasena()

# Validar si las variables de entorno están definidas
if not BASE_URL or not USUARIO or not CONTRASENA:
    raise ValueError("BASE_URL, USUARIO o CONTRASENA no están definidas en el archivo .env")

# Fixture para aceptar el parámetro de la orden
@pytest.fixture
def orden(request):
    return request.config.getoption("--orden")

class TestCaso1OrdenCerradaenRR:

    def setup_method(self, method):
        self.driver = iniciar_navegador()

        self.vars = {}

        # Cargar variables de entorno
        self.base_url = os.getenv("BASE_URL")
        self.usuario = os.getenv("USUARIO")
        self.contrasena = os.getenv("CONTRASENA")

    def teardown_method(self, method):
        self.driver.quit()

    def medir_tiempo(self, bloque_inicio, bloque_fin):
        """Mide el tiempo de ejecución de un bloque de código."""
        start_time = time.time()  # Registrar tiempo de inicio
        time.sleep(bloque_inicio)  # Bloque que queremos medir
        end_time = time.time()  # Registrar tiempo de finalización
        elapsed_time = end_time - start_time  # Calcular tiempo transcurrido
        return elapsed_time

    def imprimir_tiempo(self, tiempo, max_time):
        """Imprime el tiempo de ejecución y verifica si excede el límite."""
        if tiempo > max_time:
            print(f"Advertencia: El tiempo de ejecución excedió los {max_time} segundos. Tiempo registrado: {tiempo:.2f} segundos")

    def test_caso1OrdenCerradaenRR(self, orden):
        # Registrar el inicio del tiempo total
        total_start_time = time.time()

        # Abrir el archivo de órdenes si no se ha pasado un orden específico
        if orden is None:
            
            with open("../../utils/orders.txt", "r") as f:
                ordenes = f.readlines()
        else:
            ordenes = [orden]  # Si se pasa un número de orden específico, usarlo directamente

        for orden in ordenes:
            orden = orden.strip()
            if not orden:
                print("Se encontró una línea vacía en el archivo de órdenes, se omite esta línea.")
                continue

            # Navegar a la URL
            time.sleep(10)
            self.driver.get(BASE_URL)
            time.sleep(10)
            self.driver.set_window_size(1296, 688)

            # Esperar que el documento esté completamente cargado
            WebDriverWait(self.driver, 10).until(
              lambda driver: driver.execute_script("return document.readyState") == "complete"
           ) 

            # Esperar a que el formulario esté cargado
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".loginClaro-blockheader:nth-child(2) > .t:nth-child(2)")
                    )
                )    
            except Exception as e:
                print(f"Error al cargar el formulario de login: {e}")
                continue
            # LOGIN
            login = Login(self.driver, USUARIO, CONTRASENA)
            tipoRed_element = login.ingresar()
            self.vars["tipoRed"] = tipoRed_element

            #validacion modulo
        if self.driver.execute_script("return (arguments[0] !== null)", self.vars["tipoRed"]): #true
            self.driver.find_element(By.ID, "tipoRed").click()
            dropdown = self.driver.find_element(By.ID, "tipoRed")
            dropdown.find_element(By.XPATH, "//option[. = 'Operaciones']").click()
            try:
                # Hacer clic en el botón "Submit"
                self.driver.find_element(By.ID, "Submit").click()
                time.sleep(10)

                # Validar error de ingreso
                try:
                    self.vars["errorIngreso"] = self.driver.execute_script(
                        "return !!document.querySelector('#DvActividad > table > tbody > tr:nth-child(3) > td > b > font')?.textContent.trim();"
                    )

                    if self.vars["errorIngreso"]:
                        self.vars["valueIngreso"] = self.driver.find_element(
                            By.XPATH, "//div[@id='DvActividad']/table/tbody/tr[3]/td/b/font"
                        ).text
                        print(f"Error: {self.vars['valueIngreso']}")
                        return  # Salir del método si hay error
                except Exception as e:
                    print("Error durante la validación de ingreso:", e)
                time.sleep(2)

                # NAV MENU
                # Crear una instancia de la clase NavMenu
                menu = NavMenu(self.driver)
                # Llamar al método navegar_por_menu
                menu.menu_agendaWFM()
                
                time.sleep(2)
                
                # CONSULTA
                ruta_archivo = os.path.join(os.path.dirname(__file__), "..", "utils", "orders.txt")
                consultaOT = Consulta(self.driver)

                # Leer las órdenes desde el archivo
                with open(ruta_archivo, "r") as archivo:
                    ordenes = [line.strip() for line in archivo if line.strip()]

                # Ejecutar la consulta por cada orden
                for orden in ordenes:
                    consultaOT.consulta_agendaWFM(orden)
                    time.sleep(5)  # espera opcional entre consultas para evitar sobrecarga
                
                #RESULTADOS
                resul = resultados(self.driver)
                resul.resultados_agendawfm()
                #resultados_agendawfm(self)

            except Exception as e:
                print("Error durante la validación de ingreso:", e)
            except TimeoutException as te:
                print("Error de tiempo de espera:", te)
            except NoSuchElementException as nse:
                print("Error: Elemento no encontrado:", nse)
            except Exception as e:
                print("Error desconocido:", e)
        else: #false
            
            try:
                # Hacer clic en el botón "Submit"
                self.driver.find_element(By.ID, "Submit").click()
                time.sleep(10)
                
                # Validar error de ingreso
                try:
                    self.vars["errorIngreso"] = self.driver.execute_script(
                        "return !!document.querySelector('#DvActividad > table > tbody > tr:nth-child(3) > td > b > font')?.textContent.trim();"
                    )

                    if self.vars["errorIngreso"]:
                        self.vars["valueIngreso"] = self.driver.find_element(
                            By.XPATH, "//div[@id='DvActividad']/table/tbody/tr[3]/td/b/font"
                        ).text
                        print(f"Error: {self.vars['valueIngreso']}")
                        return  # Salir del método si hay error
                except Exception as e:
                    print("Error durante la validación de ingreso:", e)
                time.sleep(2)

                # NAV MENU
                # Crear una instancia de la clase NavMenu
                menu = NavMenu(self.driver)
                # Llamar al método navegar_por_menu
                menu.menu_agendaWFM()
                
                time.sleep(2)
                
                 # CONSULTA
                ruta_archivo = os.path.join(os.path.dirname(__file__), "..", "utils", "orders.txt")
                consultaOT = Consulta(self.driver)
                
                # Leer las órdenes desde el archivo
                with open(ruta_archivo, "r") as archivo:
                    ordenes = [line.strip() for line in archivo if line.strip()]

                # Ejecutar la consulta por cada orden
                for orden in ordenes:
                    consultaOT.consulta_agendaWFM(orden)
                    time.sleep(5)  # espera opcional entre consultas para evitar sobrecarga
                
                #RESULTADOS
                resul = resultados(self.driver)
                resul.resultados_agendawfm()

            except Exception as e:
                print("Error durante la validación de ingreso:", e)
            except TimeoutException as te:
                print("Error de tiempo de espera:", te)
            except NoSuchElementException as nse:
                print("Error: Elemento no encontrado:", nse)
            except Exception as e:
                print("Error desconocido:", e)