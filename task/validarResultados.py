import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
from selenium.webdriver.common.action_chains import ActionChains
from utils.captura import Capturas  # <-- Capturas importada
from utils.reportes.reporte_word import ReporteDocumento
from utils.reportes.word import ReporteManager

class resultados:
    def __init__(self, reporte, driver):
        self.reporte = reporte
        self.driver = driver
        self.vars = {}

    def resultados_aprovisionamiento_ingresar(self, cuenta):
        ruta=[]
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located((By.ID, "ContainerData2"))
        )

        self.vars["nombreSuscriptoBoolean"] = self.driver.execute_script(
            "return !!document.querySelector('tr:nth-child(1) > td:nth-child(4) > .valor_validar')?.textContent.trim();"
        )
        self.vars["errorWebServices"] = self.driver.execute_script(
            "return !!document.querySelector('#ContainerData2')?.textContent.trim();"
        )

        if self.vars["nombreSuscriptoBoolean"]:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#CTA_SUSCRIPTOR > fieldset > legend"))
            )
            self.vars["nombreSuscriptor"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(1) > td:nth-child(4) > .valor_validar"
            ).text
            self.vars["estadoSuscriptor"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(2) > td:nth-child(2) > .valor_validar"
            ).text
            self.vars["servicioTelevision"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(4) > td:nth-child(2) font"
            ).text
            self.vars["servicioClaroBox"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(5) > td:nth-child(2) font"
            ).text
            self.vars["servicioInternet"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(4) > td:nth-child(4) font"
            ).text
            self.vars["servicioDTH"] = self.driver.find_element(
                By.CSS_SELECTOR, "tr:nth-child(5) > td:nth-child(4) font"
            ).text
            self.vars["servicioTelefonia"] = self.driver.find_element(
                By.CSS_SELECTOR, "td:nth-child(6) font"
            ).text

            print("\nInformación obtenida:")
            print(f"Cuenta: {cuenta}")
            print(f"Nombre del suscriptor: {self.vars['nombreSuscriptor']}")
            print(f"Estado del suscriptor: {self.vars['estadoSuscriptor']}")
            print(f"Televisión: {self.vars['servicioTelevision']}")
            print(f"Claro Box TV: {self.vars['servicioClaroBox']}")
            print(f"Internet: {self.vars['servicioInternet']}")
            print(f"DTH: {self.vars['servicioDTH']}")
            print(f"Telefonía: {self.vars['servicioTelefonia']}\n")

            ruta.append(Capturas.tomar_pantallazo(self.driver, "resultados_consulta","aprovisionamiento_ingresar", "Resultados"))

            time.sleep(3)
            if self.driver.execute_script("return (arguments[0] === \"SIN SERVICIO\" && arguments[1] === \"SIN SERVICIO\" && arguments[2] === \"SIN SERVICIO\" && arguments[3] === \"SIN SERVICIO\" && arguments[4] === \"SIN SERVICIO\")", self.vars["servicioTelevision"], self.vars["servicioClaroBox"], self.vars["servicioInternet"], self.vars["servicioDTH"], self.vars["servicioTelefonia"]):
                self.vars["suspendido"] = self.driver.find_element(By.CSS_SELECTOR, "fieldset > div:nth-child(3)").text
                #print("El suscriptor {} tiene es estado ${estadoSuscriptor} y esta ${suspendido}".format(self.vars["nombreSuscriptor"]))
                ruta.append(Capturas.tomar_pantallazo(self.driver, "Suspendido","aprovisionamiento_ingresar","Resultados"))
                print(
                "El suscriptor {} tiene el estado {} y está {}".format(
                    self.vars["nombreSuscriptor"],
                    self.vars.get("estadoSuscriptor", "NO DISPONIBLE"),
                    self.vars.get("suspendido", "NO DISPONIBLE")
                )
                )
            else:
                if self.driver.execute_script("return (arguments[0] === \"OK\" || arguments[0] === \"MODIFICAR\")", self.vars["servicioTelevision"]):
                    self.driver.find_element(By.LINK_TEXT, "TELEVISION").click()
                    self.vars["tablaTelevision"] = self.driver.execute_script("return !!document.querySelector('#TELEVISION .containerData3')?.textContent.trim();")
                    if self.driver.execute_script("return (arguments[0])", self.vars["tablaTelevision"]):
                        self.vars["infoTelevision"] = self.driver.find_element(By.CSS_SELECTOR, "#TELEVISION .containerData3").text
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_television","aprovisionamiento_ingresar", "Resultados"))
                        
                        print("DATOS TELEVISION")
                        print("{}".format(self.vars["infoTelevision"]))
                        print("")
                    else:
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_no_tabla_servicio_television", "aprovisionamiento_ingresar","Resultados"))
                        print("No hay información")

                if self.driver.execute_script("return (arguments[0] === \"OK\" || arguments[0] === \"MODIFICAR\")", self.vars["servicioClaroBox"]):
                    self.driver.find_element(By.LINK_TEXT, "CLARO_BOX_TV").click()
                    self.vars["tablaClaroBox"] = self.driver.execute_script("return !!document.querySelector('#CLARO_BOX_TV .containerData3')?.textContent.trim();")
                    if self.driver.execute_script("return (arguments[0])", self.vars["tablaClaroBox"]):
                        self.vars["infoClaroBox"] = self.driver.find_element(By.CSS_SELECTOR, "#CLARO_BOX_TV .containerData3").text
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_claro_box", "aprovisionamiento_ingresar", "Resultados"))
                        print("DATOS CLARO BOX TV")
                        print("{}".format(self.vars["infoClaroBox"]))
                        print("")
                    else:
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_no_tabla_servicio_claro_box", "aprovisionamiento_ingresar","Resultados"))
                        print("No hay información")

                if self.driver.execute_script("return (arguments[0] === \"OK\" || arguments[0] === \"MODIFICAR\")", self.vars["servicioInternet"]):
                    self.driver.find_element(By.LINK_TEXT, "INTERNET").click()
                    self.vars["tablaInternet"] = self.driver.execute_script("return !!document.querySelector('#INTERNET .containerData3')?.textContent.trim();")
                    if self.driver.execute_script("return (arguments[0])", self.vars["tablaInternet"]):
                        self.vars["infointernet"] = self.driver.find_element(By.CSS_SELECTOR, "#INTERNET .containerData3").text
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_Internet","aprovisionamiento_ingresar", "Resultados"))
                        print("DATOS INTERNET")
                        print("{}".format(self.vars["infointernet"]))
                        print("")

                        time.sleep(10)

                        self.vars["tipoFabricante"] = self.driver.find_element(By.CSS_SELECTOR, "#INTERNET tr:nth-child(1) > td:nth-child(1)").text
                        #print(self.vars["tipoFabricante"])
                        if "MTA" in self.vars["tipoFabricante"].upper():
                            time.sleep(5)
                            self.driver.find_element(By.ID, "comando").click()
                            dropdown = self.driver.find_element(By.ID, "comando")
                            dropdown.find_element(By.XPATH, "//option[. = 'Niveles']").click()
                            time.sleep(10)

                            print("Resultados Validacion Niveles")
                            wait = WebDriverWait(self.driver, 40)

                            element = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "table:nth-child(1) > tbody > tr:nth-child(1) > td > .valor_validar"))
                            )
                            self.vars["fechaMedicion"] = element.text
                            time.sleep(3)
                            print(f"     La FECHA MEDICION es: {self.vars['fechaMedicion']}")

                            #self.vars["fechaMedicion"] = self.driver.find_element(By.CSS_SELECTOR, "table:nth-child(1) > tbody > tr:nth-child(1) > td > .valor_validar").text
                            #print(f"     La FECHA MEDICION es: {self.vars['fechaMedicion']}")

                            self.vars["macAddress"] = self.driver.find_element(By.CSS_SELECTOR, "table:nth-child(1) > tbody > tr:nth-child(2) > td > .valor_validar").text
                            time.sleep(3)
                            print(f"     La MAC ADDRESS es: {self.vars['macAddress']}")
                            time.sleep(3)
                            print("     Potencia Señal")
                            self.vars["downstreamPS"] = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > td > fieldset tr:nth-child(1) font").text
                            #print(self.vars["downstreamPS"])
                            time.sleep(3)
                            print(f"          Downstream: {self.vars['downstreamPS']}")

                            self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > td > fieldset tr:nth-child(2) .valor_validar").click()
                            self.vars["upstreamPS"] = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > td > fieldset tr:nth-child(2) font").text
                            #print(self.vars["upstreamPS"])
                            time.sleep(3)
                            print(f"          Upstream: {self.vars['upstreamPS']}")
                            time.sleep(3)
                            print("     Relacion Ruido")
                            self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) > td > fieldset tr:nth-child(1) .valor_validar").click()
                            self.vars["downstreamRR"] = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) > td > fieldset tr:nth-child(1) font").text
                            #print(self.vars["downstreamRR"])
                            time.sleep(3)
                            print(f"          Downstream: {self.vars['downstreamRR']}")
                            
                            self.vars["upstreamRR"] = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) > td > fieldset tr:nth-child(2) font").text
                            #print(self.vars["upstreamRR"])
                            ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_internet_niveles","aprovisionamiento_ingresar", "Resultados"))
                            time.sleep(3)
                            print(f"          Upstream: {self.vars['upstreamRR']}")
                            print("")
                        else:
                            print(f"tipoFabricante no contiene 'MTA'. Valor actual: '{self.vars['tipoFabricante']}'")
                            print("")
                    else:
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_no_tabla_servicio_internet","aprovisionamiento_ingresar", "Resultados"))

                        print("No hay información")

                if self.driver.execute_script("return (arguments[0] === \"OK\" || arguments[0] === \"MODIFICAR\")", self.vars["servicioDTH"]):
                    self.driver.find_element(By.LINK_TEXT, "DTH").click()
                    self.vars["tablaDTH"] = self.driver.execute_script("return !!document.querySelector('.containerData3 > table > tbody > tr > td')?.textContent.trim();")
                    if self.driver.execute_script("return (arguments[0])", self.vars["tablaDTH"]):
                        self.vars["infoDTH"] = self.driver.find_element(By.CSS_SELECTOR, ".containerData3 > table > tbody > tr > td").text
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_DTH", "aprovisionamiento_ingresar", "Resultados"))
                        print("DATOS DTH")
                        print("{}".format(self.vars["infoDTH"]))
                        print("")
                    else:
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_no_tabla_servicio_DTH", "aprovisionamiento_ingresar", "Resultados"))
                        print("No hay información")

                if self.driver.execute_script("return (arguments[0] === \"OK\" || arguments[0] === \"MODIFICAR\")", self.vars["servicioTelefonia"]):
                    self.driver.find_element(By.LINK_TEXT, "TELEFONIA").click()
                    self.vars["tablaTelefonia"] = self.driver.execute_script("return !!document.querySelector('#TELEFONIA > fieldset')?.textContent.trim();")
                    if self.driver.execute_script("return (arguments[0])", self.vars["tablaTelefonia"]):
                        self.vars["infoTelefonia"] = self.driver.find_element(By.CSS_SELECTOR, "#TELEFONIA > fieldset").text
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_tabla_servicio_telefonia","aprovisionamiento_ingresar", "Resultados"))
                        print("{}".format(self.vars["infoTelefonia"]))
                        print("")
                    else:
                        ruta.append(Capturas.tomar_pantallazo(self.driver, "aprovisionamiento_no_tabla_servicio_telefonia", "aprovisionamiento_ingresar", "Resultados"))

                        print("No hay información")
        else:
            ruta.append(Capturas.tomar_pantallazo(self.driver, "no_existe_cuenta", "aprovisionamiento_ingresar", "Resultados"))
            print(f"La cuenta {cuenta} no existe.")
            
        return ruta
    
    def resultados_simulador_regla(self):
        ruta=[]
        driver = self.driver
        vars = self.vars
        time.sleep(3)
        vars["info"] = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#log td"))
        ).text
        print(str(vars["info"]))

        time.sleep(3)
        vars["tableActividad"] = driver.execute_script(
            "return !!document.querySelector('#log tr:nth-child(3)')?.textContent.trim();"
        )

        if driver.execute_script("return (arguments[0])", vars["tableActividad"]):
            print("\nPESTAÑA SIMULADOR OT")
            vars["infoTableActividad"] = driver.find_element(By.ID, "log").text
            print(str(vars["infoTableActividad"]))
            ruta.append(Capturas.tomar_pantallazo(driver, "pestaña_simulador_OT", "simulador_regla", "Resultados"))
            print("\nPESTAÑA LOG DE SIMULACION")
            driver.find_element(By.LINK_TEXT, "Log de simulacion").click()
            vars["InfoLog"] = driver.find_element(By.ID, "tabs-2").text
            ruta.append(Capturas.tomar_pantallazo(driver, "pestaña_log_simulacion", "simulador_regla", "Resultados"))
            print(str(vars["InfoLog"]))
        else:
            print("\nPESTAÑA SIMULADOR OT")
            driver.find_element(By.ID, "origen").click()
            dropdown = driver.find_element(By.ID, "origen")
            time.sleep(3)
            dropdown.find_element(By.XPATH, "//option[. = 'Llamada de servicio']").click()
            ruta.append(Capturas.tomar_pantallazo(driver, "consulta", "simulador_regla", "Consulta"))
            time.sleep(3)
            driver.find_element(By.ID, "consultar").click()
            time.sleep(3)
            vars["infoTableActividad"] = driver.find_element(By.ID, "log").text
            
            ruta.append(Capturas.tomar_pantallazo(driver, "pestaña_simulador_OT", "simulador_regla", "Resultados"))
            print(str(vars["infoTableActividad"]))

            print("\nPESTAÑA LOG DE SIMULACION")
            driver.find_element(By.LINK_TEXT, "Log de simulacion").click()
            vars["InfoLog"] = driver.find_element(By.ID, "tabs-2").text
            
            ruta.append(Capturas.tomar_pantallazo(driver, "pestaña_log_simulacion", "simulador_regla", "Resultados"))
            print(str(vars["InfoLog"]))
        
        return ruta

    def resultados_agendawfm(self):
        # Capturar estados y validaciones
        try:
            self.vars["dialogo"] = self.driver.execute_script("return !!document.getElementById('dialog_msg_dialog');")
            self.vars["titulo"] = self.driver.execute_script("return document.querySelector('.Cabecera:nth-child(1) > .Banner') !== null;")
            self.vars["estVisita"] = self.driver.execute_script("return document.querySelector('#estadoag') !== null;")
        except Exception as e:
            print(f"Error al capturar el estado de la página: {e}")
            return  # Aquí no deberías continuar con el resto si hay error
        # Validaciones
        if self.vars["dialogo"]:
            self.vars["dialogText"] = self.driver.find_element(By.ID, "dialog_msg_dialog").text
            time.sleep(2)
            if self.vars["dialogText"] == "La orden se encuentra cerrada en RR":
                try:
                    element = WebDriverWait(self.driver, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-state-focus > .ui-button-text"))
                    )
                    element.click()
                except TimeoutException:
                    print("Tiempo de espera excedido. No se encontró el elemento.")
                except NoSuchElementException:
                    print("No se encontró el elemento en el DOM.")
                except Exception as e:
                    print(f"Ocurrió un error inesperado: {e}")
                
                time.sleep(2)
                self.vars["estado"] = self.driver.find_element(By.ID, "estadoag").text
                if self.vars["estado"] in ["COMPLETADO", "CANCELADA", "NO AGENDADO"]:
                    try:
                        element = WebDriverWait(self.driver, 20).until(
                            EC.element_to_be_clickable((By.ID, "actividades_facturables_menu"))
                        )
                        element.click()
                    except ElementClickInterceptedException:
                        print("Elemento bloqueado. Intentando con ActionChains...")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element).click().perform()
                    except TimeoutException:
                        print("El elemento no se volvió clickeable dentro del tiempo especificado.")
                    except NoSuchElementException:
                        print("El elemento no existe en el DOM.")
                    except Exception as e:
                        print(f"Ocurrió un error inesperado: {e}")
                    self.vars["trActividades"] = self.driver.execute_script("return document.querySelector('#tbody-tab-actividades-facturables-nuevas > tr') !== null;")
                    if not self.vars["trActividades"]:
                        print(f"{self.vars['dialogText']}, el estado está en {self.vars['estado']} y no tiene actividades")
                    else:
                        print(f"{self.vars['dialogText']}, el estado está en {self.vars['estado']} y tiene actividades")
        elif self.driver.execute_script("return (arguments[0])", self.vars["titulo"]):
            self.vars["tituloMG"] = self.driver.find_element(By.CSS_SELECTOR, ".Cabecera:nth-child(1) > .Banner").text
            self.vars["tituloDatos"] = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > .Descripcion > .Banner").text
            if self.driver.execute_script("return (arguments[0] == \"MODULO DE AGENDAMIENTO\" && arguments[1] == \"DATOS DE LA ORDEN [Refrescar]\")", self.vars["tituloMG"], self.vars["tituloDatos"]):
                print("Es AGENDA ANTIGUA, validar el servicio: PSML consulta orden tt.")
        elif self.driver.execute_script("return (arguments[0])", self.vars["estVisita"]):
            self.vars["estReporgramada"] = self.driver.find_element(By.ID, "estadoag").text
            if self.driver.execute_script("return (arguments[0] != \"\")", self.vars["estReporgramada"]):
                self.vars["dia"] = self.driver.find_element(By.CSS_SELECTOR, ".td_content_agend:nth-child(1) tr:nth-child(3) > .verderesaltado:nth-child(2)").text
                self.vars["franja"] = self.driver.find_element(By.CSS_SELECTOR, ".td_content_agend:nth-child(1) tr:nth-child(3) > .verderesaltado:nth-child(4)").text
                self.driver.find_element(By.ID, "actividades_facturables_menu").click()
                self.vars["trActividades"] = self.driver.execute_script("return document.querySelector('#tbody-tab-actividades-facturables-nuevas > tr') !== null;")
            if not self.vars["trActividades"]:
                print(f"La visita tiene el estado {self.vars['estReporgramada']} con fecha programada del {self.vars['dia']} en la franja horaria {self.vars['franja']} y no tiene actividades")
            else:
                print(f"La visita tiene el estado {self.vars['estReporgramada']} con fecha programada del {self.vars['dia']} en la franja horaria {self.vars['franja']} y tiene actividades")