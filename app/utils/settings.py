import argparse
import sys

import logging                  # Importa o módulo de LOGGING padrão do python
from .logger import logger      # Importa o nosso wrapper de LOGS

# Valores pré settados de variáveis "globais":
DEBUG = False               # Se True: Logs mais detalhados, navegador não fecha em erro, etc.
TIMEOUT_ESPERA = 10         # Tempo padrão para esperar elementos na tela (WebDriverWait)
TIMEOUT_LONGO = 120         # Tempo para downloads pesados ou processamentos demorados (RemoteConnection)
NOT_HEADLESS = False        # Se True: Exibe o navegador (roda em primeiro plano)

def setup():
    """
    Lê os argumentos passados via linha de comando (ou atalho do Windows)
    e atualiza as variáveis globais deste módulo (que é importado em múltiplos outros módulos).
    """
    global DEBUG, TIMEOUT_ESPERA, TIMEOUT_LONGO, NOT_HEADLESS

    parser = argparse.ArgumentParser(description="Automação de Triagem - Configurações de Execução")

    # Argumento --debug (Flag booleana. Se presente, vira True. Se ausente, False)
    parser.add_argument(
        "--debug", "-d", "-dbg", 
        action="store_true", 
        help="Ativa modo de depuração (Logs verbosos nas etapas)."
    )

    # Argumento --not-headless (Flag booleana. Se presente, vira True. Se ausente, False)
    parser.add_argument(
        "--not-headless", "--show-browser","-sb","-nhdls", 
        action="store_true", 
        help="Ativa modo de exibição do navegador (roda em primeiro plano) para depuração visual de erros de navegação."
    )

    # Argumento --timeout (Número Inteiro. Padrão 10)
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=10, 
        help="Tempo limite padrão (em segundos) para esperar elementos na tela durante os carregamentos das páginas."
    )
    
    # Argumento --timeout-longo (Número Inteiro. Padrão 120)
    parser.add_argument(
        "--timeout-longo", 
        type=int, 
        default=120, 
        help="Tempo limite longo (em segundos) para downloads e processamentos pesados."
    )

    # Parseia os argumentos
    args = parser.parse_args()

    # Atualiza as variáveis globais com o que veio do argumento
    DEBUG = args.debug
    TIMEOUT_ESPERA = args.timeout
    TIMEOUT_LONGO = args.timeout_longo
    NOT_HEADLESS = args.not_headless

    if DEBUG:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"::: MODO DEBUG ATIVADO ::: \nNível mínimo de Log alterado para DEBUG.")
    else:
        logger.setLevel(logging.INFO)

    # Feedback no terminal (útil para debug visual ao iniciar)
    logger.debug(f"[SETTINGS] Configuração Carregada: DEBUG={DEBUG}, NOT_HEADLESS={NOT_HEADLESS} TIMEOUT_ESPERA={TIMEOUT_ESPERA}s, TIMEOUT_LONGO={TIMEOUT_LONGO}s")