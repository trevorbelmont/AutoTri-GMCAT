''' Baseado no script "pega_poligono.py" de Daniel Kenji Matsumoto Viana disponível em: 
https://drive.google.com/drive/folders/1YX6RQn7t68uCbcy7dZSGDFhNVjcOxC8H '''


import re
import os
from typing import Optional
from curl_cffi import requests

from .base import BotBase
from utils import logger

class PoligonoAuto(BotBase):
    """
    Bot-Core especializado em capturar polígonos de lotes via serviço WFS.
    Não utiliza Selenium Webdriver, mas requisições HTTP diretas..
    """

    def __init__(self, pasta_download: str):
        """
        Inicializa o robô de polígonos.
        """

        # Este robô não usa WebDriver
        super().__init__(driver=None)
        self.pasta_download = pasta_download

    def capturar_kml(self, indice: str) -> bool:
        """
        Realiza a requisição ao servidor de geoprocessamento e salva o arquivo KML.
        
        :param indice: Índice Cadastral (IC) formatado.
        :return: True se o arquivo foi salvo com sucesso, False caso contrário.
        """
        clean_id = indice.strip()
        
        # Prepara nomes seguros para URL e para o Arquivo
        safe_id_url = clean_id.replace(" ", "%20")
        safe_id_file = self._sanitize_filename(clean_id.replace(" ", "_"))
        
        filename = f"poligono_{safe_id_file}.kml"
        caminho_final = os.path.join(self.pasta_download, filename)
        
        url = (
            "https://geoservicos.pbh.gov.br/geoserver/ide_bhgeo/wfs?"
            "service=WFS&version=1.0.0&request=GetFeature"
            "&typeName=ide_bhgeo:CADASTRO_IMOBILIARIO"
            "&outputFormat=application/vnd.google-earth.kml+xml"
            f"&CQL_FILTER=INDICE_CADASTRAL='{safe_id_url}'"
        )

        logger.info(f"Solicitando polígono via WFS para o IC: {clean_id}...")

        try:
            # impersonate="chrome110" simula o cabeçalho de um navegador real para evitar erro 403
            response = requests.get(url, impersonate="chrome110", verify=False, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Validação: Verifica se o retorno contém coordenadas válidas
                if "coordinates" not in content:
                    logger.warning(f"Polígono não encontrado para o IC {clean_id} (Servidor retornou mapa vazio).")
                    return False

                # Injeção de Estilo: Define a cor vermelha e transparência para o polígono
                red_style = (
                    '<Style>'
                    '<LineStyle><color>ff0000ff</color><width>5</width></LineStyle>'
                    '<PolyStyle><fill>0</fill></PolyStyle>'
                    '</Style>'
                )
                
                # Insere o estilo logo após a tag Placemark de forma robusta
                content = re.sub(r'(<[\w:]*Placemark[^>]*>)', r'\1' + red_style, content)

                # Escrita do arquivo no diretório de triagem do IC
                with open(caminho_final, "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info(f"Polígono KML salvo com sucesso: {filename}")
                return True
                
            else:
                logger.error(f"Erro {response.status_code} ao acessar GeoServicos: Acesso negado ou servidor offline.")
                return False

        except Exception as e:
            logger.error(f"Falha crítica ao capturar polígono: {e}")
            return False