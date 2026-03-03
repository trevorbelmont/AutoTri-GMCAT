import sys
from pathlib import Path
import queue                    
import logging
import os

# Detecta se está rodando via PyInstaller, pra salvar os "Detalhes da Triagem"
if getattr(sys, "frozen", False):
    ROOT = Path.cwd()
else:
    ROOT = Path(__file__).parent.parent.parent


LOG_FILE = "Detalhes da Última Triagem.txt"

log_path = ROOT / LOG_FILE
log_path.parent.mkdir(parents=True, exist_ok=True)


log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """Envia registros de log para uma fila thread-safe."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
        except Exception:
            self.handleError(record)


def lot_logger_config(pasta_resultados:str, activate_extra_log: bool):
    """
    Adiciona um handler extra ao logger se activate_extra_log for True.
    Este handler extra filtra apenas mensagens de nível WARNING ou superior.
    """
    from utils import settings
    if settings.LOT_DEBUGGER:
        log_lote_path = os.path.join(pasta_resultados, "Log de Erros.txt")
        
        
        lote_handler = logging.FileHandler(log_lote_path, mode="w", encoding="utf-8")
        lote_handler.setLevel(logging.WARNING)
        lote_handler.setFormatter(lot_formatter)
        
        # Adicionamos ao logger principal (triagem_logger)
        logger.addHandler(lote_handler)
        logger.debug(f"[LOGGER] Handler de Lote ativado em: {log_lote_path}")


def reset_log_file():
    """
    Força a limpeza do arquivo de log para iniciar uma nova triagem limpa.
    Chamado no início de cada processamento para não levar detalhes de triagem anteriores para a triagem atual
    """
    global file_handler 

    file_handler.close()
    logger.removeHandler(file_handler)
    
    new_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    new_handler.setFormatter(file_formatter)
    
    logger.addHandler(new_handler)
    file_handler = new_handler


def section_log(titulo: str, separador: str = "-", largura: int = 50, addEndLines: int = 0,level=logging.INFO):
    """
    Gera uma linha de log centralizada e destacada com Título.
    Ex: ----------- < SIATU : 31.00337504/2025-03 > -----------

    :param: titulo: (str) A mensagem a ser exibida no centro (entre os separadores)
    :param: separador: (str) o caractére usado como separador (por padrão é '-' mas pode ser ' ', espaço em branco tb) 
    :param: largura: (int) a largura da linha da mensagem
    :param: addEndLines: (int) número de quebras de linhas adicionais ao final do section_log

    """
    mensagem = f" {titulo} "
    linha_formatada = mensagem.center(largura, separador)
    linha_formatada += "\n" * addEndLines

    logger.log(level,linha_formatada)


console_formatter = logging.Formatter("%(levelname)s: %(message)s")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
lot_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M")

# Handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_handler.setFormatter(file_formatter)

queue_handler = QueueHandler()
queue_handler.setFormatter(console_formatter)

''' DEFINE O OBJETO LOGGER - utilizando logging.getlogger (do python)'''
logger = logging.getLogger("triagem_logger")
logger.setLevel(logging.INFO) 
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(queue_handler)