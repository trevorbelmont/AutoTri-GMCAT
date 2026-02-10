from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional

from utils import settings

import re
import os
import time


from utils import logger


class BotBase:
    """
    Classe base dos bots do bot-core.
    Centraliza métodos comuns (clique, espera, interact com fallback)
    e padroniza a inicialização do Driver e tempos de espera.
    """

    def __init__(self, driver: WebDriver, timeout: Optional[float] = None):
        """
        Inicializa o bot com o driver e configura o WebDriverWait padrão.

        :param driver: Instância do Selenium WebDriver.
        :param timeout: Tempo padrão de espera explícita (em segundos).
        """

        if timeout is None:
            self.timeout = settings.TIMEOUT_ESPERA
        else:
            self.timeout = timeout

        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=self.timeout)

    def _click(self, element):
        """Click padrão: tenta clicar diretamente, se falhar usa JavaScript."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def _interact(
        self,
        nome_log: str,
        timeout_tentativa: float = 2.0,
        clicar: bool = True,
        **seletores: str,
    ) -> Optional[WebElement]:
        """Um click ou element finder mais robusto com lógica de fallback em várias etpas implementada.
        Localiza um elemento usando estratégias de fallback baseadas nos argumentos passados e na ordem que são passados.
        Retorna o WebElement encontrado para uso posterior, caso necessário."""

        # Define os tipo de métodos de procura válidos (tags do código fonte)
        mapa_by = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "class_name": By.CLASS_NAME,
            "tag": By.TAG_NAME,
        }

        tempo_gasto = 0

        # Itera sobre os argumentos passados (kwargs preserva ordem no Python 3.7+)
        for estrategia, valor_seletor in seletores.items():
            if estrategia not in mapa_by:
                continue

            by_type = mapa_by[estrategia]

            try:
                elemento = WebDriverWait(self.driver, timeout_tentativa).until(
                    EC.element_to_be_clickable((by_type, valor_seletor))
                )

                tempo_gasto += timeout_tentativa
                logger.info(
                    f"{nome_log} encontrado via '{estrategia}' em menos de {tempo_gasto:.1f} segs de busca."
                )

                if clicar:
                    self._click(elemento)

                return elemento

            except Exception:
                tempo_gasto += timeout_tentativa
                continue

        logger.error(
            f"ERRO: {nome_log} não encontrado após todas as {len(seletores)} tentativas.\n"
            f"Tempo de procura por {nome_log}: {tempo_gasto:.1f} segs"
        )
        return None

    def _esperar_download_concluir(
        self,
        caminho_arquivo,
        arquivos_anteriores,
        timeout_download: Optional[float] = None,
    ):
        """
        Espera até que o arquivo seja completamente baixado na pasta de destino.
        Funciona mesmo que o navegador use nomes temporários diferentes.
        """

        time_limit = (
            settings.TIMEOUT_DOWNLOAD if timeout_download is None else timeout_download
        )

        pasta = os.path.dirname(caminho_arquivo)
        nome_base = self._sanitize_filename(os.path.basename(caminho_arquivo))
        temporarios = (".crdownload", ".part", ".tmp")
        inicio = time.time()

        while True:

            try:
                arquivos_atuais = {
                    f: os.path.getsize(os.path.join(pasta, f))
                    for f in os.listdir(pasta)
                }
            except FileNotFoundError:
                arquivos_atuais = {}

            for f, tamanho in arquivos_atuais.items():
                if f.endswith(temporarios):
                    continue
                sanitized = self._sanitize_filename(f)

                if (
                    sanitized == nome_base
                    or (f not in arquivos_anteriores)
                    or (arquivos_anteriores.get(f) != tamanho)
                ):
                    return True

            if time.time() - inicio > time_limit:
                logger.warning(
                    "Timeout aguardando download: %s por %f segundos", caminho_arquivo
                )
                return False

            time.sleep(0.2)

    def _sanitize_filename(self, nome: str) -> str:
        """
        Remove caracteres inválidos em nomes de arquivos no Windows.
        """
        return re.sub(r'[<>:"/\\|?*]', "_", nome)
