import sys
import os
os.environ["GENERAR_REPORTE"] = "FALSE"
GENERAR_REPORTE = os.getenv("GENERAR_REPORTE", "True").lower() == "true"
# Añade el directorio raíz del proyecto al path si no está ya
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))  
import unittest
import os
import time
import traceback
import xml.etree.ElementTree as ET
from xml.dom import minidom
import concurrent.futures

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
 
# screenplay
from abilities.navegar import iniciar_navegador
from task.login import Login
from task.navMenu import NavMenu
from task.consulta import Consulta
from test.test_actualizar_datos_WFM import esperar_elemento, validacion_campos
from utils.descifrar_contrasena import obtener_contrasena
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager

# Cargar variables desde .env
load_dotenv()
BASE_URL = os.getenv('BASE_URL')
USUARIO = os.getenv('USUARIO')
CONTRASENA = obtener_contrasena()
ID = os.getenv('ID')
MAX_WORKERS = int(os.getenv("HILOS", 1))


class TestModuloGestionCalidad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if GENERAR_REPORTE:
            cls.reporte = ReporteManager.obtener("actualizar_datos_WFM")
        else:
            cls.reporte = None        

    def setUp(self):
        self.driver = iniciar_navegador()
        self.driver.set_page_load_timeout(120)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.reporte = self.__class__.reporte

    def tearDown(self):
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        if cls.reporte:
            ReporteManager.guardar_todos()

    def test_1_ingreso_pagina(self):
        time.sleep(5)
        self.driver.get(BASE_URL)
        ruta1 = Capturas.tomar_pantallazo_especial(self.driver, "test_1_ingreso_pagina", "actualizar_datos_WFM", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("test 1 Ingreso Pagina", ruta1)

    def test_2_ingreso_credenciales(self):
        time.sleep(5)
        self.driver.get(BASE_URL)
        login = Login(self.reporte, self.driver, USUARIO, CONTRASENA)
        login.ingresar_actualizacion_datos_WFM()
        time.sleep(3)
        self.assertTrue(True, "Inicio de sesión ejecutado.")
        ruta2 = Capturas.tomar_pantallazo_especial(self.driver, "test_2_ingreso_credenciales","actualizar_datos_WFM", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("test 2 Ingreso Credenciales", ruta2)

    def test_3_consulta_documentoCorrecto(self):
        time.sleep(5)
        self.driver.get(BASE_URL)
        login = Login(self.reporte, self.driver, USUARIO, CONTRASENA)
        login.ingresar_actualizacion_datos_WFM()
        nav = NavMenu(self.reporte, self.driver)
        nav.menu_actualizacion_datos_WFM()
        consulta = Consulta(self.reporte, self.driver)
        consulta.consulta_actualizacion_datos_WFM(ID)
        validacion_campos(self.driver)
        ruta3 = Capturas.tomar_pantallazo_especial(self.driver, "test_3_consulta_documentoCorrecto","actualizar_datos_WFM", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("test 3 Consulta DocumentoCorrecto", ruta3)

    def test_4_consulta_documentoIncorrecto(self):
        time.sleep(5)
        self.driver.get(BASE_URL)
        login = Login(self.reporte, self.driver, USUARIO, CONTRASENA)
        self.assertTrue(login, "Falló el inicio de sesión tras varios intentos.")
        login.ingresar_actualizacion_datos_WFM()
        nav = NavMenu(self.reporte, self.driver)
        nav.menu_actualizacion_datos_WFM()
        consulta = Consulta(self.reporte, self.driver)
        consulta.consulta_actualizacion_datos_WFM("1024585387")  # Documento incorrecto
        error_xpath = "//div[@id='div_mensaje' and contains(@class, 'ui-dialog-content')]"
        error_msg_element = esperar_elemento(self.driver, By.XPATH, error_xpath, timeout=10)
        # Validar el texto del error
        self.assertEqual(error_msg_element.text.strip(), "No se encontro usuario en OFSC!!", "El mensaje de error no coincide")
        ruta4 = Capturas.tomar_pantallazo_especial(self.driver, "test_4_consulta_documentoIncorrecto","actualizar_datos_WFM", "screenshot")
        if self.reporte:
            self.reporte.agregar_evidencia("test 4 Consulta DocumentoIncorrecto", ruta4)

def generate_custom_xml(suite_results, total_time, max_workers):
    testsuites = ET.Element("testsuites")

    total_tests = len(suite_results)
    total_passed = sum(1 for r in suite_results.values() if r['success'])
    total_failures = total_tests - total_passed

    resumen_suite = ET.SubElement(
        testsuites, "testsuite",
        name="TestMGC",
        tests=str(total_tests),
        failures=str(total_failures),
        passed=str(total_passed),
        time=str(total_time)
    )

    print("\n------ Resumen de pruebas: ------")
    print(f"Total de pruebas ejecutadas: {total_tests}")
    print(f"Total de pruebas exitosas: {total_passed}")
    print(f"Total de pruebas fallidas: {total_failures}")
    print(f"Tiempo total de ejecución: {total_time:.2f} segundos.\n")

    for i in range(max_workers):
        hilo_suite = ET.SubElement(
            testsuites, "testsuite",
            name=f"hilo {i + 1}",
            tests=str(len(suite_results)),
            failures=str(total_failures),
            passed=str(total_passed)
        )

        for test_name, result in suite_results.items():
            testcase = ET.SubElement(hilo_suite, "testcase", name=test_name)
            if not result['success']:
                error_traceback = result.get('error', 'Error desconocido')
                error_node = ET.SubElement(testcase, "system-out")
                error_node.text = f"<![CDATA[\n{error_traceback}\n]]>"
            else:
                ET.SubElement(testcase, "system-out").text = "Exitoso"

    xml_str = ET.tostring(testsuites, encoding='utf-8', method='xml')
    parsed_str = minidom.parseString(xml_str)
    # Asegura que el directorio exista
    #os.makedirs("../reports/junit/", exist_ok=True)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(script_dir, "..", "reports", "junit")
    os.makedirs(report_dir, exist_ok=True)

    #with open("../reports/junit/resultados_junit_actualizacion_datos_WFM.xml", "w", encoding="utf-8") as f:
    #    f.write(parsed_str.toprettyxml(indent="  "))
    output_file = os.path.join(report_dir, "resultados_junit_actualizacion_datos_WFM.xml")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(parsed_str.toprettyxml(indent="  "))



def run_all_tests_in_thread():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModuloGestionCalidad)
    test_results = {}

    for test in suite:
        start_time = time.time()
        try:
            result = unittest.TextTestRunner().run(test)
            success = result.wasSuccessful()
            error = None if success else "Fallo en la ejecución."
        except Exception as e:
            success = False
            error = traceback.format_exc()

        duration = time.time() - start_time
        test_results[test._testMethodName] = {
            'success': success,
            'time': duration,
            'error': error
        }

    return test_results

def run_tests():
    suite_results = {}
    test_class = TestModuloGestionCalidad
    test_loader = unittest.TestLoader()
    test_names = test_loader.getTestCaseNames(test_class)

    for name in test_names:
        suite = unittest.TestSuite()
        suite.addTest(test_class(name))
        
        start_time = time.time()
        try:
            result = unittest.TextTestRunner().run(suite)
            success = result.wasSuccessful()
            error = None if success else "Fallo en la ejecución."
        except Exception as e:
            success = False
            error = traceback.format_exc()
        duration = time.time() - start_time
        
        suite_results[name] = {
            'success': success,
            'time': duration,
            'error': error
        }

    total_time = sum(r['time'] for r in suite_results.values())
    generate_custom_xml(suite_results, total_time, MAX_WORKERS)

if __name__ == '__main__':
    Capturas.limpiar_subcarpeta("actualizar_datos_WFM")
    run_tests()
    
