from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import necessário para o ENTER
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Optional        # modulo de tipagem

from utils import logger
from .base import BotBase               # Super classe da herança
import time
import os


class GoogleMapsAuto(BotBase):
    """
    Classe para automatizar tarefas relacionadas ao Google Maps via Selenium - classe que herda de BotBase.
    """

    def __init__(self, driver, url: str, endereco, pasta_download, timeout: int = 10):
        # Inicializa o Pai (configura self.driver e self.wait)
        super().__init__(driver, timeout)
        """
        :param driver: instância do Selenium WebDriver
        :param url: URL do Google Maps
        :param timeout: tempo de espera padrão para WebDriverWait
        """
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
            return

    def navegar(self):
        """Navega até o endereço, muda para satélite, faz prints e Street View."""
        # =========================================================================
        # 1. PESQUISA (Busca o elemento e recebe o objeto para digitar)
        # =========================================================================
        # A ordem dos parâmetros define a prioridade de busca:
        search_input = self._interact(
            nome_log="Campo de Busca",
            timeout_tentativa=1.5,  # Fail fast (1.5s por tentativa)
            clicar=True,            # Clica para garantir o foco
            
            # SELETORES (Prioridade Top -> Down):
            name="q",
            id="UGojuc",
            css="input[role='combobox']",
            xpath="//input[@autofocus]",
            # Fallback legado se quiser manter:
            # id_legado="searchboxinput" (Isso seria ignorado pelo seu mapa, a menos que adicione lá)
        )

        if not search_input:
            logger.error(f"ERRO CRÍTICO: Não foi possível encontrar a barra de pesquisa com nenhum seletor!\n ABORTANDO ROTINA NO GOOGLE MAPS E PROSSEGUINDO COM A TRIAGEM.")
            return

        #  INTERAGE COM O CAMPO ENCONTRADO
        try:
            search_input.click() # Garante o foco
            search_input.clear()
            
            if not self.endereco or self.endereco == "Não informado":
                logger.warning("IC sem endereço, pulando navegação google maps.")
                return

            search_input.send_keys(self.endereco)
            logger.info(f"Endereço digitado")
   
         
        except Exception as e:
            logger.error(f"Erro ao digitar no campo de busca: {e}")
            return

        # Aperta Enter para pesquisar (mais robusto pois não depende de modificações na interface do site)
        try:
            search_input.send_keys(Keys.ENTER)
            logger.info("Busca disparada via tecla ENTER")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Erro ao enviar a tecla ENTER  para disparar a busca: {e}")
            return

        # SELEÇÃO DO RESULTADO (Garante o Pinpoint e o Painel Lateral)
        try:
            # Tenta encontrar links de resultados na lista (classe comum hfpxzc) ou o container de sugestões.
            resultados = self.driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc, [role='article'] a")
            
            if resultados:
                logger.info(f"Múltiplos resultados encontrados ({len(resultados)}). Clicando no primeiro para fixar local.")
                self._click(resultados[0])
                time.sleep(4) # Espera carregar o painel lateral do local específico
            else:
                logger.info("Nenhuma lista detectada. O Maps parece ter ido direto para o ponto.")
        except Exception as e:
            logger.warning(f"Erro ao tentar selecionar da lista de resultados: {e}")

        # Clica no botão de camada (satélite)
        try:
            satellite_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.yHc72.qk5Wte"))
            )
            self._click(satellite_button)
            logger.info("Visualização satélite ativada")
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Não foi possível ativar visualização satélite: {e}")

        # Print da tela (satélite)
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
        except Exception as e:
            # input ("INPUT DE DEBUG. APERTE ENTER PARA CONTINUAR")
            logger.warning(f"Não foi possível clicar no Street View: {e}")
            return

        # Print da tela (fachada)
        try:
            caminho_print_fachada = os.path.join(
                self.pasta_download, "google_maps_fachada.png"
            )
            self.driver.save_screenshot(caminho_print_fachada)
            logger.info(f"Print da fachada salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar print da fachada: {e}")
