import argparse
import sys

import logging                              # Importa o módulo de LOGGING padrão do python
from .logger import logger, section_log     # Importa o nosso wrapper de LOGS

# Valores pré settados de variáveis "globais":
DEBUG = False               # Se True: Logs mais detalhados, navegador não fecha em erro, etc.
TIMEOUT_ESPERA = 10.0         # Tempo padrão para esperar elementos na tela (WebDriverWait)
TIMEOUT_DOWNLOAD = 120.0        # Tempo para downloads pesados ou processamentos demorados (RemoteConnection)
NOT_HEADLESS = False        # Se True: Exibe o navegador (roda em primeiro plano)
_ARG_CREDS = {}

def setup():
    """
    Lê os argumentos passados via linha de comando (ou atalho do Windows)
    e atualiza as variáveis globais deste módulo (que é importado em múltiplos outros módulos).
    """
    global DEBUG, TIMEOUT_ESPERA, TIMEOUT_DOWNLOAD, NOT_HEADLESS
    global _ARG_CREDS
    

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
        type=float, 
        default=10.0, 
        help="Tempo limite padrão (em segundos) para esperar elementos na tela durante os carregamentos das páginas."
    )
    
    # Argumento --timeout-longo (Número Inteiro. Padrão 120)
    parser.add_argument(
        "--timeout-download", "--timeout-longo", 
        type=float, 
        default=120.0, 
        help="Tempo limite longo (em segundos) para downloads e processamentos pesados."
    )

    # Parser de credencias cruas: exemplo  --setSigedeCred "usuario_siged::senha_sigede"
    parser.add_argument("--setSigedeCreds", "--setSigedeCred", "-sSgdCs",type=str,dest="_sigede_creds_raw",help=argparse.SUPPRESS)
    parser.add_argument("--setSiatuCreds",  "--setSiatuCred", "-sStuCs",type=str,dest="_siatu_creds_raw",help=argparse.SUPPRESS)

    # Parseia os argumentos
    args = parser.parse_args()

    # Atualiza as variáveis globais com o que veio do argumento
    DEBUG = args.debug
    TIMEOUT_ESPERA = args.timeout
    TIMEOUT_DOWNLOAD = args.timeout_download
    NOT_HEADLESS = args.not_headless
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

    # Feedback no terminal (útil para debug visual ao iniciar)
    logger.debug(f"[SETTINGS] Configuração Carregada:\n       DEBUG={DEBUG},NOT_HEADLESS={NOT_HEADLESS},\n       TIMEOUT={TIMEOUT_ESPERA}s, TIMEOUT_DOWNLOAD={TIMEOUT_DOWNLOAD}s")

# Getter para o CredentialManager acessar os args brutos de forma encapsulada
def _get_cli_credentials():
    return _ARG_CREDS

def limpar_memoria_credenciais():
    """
    Remove as credenciais da memória global do módulo (singleton) settings.py.
    """
    global _ARG_CREDS
    # Em Python, .clear() em dicionário remove o conteúdo mantendo o objeto.
    # É melhor do que 'del _ARG_CREDS' pois não quebra referências de outros lugares, mas esvazia o conteúdo sensível.
    tem_conteudo = any(valor.strip() for valor in _ARG_CREDS.values() if valor)
    _ARG_CREDS.clear()
    if(tem_conteudo):
        logger.debug("[SETTINGS] Memória de credenciais limpa neste módulo.")