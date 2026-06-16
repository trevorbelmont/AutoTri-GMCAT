import sys
import os
import ctypes
import subprocess
from pathlib import Path
from typing import Union
from utils.logger import logger #

def get_persistent_dir() -> Path:
    """
    Define o diretório de dados persistentes (config.tri e credentials.tri) com Fallout:
    1. Tenta %APPDATA%/AutoTri (Prioridade)
    2. Se falhar (permissão/erro), cai para a pasta do Executável
    """ 

    appdata = Path(os.environ.get('APPDATA', '')) / "AutoTri" 
    try:
        appdata.mkdir(parents=True, exist_ok=True)
        
        # Teste de escrita para garantir resiliência
        test_file = appdata / ".permissao_teste"
        test_file.touch()
        test_file.unlink()
               
        logger.debug(f"[PASTAS] Persistência definida no AppData: {appdata}")
        return appdata

    except Exception as e:
        logger.warning(f"[PASTAS] Falha ao acessar AppData ({e}). Iniciando sistema de Fallout...")

        #Se executável, devolve a pasta do executável 
        if getattr(sys, "frozen", False):
            fallback_path = Path(sys.executable).resolve().parent
        #Se no modo dev (interpretador), a pasta do repositório
        else:
            fallback_path = Path(__file__).resolve().parent.parent.parent

        logger.debug(f"[PASTAS] Persistência definida no diretório de execução: {fallback_path}")
        return fallback_path

def set_hidden(path: Union[str, Path]):
    """Marca um arquivo como oculto no Windows, aceitando Path ou String."""
    try:
        path_str = str(path)
        
        if sys.platform.startswith("win"):
            # 0x02 é o atributo para 'Hidden' no Windows
            ctypes.windll.kernel32.SetFileAttributesW(path_str, 0x02)
            logger.debug(f"[PASTAS] Arquivo marcado como oculto: {path_str}")
    except Exception as e:
        logger.warning(f"[PASTAS] O sistema foi incapaz de tornar oculto o arquivo {path_str}: {e}")

def set_visible(path: Union[str, Path]):
    """Remove atributos especiais e torna o arquivo 'Normal' no Windows."""
    try:
        path_str = str(path)
        if sys.platform.startswith("win") and os.path.exists(path_str):
            # 0x80 é o atributo para 'Normal' (limpa o Hidden)
            ctypes.windll.kernel32.SetFileAttributesW(path_str, 0x80)
            logger.debug(f"[PASTAS] Atributos resetados para Normal: {path_str}")
    except Exception as e:
        logger.warning(f"[PASTAS] Falha ao remover ocultação de {path_str}: {e}")

def abrir_pasta(path):
    """Abre a pasta especificada no explorador de arquivos do sistema."""
    if sys.platform.startswith("win"):  # Windows
        os.startfile(path)
    elif sys.platform.startswith("darwin"):  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])


def criar_pasta_resultados() -> str:
    """Cria uma pasta de resultados com timestamp legível em português do Brasil.

    :return: A String, pasta_resultados, com o nome da pasta (ex: "Resultados - 08 de janeiro de 2026 13h58)
    """
    import locale
    from datetime import datetime

    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

    timestamp_legivel = datetime.now().strftime("Resultados - %d de %B de %Y %Hh%M")
    pasta_resultados = timestamp_legivel
    os.makedirs(pasta_resultados, exist_ok=True)

    return pasta_resultados


def resource_path(relative_path: str) -> str:
    """ Retorna o caminho absoluto para recursos (como ícones) (Dev vs PyInstaller) """
    try:
        # Modo PyInstaller: procura a pasta temporária MEIPASS
        base_path = sys._MEIPASS

    except Exception:
        # Se não achou a pasta MEIPASS, então está rodando no interpretador
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir)

    return os.path.join(base_path, relative_path)
