from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Any, Optional
from utils import logger, settings
from .base import BotBase
import time
import os


class GoogleMapsAuto(BotBase):
    """
    Classe para automatizar tarefas relacionadas ao Google Maps via Selenium - classe que herda de BotBase.
    """

    def __init__(
        self,
        driver: WebDriver,
        url: str,
        endereco: str,
        pasta_download: str,
        timeout: float = 10.0,
    ):
        super().__init__(driver, settings.TIMEOUT_ESPERA)

        self.url = url
        self.endereco = endereco
        self.pasta_download = pasta_download

    def acessar_google_maps(self):
        """Abre a página inicial do Google Maps."""
        try:
            self.driver.get(self.url)
            logger.info(f"Acessando Google Maps")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Erro ao acessar o Google Maps: {e}")
            raise

    def navegar(self):
        """Navega até o endereço, muda para satélite, faz prints e Street View."""

        # Interage com o campo de busca para garantir o foco
        search_input = self._interact(
            nome_log="Campo de Busca",
            timeout_tentativa=1.5,
            clicar=True,
            name="q",
            id="UGojuc",
            css="input[role='combobox']",
            xpath="//input[@autofocus]",
        )

        if not search_input:
            logger.error(
                f"ERRO CRÍTICO: Não foi possível encontrar a barra de pesquisa com nenhum seletor!\n ABORTANDO ROTINA NO GOOGLE MAPS E PROSSEGUINDO COM A TRIAGEM."
            )
            raise

        #  INTERAGE COM O CAMPO ENCONTRADO
        try:
            search_input.click()
            search_input.clear()

            if not self.endereco or self.endereco == "Não informado":
                logger.warning("IC sem endereço, pulando navegação google maps.")
                return

            search_input.send_keys(self.endereco)
            logger.info(f"Endereço digitado")

        except Exception as e:
            logger.error(f"Erro ao digitar no campo de busca: {e}")
            return

        try:
            search_input.send_keys(Keys.ENTER)
            logger.info("Busca disparada via tecla ENTER")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Erro ao enviar a tecla ENTER  para disparar a busca: {e}")
            return

        # SELEÇÃO DO RESULTADO (Garante o Pinpoint e o Painel Lateral)
        try:
            resultados = self.driver.find_elements(
                By.CSS_SELECTOR, "a.hfpxzc, [role='article'] a"
            )

            if resultados:
                logger.info(
                    f"Múltiplos resultados encontrados ({len(resultados)}). Clicando no primeiro para fixar local."
                )
                self._click(resultados[0])
                time.sleep(4)
            else:
                logger.info(
                    "Nenhuma lista detectada. O Maps parece ter ido direto para o ponto."
                )
        except Exception as e:
            logger.warning(f"Erro ao tentar selecionar da lista de resultados: {e}")

        # Clica no botão de camada (satélite)
        error_counter = 0
        try:
            satellite_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.yHc72.qk5Wte"))
            )
            self._click(satellite_button)
            logger.info("Visualização satélite ativada")
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Não foi possível ativar visualização satélite: {e}")
            error_counter += 1

        # Print Aereo (satélite)
        try:
            caminho_print_aereo = os.path.join(
                self.pasta_download, "google_maps_aereo.png"
            )
            self.driver.save_screenshot(caminho_print_aereo)
            logger.info(f"Print da visualização aérea salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar print da visualização aérea: {e}")

        # Clica no botão para visualizar a fachada (Street View)
        try:
            street_view_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dQDAle"))
            )
            self._click(street_view_button)
            logger.info("Street View ativado")
            time.sleep(5)

            caminho_print_fachada = os.path.join(
                self.pasta_download, "google_maps_fachada.png"
            )
            self.driver.save_screenshot(caminho_print_fachada)
            logger.info(f"Print da fachada salvo")
        except Exception as e:
            logger.warning(f"Não foi possível clicar no Street View para capturar fachada: {e}")
            error_counter +=1

        if error_counter > 0:
            msg_erro = f"Automação Google Maps finalizada com {error_counter} erros. Solicitando retentativa (Retry)..."
            logger.error(msg_erro)
            raise Exception(msg_erro)
        
        logger.info("Automação Google Maps concluída com 100% de sucesso.")

