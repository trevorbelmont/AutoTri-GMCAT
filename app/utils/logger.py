import sys
from pathlib import Path
import queue                    
import logging

# Detecta se está rodando via PyInstaller, pra salvar os "Detalhes da Triagem"
if getattr(sys, "frozen", False):
    ROOT = Path.cwd()       # pasta do PyInstaller
else:                       # Se não é executável, salva relativamente na raíz (onde está a venv)
    ROOT = Path(__file__).parent.parent.parent


# NOTE: Este arquivo é substituído a cada nova triagem
LOG_FILE = "Detalhes da Última Triagem.txt"

# Cria pasta do log se não existir
log_path = ROOT / LOG_FILE
log_path.parent.mkdir(parents=True, exist_ok=True)


# Fila com as novas mensagens do log à serem adicionadas ao logger (e que a interface "escuta")
log_queue = queue.Queue()

# Definimos uma classe QueueHandler para manusear nossa fila
class QueueHandler(logging.Handler):
    """Envia registros de log para uma fila thread-safe."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
        except Exception:
            self.handleError(record)




# Limpa o arquivo de Detalhes da Última Triagem.xt
def reset_log_file():
    """
    Força a limpeza do arquivo de log para iniciar uma nova triagem limpa.
    Chamado no início de cada processamento para não levar detalhes de triagem anteriores para a triagem atual
    """
    # 'global' avisa o python que não é uma variável nova, mas uma referência à variável global pre existente
    global file_handler 

    # Fecha o handler atual para liberar o arquivo
    file_handler.close()
    logger.removeHandler(file_handler)
    
    # Reabre o arquivo em modo 'w' (write), o que trunca (limpa) o conteúdo
    new_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    new_handler.setFormatter(file_formatter)
    
    # Reconecta o handler ao logger
    logger.addHandler(new_handler)
    
    # Atualiza a referência global da variável file_handler
    file_handler = new_handler


# Define uma função para gerar separadores de seção
def section_log(titulo: str, separador: str = "-", largura: int = 50, addEndLines: int = 0):
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

    logger.info(linha_formatada)


# Formatter para o console e GUI (limpo, sem milissegundos)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")

# Formatter para o arquivo (com timestamp completo)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_handler.setFormatter(file_formatter)

# Handler da Fila (Usamos o formato do console para ficar limpo na tela)
queue_handler = QueueHandler()
queue_handler.setFormatter(console_formatter)

''' DEFINE O OBJETO LOGGER - utilizando logging.getlogger (do python)'''
# Logger central - pode ser alterado posteriormente na main usando setting.setup()
logger = logging.getLogger("triagem_logger")
logger.setLevel(logging.INFO) 
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(queue_handler) # Adicionamos a GUI como um destino também.