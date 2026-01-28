from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional

import re
import os
import time



from utils import logger

class BotBase:
    """
    Classe pai de todos os bots de automação (Bot-Core).
    Fornece métodos robustos de interação (clique, espera, interact com fallback).
    Padroniza a inicialização do Driver.
    """

    def __init__(self, driver, timeout: int = 10):
        """
        Inicializa o bot com o driver e configura o WebDriverWait padrão.
        
        :param driver: Instância do Selenium WebDriver.
        :param timeout: Tempo padrão de espera explícita (em segundos).
        """
        self.driver = driver
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
                     f"Tempo de procura por {nome_log}: {tempo_gasto:.1f} segs")
        return None
    

    def _esperar_download_concluir(self, caminho_arquivo, timeout=120):
        """
        Espera até que o arquivo seja completamente baixado na pasta de destino.
        Funciona mesmo que o navegador use nomes temporários diferentes.
        """
        pasta = os.path.dirname(caminho_arquivo)
        nome_base = self._sanitize_filename(os.path.basename(caminho_arquivo))
        temporarios = (".crdownload", ".part", ".tmp")
        inicio = time.time()

        # Mapeia arquivos existentes e seus tamanhos
        try:
            arquivos_anteriores = {
                f: os.path.getsize(os.path.join(pasta, f)) for f in os.listdir(pasta)
            }
        except FileNotFoundError:
            arquivos_anteriores = {}

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
                # Detecta se é novo ou mudou de tamanho
                if (
                    sanitized == nome_base
                    or (f not in arquivos_anteriores)
                    or (arquivos_anteriores.get(f) != tamanho)
                ):
                    return True

            if time.time() - inicio > timeout:
                logger.warning("Timeout aguardando download: %s", caminho_arquivo)
                return False

            time.sleep(0.2)


    def _sanitize_filename(self, nome: str) -> str:
        """
        Remove caracteres inválidos em nomes de arquivos no Windows.
        Útil para renomear arquivos baixados baseados em títulos/índices.
        """
        # Remove < > : " / \ | ? *
        return re.sub(r'[<>:"/\\|?*]', "_", nome)