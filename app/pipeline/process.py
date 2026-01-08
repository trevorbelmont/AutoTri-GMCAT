from utils import logger
from core import gerar_relatorio
from .sistemas import Siatu
from .sistemas import Urbano
from .sistemas import Sisctm
from .sistemas import GoogleMaps
from .sistemas import Sigede

import os
from typing import Dict, List, Any


'''
==================================================================================================================================
Este módulo, app/pipeline/process.py, funciona como um sub-orquestrador do pipeline da automação. 
Aqui as classes de serviço definidas em app/pipiline/sistemas.py são instanciadas e utilizadas para executar a automação em uma sequência lógica.
Este módulo gerencia os caminhos de arquivos e pastas (checando a existência dos diretórios para previnir exceções) e aciona a geração do relatório da automação.
==================================================================================================================================
'''


def processar_protocolo(protocolo: str, credenciais: Dict[str, str], pasta_resultados: str) -> List[str]:
    """
    Execução do módulo SIGEDE (Protocolos). Captura de ICs no protocolo e cria a pasta do protocolo.
    A lista de índices retornada nessa função será utiliza nas próximas etapas da automação.

    :param protocolo: Número do protocolo a ser processado.
    :param credenciais: Dicionário contendo as credenciais de acesso.
    :param pasta_resultados: Caminho para a pasta raiz dos resultados.
    :return: Lista de índices cadastrais (IC) vinculados ao protocolo.
    """
   
    pasta_protocolo = os.path.join(pasta_resultados, protocolo)
    os.makedirs(pasta_protocolo, exist_ok=True)

    indices: List[str] = Sigede().executar(protocolo, credenciais, pasta_protocolo)
    return indices      # Retorna Lista de Índices Cadastrais (IC) a serem processados


def processar_indice(indice: str, credenciais: Dict[str, str], protocolo: str, pasta_resultados: str) -> None:
    """
    Execução dos módulos SIATU, URBANO e SISCTM para UM ÚNICO índice especificado, Gera relatório e Cria a pasta do IC.
    
    :param indice: Índice cadastral (IC) a ser processado.
    :param credenciais: Dicionário contendo as credenciais de acesso.
    :param protocolo: Número do protocolo pai.
    :param pasta_resultados: Caminho para a pasta raiz dos resultados.
    :return: None
    """

    # Definição do caminho e criação da pasta 
    pasta_indice = os.path.join(pasta_resultados, protocolo, indice)
    os.makedirs(pasta_indice, exist_ok=True) # exist_ok= True : garante que, se necessário, os diretórios parent sejam criados.
    # Essa é uma linha robusta que altera o comportamento do método os.makedirs(____, exist_ok=True) para não lançar exceção e parar a automação
    #caso a pasta em questão não exista. Esse parâmetro garante que, caso não exista, ela seja criada no caminho especificado.

    # Executa a automação dos Bots Siatu, Urbano,Sisctm e GoogleMaps (via classes de serviços- os adapters dos "bot-core")
    # Instancia variáveis e exectua Siatu
    dados_pb: Dict[str, Any]
    anexos_count: int
    (dados_pb, anexos_count) = Siatu().executar(indice, credenciais, pasta_indice)

    # Instancia variáveis e executa Urbano.executar(...)
    dados_projeto: Dict[str, Any]
    projetos_count: int
    (dados_projeto, projetos_count) = Urbano().executar(indice, credenciais, pasta_indice)

    # Executa Sisctm
    dados_sisctm: Dict[str, Any] = Sisctm().executar(indice, credenciais, pasta_indice)

    # Executa GoogleMaps (não retorna valor)
    GoogleMaps().executar(indice, dados_sisctm, dados_pb, pasta_indice)

    pdf_path = os.path.join(pasta_indice, f"1. Relatório de Triagem - {indice}.pdf")
    gerar_relatorio(
        indice_cadastral=indice,
        anexos_count=anexos_count,
        projetos_count=projetos_count,
        pasta_anexos=pasta_indice,
        prps_trabalhador=credenciais["usuario"], # identifica o trabalhador sem passar credenciais críticas (senhas)
        nome_pdf=pdf_path,
        dados_planta=dados_pb,
        dados_projeto=dados_projeto,
        dados_sisctm=dados_sisctm,
    )
    logger.info(f"Relatório gerad\n\n")
