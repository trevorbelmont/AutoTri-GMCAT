import argparse
import sys, os
import json
from pathlib import Path
import logging
from tkinter.messagebox import RETRY
from .logger import logger, section_log
from .logger import ROOT 
from utils.pastas import get_persistent_dir


DATA_DIR = get_persistent_dir()
CONFIG_FILE = DATA_DIR / "config.tri"

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

    parser.add_argument("--debug", "-d", "-dbg", action="store_true", default=None)
    parser.add_argument("--not-headless", "--show-browser", "-sb", action="store_true", default=None)
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--timeout-download", type=float, default=None)
    parser.add_argument("--retry", type=int, dest="retry", default=None)
    parser.add_argument("--retry-delay", type=float, dest="retry_delay", default=None)
    parser.add_argument("--lot-debugger", "-ltdbg", action="store_true", default=None)

    parser.add_argument("--setSigedeCreds", type=str, dest="_sigede_creds_raw", help=argparse.SUPPRESS)
    parser.add_argument("--setSiatuCreds", type=str, dest="_siatu_creds_raw", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.debug is not None: DEBUG = args.debug
    if args.timeout is not None: TIMEOUT_ESPERA = args.timeout
    if args.timeout_download is not None: TIMEOUT_DOWNLOAD = args.timeout_download
    if args.retry is not None: RETRY_MAX = args.retry
    if args.retry_delay is not None: RETRY_DELAY = args.retry_delay
    if args.not_headless is not None: NOT_HEADLESS = args.not_headless
    if args.lot_debugger is not None: LOT_DEBUGGER = args.lot_debugger

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
                 f"       TIMEOUT={TIMEOUT_ESPERA}s, TIMEOUT_DOWNLOAD={TIMEOUT_DOWNLOAD}s,\n"
                 f"       RETRY_MAX ={RETRY_MAX}, RETRY_DELAY={RETRY_DELAY}, LOT_DEBUGGER={LOT_DEBUGGER},\n"
                 f"       DATA_DIR= {DATA_DIR}\n")

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