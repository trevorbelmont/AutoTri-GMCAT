from utils import logger
from core import gerar_relatorio
from .sistemas import Siatu
from .sistemas import Urbano
from .sistemas import Sisctm
from .sistemas import GoogleMaps
from .sistemas import Sigede

import os


'''
==================================================================================================================================
Este módulo, app/pipeline/process.py, funciona como um sub-orquestrador do pipeline da automação. 
Aqui as classes de serviço definidas em app/pipiline/sistemas.py são instanciadas e utilizadas para executar a automação em uma sequência lógica.
Este módulo gerencia os caminhos de arquivos e pastas (checando a existência dos diretórios para previnir exceções) e aciona a geração do relatório da automação.
==================================================================================================================================
'''


def processar_protocolo(protocolo, credenciais, pasta_resultados):
    """
    Execução do módulo SIGEDE (Protocolos) - O passo inicial da automação.
    Captura indices cadastrais vinculados ao protocolo;
    Criação da pasta protocolo.
    A lista de índice retornada nessa função será utiliza nas próximas etapas da automação.
    """
    pasta_protocolo = os.path.join(pasta_resultados, protocolo)
    os.makedirs(pasta_protocolo, exist_ok=True)

    indices = Sigede().executar(protocolo, credenciais, pasta_protocolo)
    return indices      # Retorna Lista de Índices Cadastrais (IC) a serem processados


def processar_indice(indice, credenciais, protocolo, pasta_resultados):
    """
    Execução dos módulos SIATU, URBANO e SISCTM para UM ÚNICO índice especificado.
    Gera relatório;
    Criação da pasta IC.
    """

    # Definição do caminho e criação da pasta 
    pasta_indice = os.path.join(pasta_resultados, protocolo, indice)
    os.makedirs(pasta_indice, exist_ok=True) # exist_ok= True : garante que, se necessário, os diretórios parent sejam criados.
    # Essa é uma linha robusta que altera o comportamento do método os.makedirs(____, exist_ok=True) para não lançar exceção e parar a automação
    #caso a pasta em questão não exista. Esse parâmetro garante que, caso não exista, ela seja criada no caminho especificado.

    # Executa a automação dos Bots Siatu, Urbano,Sisctm e GoogleMaps (via classes de serviços- os adapters dos "bot-core")
    dados_pb, anexos_count = Siatu().executar(indice, credenciais, pasta_indice)
    dados_projeto, projetos_count = Urbano().executar(indice, credenciais, pasta_indice)
    dados_sisctm = Sisctm().executar(indice, credenciais, pasta_indice)
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
    logger.info(f"Relatório gerado")
