from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import necessário para o ENTER

from utils import logger

import time
import os
kjhsdf, s,

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
        """Tenta clicar diretamente, se falhar usa JavaScript."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

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
        # Insere endereço no campo de busca
        ''' BUG FIXING:
        0. Normalmente a página já é carregada com o cursor na barra de busca - mas isso não é robusto pra todos os casos.
        1. Localiza a barra de busca usando uma lista prioritária de seletores (Fallback: Name > ID > CSS),
           contornando IDs dinâmicos gerados pelo Google. (07/01/2026)
        2. Dispara a pesquisa via tecla ENTER, eliminando a dependência do botão de lupa instável.'''
        
        search_input = None # O input na barra de busca
        
        # Lista de seletores par as  tentativas - da mais provável para a menos provável
        seletores = [
            (By.NAME, "q"),                               
            (By.ID, "searchboxinput"),                    
            (By.CSS_SELECTOR, "input[role='combobox']"),  # Semântico (baseado no HTML)
            (By.XPATH, "//input[@autofocus]")             # Genérico (o campo de busca costuma ter foco)
        ]

        # Testa pra cada tupla (by_type, locator) se acha o campo 
        i: int  = 0
        for (by_type, locator) in seletores: 
            i+=1
            try:
                # Tenta achar com timeout curto (2s)
                search_input = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((by_type, locator))
                )
                logger.info(f"Campo de busca encontrado usando: {locator} - em menos de {i*2} segs")
                break # Se achou, sai do loop
            except Exception:
                continue # Se não achou, tenta o próximo

        if not search_input:
            logger.error(f"ERRO CRÍTICO: Não foi possível encontrar a barra de pesquisa com nenhum seletor - testes duraram {i*2}segs.")
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
            input ("INPUT DE DEBUG. APERTE ENTER PARA CONTINUAR")
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
