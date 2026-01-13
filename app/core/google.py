from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import necessário para o ENTER
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Optional        # modulo de tipagem

from utils import logger

import time
import os


class GoogleMapsAuto:
    """
    Classe para automatizar tarefas relacionadas ao Google Maps via Selenium.
    """

    def __init__(self, driver, url: str, endereco, pasta_download, timeout: int = 10):
        """
        :param driver: instância do Selenium WebDriver
        :param url: URL do Google Maps
        :param timeout: tempo de espera padrão para WebDriverWait
        """
        self.driver = driver
        self.url = url
        self.endereco = endereco
        self.pasta_download = pasta_download
        self.wait = WebDriverWait(self.driver, timeout=timeout)

    def _click(self, element):
        """ O click clássico (e robusto): Tenta clicar diretamente, se falhar usa JavaScript."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    # Definie um método de achar elemento e clicar (ou não) robusto, que devolve o elemento encontrado.
    # Usa **kwargs (keyword arguments para gerar automaticamente o dicionário de seletores na ordem passada)
    def _interact(
        self, 
        nome_log: str, 
        timeout_tentativa: float = 2.0,
        clicar: bool = True,
        **seletores: str
    ) -> Optional[WebElement]:
        """ Um click ou element finder mais robusto com lógica de fallback em várias etpas implementada.
        Localiza um elemento usando estratégias de fallback baseadas nos argumentos passados e na ordem que são passados.
        Retorna o WebElement encontrado para uso posterior, caso necessário.

        Exemplo de uso:
            self._interagir("Botão", id="meu_id", xpath="//div", click=True)

        :param nome_log: Nome para registro no log.
        :param timeout_tentativa: [OPCIONAL - default: 2.0 segs] Tempo máximo de espera pra cada seletor achar o elmento - em segs.
        :param clicar: [[OPCIONAL - default: True] Se True, executa o _click() automaticamente ao encontrar.
        :param **seletores: Pares de estratégia=valor (ex: id="x", name="y", xpath="z").
                            A ordem dos argumentos define a prioridade.
        :return: O WebElement encontrado ou None, se falhar em todos os seletores.
        """
        # Define os tipo de métodos de procura válidos (tags do código fonte)
        # Útil para evitar que tags não previstas no selenium sejam testadas
        mapa_by = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class_name': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }

        tempo_gasto = 0
        
        # Itera sobre os argumentos passados (kwargs preserva ordem no Python 3.7+)
        for estrategia, valor_seletor in seletores.items():
            if estrategia not in mapa_by:
                continue # Ignora chaves inválidas

            by_type = mapa_by[estrategia]
            
            try:
                # Tenta encontrar
                elemento = WebDriverWait(self.driver, timeout_tentativa).until(
                    EC.element_to_be_clickable((by_type, valor_seletor))
                )
                
                tempo_gasto += timeout_tentativa
                logger.info(f"{nome_log} encontrado via '{estrategia}' em menos de {tempo_gasto:.1f} segs de busca.")
                
                # Se encontrou elemento e click é true, clica no elemento antes de devolvê-lo
                if clicar:
                    self._click(elemento)
                
                return elemento

            except Exception:
                tempo_gasto += timeout_tentativa
                continue # Falhou, tenta o próximo argumento

        logger.error(f"ERRO: {nome_log} não encontrado após todas as {len(seletores)} tentativas.\n"
                     "Tempo de procura por {nome_log}: {tempo_gasto:.1f} segs")
        return None

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
