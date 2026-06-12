import os
import sys

#===============================================================================
#           ESTE MÓDULO DEVE SER EXECUTADO DIRETAMENTE
#      O MÓDULO DEVE SER COLOCADO NA PASTA APP PARA FUNCIONAR
#===============================================================================



# Garante que o Python enxergue a pasta 'app' e seus submódulos
caminho_app = os.path.join(os.getcwd(), "app")
sys.path.append(caminho_app)

from utils import settings
from pipeline.sistemas import GoogleMaps 

def rodar_teste_google_maps():
    # True = Mostra o navegador | False = Esconde
    settings.NOT_HEADLESS = False 
    settings.TIMEOUT_ESPERA = 10.0
    
    indice = "374300 004 0049"
    
    # Dados extraídos da triagem real (para injetar no Maps)
    dados_pb = {
        'endereco_imovel': 'RUA HENRIQUE CABRAL, 738 - APT 201 - SAO LUIZ - 31270-760 - BELO HORIZONTE - MG', 
    }

    dados_sisctm = {
        'endereco_ctmgeo': 'RUA HENRIQUE CABRAL, 738 - Belo Horizonte - MG, 31270760', 
    }

    # Cria uma pasta temporária só para teste
    pasta_teste = os.path.join(os.getcwd(), f"Teste_Google_Maps_{indice.replace(' ', '_')}")
    os.makedirs(pasta_teste, exist_ok=True)

    print(f"\n[+] Iniciando Automação Sintética do Google Maps para o IC: {indice}")
    print(f"[+] Modo Visual: ATIVADO (O Chrome vai abrir)")
    
    try:
        GoogleMaps().executar(indice, dados_sisctm, dados_pb, pasta_teste)
        print(f"\n[+] Teste Finalizado! Verifique a pasta: {pasta_teste}")
    except Exception as e:
        print(f"\n[-] Erro durante a execução sintética: {e}")

if __name__ == "__main__":
    rodar_teste_google_maps()