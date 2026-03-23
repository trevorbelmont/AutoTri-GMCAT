import argparse
import sys, os
import json
from pathlib import Path
import logging
from tkinter.messagebox import RETRY
from .logger import logger, section_log
from .logger import ROOT 

CONFIG_FILE = ROOT / "config.json"

# Valores pré settados de variáveis "globais":
DEBUG = False 
TIMEOUT_ESPERA = 10.0 
TIMEOUT_DOWNLOAD = 120.0
NOT_HEADLESS = False
RETRY_MAX = 2
RETRY_DELAY = 10.0
LOT_DEBUGGER = False
_ARG_CREDS = {}


def load_config():
    """Carrega as configurações do JSON de config silenciosamente."""
    global DEBUG, TIMEOUT_ESPERA, TIMEOUT_DOWNLOAD, RETRY_MAX, RETRY_DELAY, NOT_HEADLESS, LOT_DEBUGGER
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                DEBUG = data.get("DEBUG", DEBUG)
                TIMEOUT_ESPERA = data.get("TIMEOUT_ESPERA", TIMEOUT_ESPERA)
                TIMEOUT_DOWNLOAD = data.get("TIMEOUT_DOWNLOAD", TIMEOUT_DOWNLOAD)
                RETRY_MAX = data.get("RETRY_MAX", RETRY_MAX)
                RETRY_DELAY = data.get("RETRY_DELAY", RETRY_DELAY)
                NOT_HEADLESS = data.get("NOT_HEADLESS", NOT_HEADLESS)
                LOT_DEBUGGER = data.get("LOT_DEBUGGER", LOT_DEBUGGER)
            logger.info("[SETTINGS] Preferências de configuração carregadas do arquivo config.json!")
        except Exception as e:
            logger.error(f"Falha ao ler config.json: {e}")

def save_config():
    """ Salva o estado atual das variáveis no config.json."""
    data = {
        "DEBUG": DEBUG,
        "TIMEOUT_ESPERA": TIMEOUT_ESPERA,
        "TIMEOUT_DOWNLOAD": TIMEOUT_DOWNLOAD,
        "RETRY_MAX": RETRY_MAX,
        "RETRY_DELAY": RETRY_DELAY,
        "NOT_HEADLESS": NOT_HEADLESS,
        "LOT_DEBUGGER": LOT_DEBUGGER
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("[SETTINGS] Preferências salvas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao salvar config.json: {e}")

def reset_to_defaults():
    """Remove o arquivo de configuração personalizada."""
    if CONFIG_FILE.exists():
        os.remove(CONFIG_FILE)
        logger.info("[SETTINGS] Configurações resetadas para o padrão de fábrica.")



def setup():
    """
    Lê os argumentos passados via linha de comando (ou atalho do Windows)
    e atualiza as variáveis globais deste módulo (que é importado em múltiplos outros módulos).
    """
    global DEBUG, TIMEOUT_ESPERA, TIMEOUT_DOWNLOAD, RETRY_MAX, RETRY_DELAY
    global _ARG_CREDS, NOT_HEADLESS, LOT_DEBUGGER
    
    load_config()

    parser = argparse.ArgumentParser(description="AutoTri - Configurações de Execução")

    parser.add_argument(
        "--debug", "-d", "-dbg",
        default=DEBUG, 
        action="store_true", 
        help="Ativa modo de depuração (Logs verbosos nas etapas)."
    )

    parser.add_argument(
        "--not-headless", "--show-browser","-sb","-nhdls",
        default=NOT_HEADLESS, 
        action="store_true", 
        help="Ativa modo de exibição do navegador (roda em primeiro plano) para depuração visual de erros de navegação."
    )

    parser.add_argument(
        "--timeout", 
        type=float, 
        default=TIMEOUT_ESPERA, 
        help="Tempo limite padrão (em segundos) para esperar elementos na tela durante os carregamentos das páginas."
    )
    
    parser.add_argument(
        "--timeout-download", "--timeout-longo", 
        type=float, 
        default=TIMEOUT_DOWNLOAD, 
        help="Tempo limite longo (em segundos) para downloads e processamentos pesados."
    )
    parser.add_argument(
        "--retry", "--retries", 
        type=int,
        dest="retry", 
        default=RETRY_MAX, 
        help="Define o número máximo de retries (tentativas) do decorador @retry - usado no Siatu."
    )
    parser.add_argument(
        "--retry-delay", "--delay", 
        type=float,
        dest="retry_delay", 
        default=RETRY_DELAY, 
        help="Define o tempo de espera (delay) em segundos entre as retries do decorador @retry - usado no Siatu."
    )

    parser.add_argument(
        "--lot-debugger", "-ltdbg",
        action="store_true",
        default=LOT_DEBUGGER,
        help="Gera um arquivo secundário ('Log de Erros.txt') apenas com falhas críticas da última triagem."
    )

    parser.add_argument("--setSigedeCreds", "--setSigedeCred", "-sSgdCs",type=str,dest="_sigede_creds_raw",help=argparse.SUPPRESS)
    parser.add_argument("--setSiatuCreds",  "--setSiatuCred", "-sStuCs",type=str,dest="_siatu_creds_raw",help=argparse.SUPPRESS)

    args = parser.parse_args()

    DEBUG = args.debug
    TIMEOUT_ESPERA = args.timeout
    TIMEOUT_DOWNLOAD = args.timeout_download
    RETRY_MAX = args.retry
    RETRY_DELAY = args.retry_delay
    NOT_HEADLESS = args.not_headless
    LOT_DEBUGGER = args.lot_debugger
    _ARG_CREDS.update({
        "sigede_creds_raw": args._sigede_creds_raw,
        "siatu_creds_raw": args._siatu_creds_raw,
    })



    if DEBUG:
        logger.setLevel(logging.DEBUG)
        section_log(f"MODO DEBUG ATIVADO",':',60,1)
        logger.debug(f"Nível mínimo de Log alterado para DEBUG.")
    else:
        logger.setLevel(logging.INFO)

    logger.debug(f"[SETTINGS] Configuração Carregada:\n       DEBUG={DEBUG}, NOT_HEADLESS={NOT_HEADLESS},\n"
                 f"       TIMEOUT={TIMEOUT_ESPERA}s, TIMEOUT_DOWNLOAD={TIMEOUT_DOWNLOAD}s\n"
                 f"       RETRY_MAX ={RETRY_MAX}, RETRY_DELAY={RETRY_DELAY}, LOT_DEBUGGER={LOT_DEBUGGER}"
                 )

def _get_cli_credentials():
    return _ARG_CREDS

def limpar_memoria_credenciais():
    """
    Remove as credenciais da memória global do módulo (singleton) settings.py.
    """
    global _ARG_CREDS
    tem_conteudo = any(valor.strip() for valor in _ARG_CREDS.values() if valor)
    _ARG_CREDS.clear()
    if(tem_conteudo):
        logger.debug("[SETTINGS] Memória de credenciais limpa neste módulo.")