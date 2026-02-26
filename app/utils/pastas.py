import sys
import os
import subprocess


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

    # Define a localidade para português do Brasil
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

    # Timestamp legível para a pasta resultados
    timestamp_legivel = datetime.now().strftime("Resultados - %d de %B de %Y %Hh%M")
    pasta_resultados = timestamp_legivel
    os.makedirs(pasta_resultados, exist_ok=True)

    return pasta_resultados


def resource_path(relative_path: str) -> str:
    """ Retorna o caminho absoluto para recursos (como ícones) (Dev vs PyInstaller) """
    try:
        # Modo PyInstaller: procura a pasta temporária MEIPASS
        base_path = sys._MEIPASS

    except Exception: # Se não achou a pasta MEIPASS, então está rodando no interpretador

        # Modo Desenvolvimento (Baseado na localização do módulo atual, interface.py)
        # O arquivo interface.py está em: .../app/gui/
        # O ícone está em:                .../app/
        
        # Pega a pasta atual do arquivo (app/gui)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Sobe um nível para chegar em 'app/' (onde o ícone deve estar)
        base_path = os.path.dirname(current_dir)

    return os.path.join(base_path, relative_path)

