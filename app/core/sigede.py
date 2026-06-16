import time
import os
import re

from utils import logger, settings
from .base import BotBase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional


class SigedeAuto(BotBase):
    """
    Classe para automatizar tarefas relacionadas ao SIGEDE via Selenium - herda de BotBase.
    """

    def __init__(
        self, driver: WebDriver, url: str, usuario: str, senha: str, pasta_download: str
    ):

        super().__init__(driver, settings.TIMEOUT_ESPERA/2)

        self.url = url
        self.usuario = usuario
        self.senha = senha
        self.pasta_download = pasta_download

    def acessar(self) -> bool:
        try:
            logger.info("Acessando o Sistema 0: SIGEDE")
            self.driver.get(self.url)
            return True
        except Exception as e:
            logger.error("Erro ao acessar o sistema: %s", e)
            return False

    def login(self) -> bool:

        try:
            logger.info("Preenchendo usuário e senha")
            self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            ).send_keys(self.usuario)
            self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            ).send_keys(self.senha)

            # Busca pelo botão pelo value "ENTRAR"
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@value='ENTRAR']"))
            ).click()

            logger.info("Testando login...")

            time.sleep(5)
            return True
        except Exception as e:
            logger.error("Erro no login: %s", e)
            raise

    def navegar(self, protocolo: str) -> bool:
        """
        Navega até o módulo SisCop e realiza uma busca pelo protocolo fornecido.

        """
        try:
            siscop_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH,"//a[@href='/sigede/siscop' and contains(text(), 'SisCop - Web')]")))
            logger.info("Login validado: Painel do SIGEDE carregado com sucesso.")
        except Exception as e:
            logger.error(f"Falha de credenciais ou rede durante login do SIGEDE: {e}")
            raise
        
        try:
            logger.info("Navegando para o SisCop")

            # Clica no elemento SisCop
            siscop_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//a[@href='/sigede/siscop' and contains(text(), 'SisCop - Web')]",
                    )
                )
            )
            self._click(siscop_btn)
            time.sleep(3)

            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchkey"))
            )
            search_input.clear()
            search_input.send_keys(protocolo)
            logger.info("Protocolo informado: %s", protocolo)

            pesquisar_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@onclick='pesquisar();']")
                )
            )
            self._click(pesquisar_btn)
            logger.info("Pesquisa realizada com sucesso")

            time.sleep(5)
            return True

        except (TimeoutException, NoSuchElementException) as e:
            logger.error("Erro ao navegar no SisCop: %s", e)
            return False

    def verificar_tabela(self):
        """
        Verifica a tabela de resultados do SisCop.

        - Salva um print da tela chamado 'pesquisa_protocolo.png'.
        - Se não houver registros, encerra o fluxo.
        - Se houver, clica no elemento cuja coluna 'Situação' seja 'Não iniciado', 'Executando Siafim' ou 'Executando'.
        """
        try:
            logger.info("Verificando registros na tabela")

            panel = self.wait.until(EC.presence_of_element_located((By.ID, "generic")))

            # Salva screenshot
            screenshot_path = os.path.join(
                self.pasta_download, "pesquisa_protocolo.png"
            )
            self.driver.save_screenshot(screenshot_path)
            logger.info("Print da tela salvo.")

            # Procura a tabela dentro da div
            table = panel.find_element(By.TAG_NAME, "table")
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            if not rows:
                logger.info("Nenhum processo encontrado. Encerrando fluxo.")
                return []

            # Itera pelas linhas para encontrar valor desejada na coluna Situação
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 5:
                    continue

                situacao = cols[4].text.strip()
                if (
                    situacao == "Executando"
                    or situacao == "Executando Siafim"
                    or situacao == "Não Iniciado"
                ):
                    # Clica no link dentro da coluna Situação
                    link = cols[4].find_element(By.TAG_NAME, "a")
                    self._click(link)
                    time.sleep(5)
                    logger.info(
                        f"Processo com situação ({situacao}) encontrado e clicado"
                    )

                    self._download_inteiro_teor()
                    indices = self._captura_indices()
                    self._busca_por_indices(indices)

                    return indices

            logger.info("Nenhum registro com Situação 'Executando' encontrado.")
            return []

        except Exception as e:
            logger.error("Erro ao verificar a tabela: %s", e)
            return []

    def _download_inteiro_teor(self) -> Optional[str]:
        """
        Clica no botão 'Inteiro Teor' para disparar o download do PDF e aguarda sua conclusão.
        """
        try:
            logger.info("Iniciando download do Inteiro Teor")

            link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(),'Inteiro Teor')]")
                )
            )

            # Recupera o href para construir o nome do arquivo esperado
            href = link.get_attribute("href")
            nome_arquivo = os.path.basename(href) + ".pdf"
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            arquivos_anteriores = {}
            pasta = os.path.dirname(caminho_arquivo)
            try:
                arquivos_anteriores = {
                    f: os.path.getsize(os.path.join(pasta, f))
                    for f in os.listdir(pasta)
                }
            except FileNotFoundError:
                arquivos_anteriores = {}

            self._click(link)

            if self._esperar_download_concluir(caminho_arquivo, arquivos_anteriores):
                logger.info("Download concluído")
                return caminho_arquivo
            else:
                logger.warning(
                    "Download não foi concluído dentro do tempo limite: %s",
                    caminho_arquivo,
                )
                return None

        except Exception as e:
            logger.error("Erro ao tentar baixar o Inteiro Teor: %s", e)
            return None

    def _captura_indices(self):
        """
        Captura todos os índices cadastrais da aba 'Índice Cadastral' e retorna como lista de strings.
        """
        try:
            logger.info("Acessando aba 'Índice Cadastral'")

            # Clica na aba "Índice Cadastral"
            aba = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//a[@href='#indiceCadastral' and contains(text(),'Índice Cadastral')]",
                    )
                )
            )
            self._click(aba)
            time.sleep(1)

            # Localiza a tabela dentro da aba
            tab_panel = self.wait.until(
                EC.presence_of_element_located((By.ID, "indiceCadastral"))
            )
            table = tab_panel.find_element(By.TAG_NAME, "table")
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            indices = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    indice = cols[0].text.strip()
                    if indice:
                        indices.append(indice)

            logger.info("Índices capturados: %s", indices)
            return indices

        except Exception as e:
            logger.error("Erro ao capturar índices cadastrais: %s", e)
            return []

    def _busca_por_indices(self, indices):
        """
        Realiza pesquisa dos ICs vinculados ao protocolo.
        """
        try:

            for indice in indices:
                logger.info(
                    f"Buscando índice: {indice} no Sigede (Zona, Quadra e Lote)"
                )

                # Clica no elemento SisCop
                siscop_btn = self.wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//a[@href='/sigede/siscop' and contains(text(), 'SisCop - Web')]",
                        )
                    )
                )
                self._click(siscop_btn)
                logger.info("Acessando SisCop")

                time.sleep(3)

                indice = (
                    indice.strip().replace("-", "").replace(".", "").replace("/", "")
                )
                if len(indice) < 11:
                    raise ValueError(f"Índice inválido: {indice}")

                indice_formatado = indice[0:11]
                logger.info("Índice formatado para pesquisa: %s", indice_formatado)

                select_element = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "searchKeyType"))
                )

                logger.info("Selecionando opção 'Índice Cadastral' para pesquisa")
                for option in select_element.find_elements(By.TAG_NAME, "option"):
                    if option.text.strip() == "Índice Cadastral":
                        option.click()
                        break

                logger.info("Inserindo índice no campo de pesquisa")
                search_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "searchkey"))
                )
                search_input.clear()
                search_input.send_keys(indice_formatado)

                time.sleep(1)

                logger.info("Clicando no botão pesquisar")
                pesquisar_btn = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@onclick='pesquisar();']")
                    )
                )
                self._click(pesquisar_btn)

                time.sleep(2)

                screenshot_path = os.path.join(
                    self.pasta_download, f"pesquisa_indice_{indice}.png"
                )
                self.driver.save_screenshot(screenshot_path)
                logger.info("Print da tela salvo")

            return True

        except Exception as e:
            logger.error("Erro ao pesquisar índice cadastral: %s", e)
            return False
