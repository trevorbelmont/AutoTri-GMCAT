from utils import logger, section_log # importa o objetor logger e a funçõa section_log (de utils/logger.py)
from core import gerar_relatorio
from .sistemas import Siatu
from .sistemas import Urbano
from .sistemas import Sisctm
from .sistemas import GoogleMaps
from .sistemas import Sigede

import os
from typing import Tuple, Dict, List, Any, Callable, Optional


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

    section_log(f"< SIGEDE  - Protocolo: {protocolo} >") # Adiciona, nos LOGs, o separador de seção do SIGEDE
    indices: List[str] = Sigede().executar(protocolo, credenciais, pasta_protocolo)
    return indices      # Retorna Lista de Índices Cadastrais (IC) a serem processados


def processar_indice(indice: str, credenciais: Dict[str, str], protocolo: str, pasta_resultados: str,           # Param. obrigatórios pra triagem de índices
                     status_title: Optional[str] = "", statusUpdater: Optional[Callable[[str],None]] = None,    # Param. opcionais - pra interface
                     VIRTUAL_PRTCL: bool = False) -> None:                                                      # param. opcional - triagem de ic
    """
    Execução dos módulos SIATU, URBANO e SISCTM para UM ÚNICO índice especificado, Gera relatório e Cria a pasta do IC.
    
    :param indice: Índice cadastral (IC) a ser processado.
    :param credenciais: Dicionário contendo as credenciais de acesso.
    :param protocolo: Número do protocolo pai.
    :param pasta_resultados: Caminho para a pasta raiz dos resultados.

    :param status_title: String de monitoramento de processamento de protocolos. Ex: " PROTOCOLO 1/1: 700701792560" - OPCIONAL
    :param statusUpdater: função de atualização do StatusText da interface - OPICIONAL
    :return: None
    """

    # Definição do caminho e criação da pasta 
    pasta_indice = os.path.join(pasta_resultados, protocolo, indice)
    os.makedirs(pasta_indice, exist_ok=True) # exist_ok= True : garante que, se necessário, os diretórios parent sejam criados.
    # Essa é uma linha robusta que altera o comportamento do método os.makedirs(____, exist_ok=True) para não lançar exceção e parar a automação
    #caso a pasta em questão não exista. Esse parâmetro garante que, caso não exista, ela seja criada no caminho especificado.

    '''Executa a automação dos Bots Siatu, Urbano,Sisctm e GoogleMaps pro IC atual (via classes de serviços- os adapters dos "bot-core")''' 
    
    # Garante que a str status_title não seja None. Case seja, substitui por string vazia.
    # A mesma str status_title será usada no começo de todos os statusUpdater
    status_title = status_title if (status_title) else f"Protocolo : {protocolo}"  #Poderia ser feito na assinatura da função, mas é bom deixar explícito o comportamento

    # ------- STATUS, LOG e EXECUÇÃO :: SIATU ------
    if statusUpdater:
        status =  f"{status_title}  -  SIATU  :  ({indice})"
        statusUpdater(status)                         
    section_log(f"< SIATU  -  IC: {indice} >")    # Adiciona seção SIATU pra cada índice nos LOGS

    # Instancia variáveis e exectua Siatu
    dados_pb: Dict[str, Any]
    anexos_count: int
    (dados_pb, anexos_count) = Siatu().executar(indice, credenciais, pasta_indice)


    # ------ STATUS, LOG e EXECUÇÃO :: URBANO ------
    if statusUpdater:
        status =  f"{status_title}  -  URBANO  :  ({indice})"
        statusUpdater(status)                         
    section_log(f"< URBANO  -  IC: {indice} >")    # Adiciona seção SIATU pra cada índice nos LOGS

    # Instancia variáveis e executa Urbano.executar(...)
    # Adiciona seção URBANO pra cada índice nos LOGS
    dados_projeto: Dict[str, Any]
    projetos_count: int
    (dados_projeto, projetos_count) = Urbano().executar(indice, credenciais, pasta_indice)


    # ------ STATUS, LOG e EXECUÇÃO :: SISTM ------
    if statusUpdater:
        status =  f"{status_title}  -  SISCTM  :  ({indice})"
        statusUpdater(status)                         
    section_log(f"< SISCTM  -  IC: {indice} >")   # Adiciona seção SIATU pra cada índice nos LOGS
    print("DEBUG SISCTM:")
    print (indice)
    print (credenciais)
    print (pasta_indice)
    dados_sisctm: Dict[str, Any] = Sisctm().executar(indice, credenciais, pasta_indice)

    # ------ STATUS, LOG e EXECUÇÃO :: GOOGLE MAPS ------
    if statusUpdater:
        status =  f"{status_title}  -  G-MAPS  :  ({indice})"
        statusUpdater(status)                         
    section_log(f"< GOOGLE MAPS  -  IC: {indice} >")   # Adiciona seção SIATU pra cada índice nos LOGS
    GoogleMaps().executar(indice, dados_sisctm, dados_pb, pasta_indice)

    # ------ GERANDO RELATÓRIO ------
    if statusUpdater:
        status =  f"{status_title}  -  GERANDO RELATÓRIO  :  ({indice})"
        statusUpdater(status)                         
    section_log(f"<  RELATÓRIO do IC: {indice} >")   # Adiciona seção SIATU pra cada índice nos LOGS

    # O caminho para o relatório de Triagem (PDF)
    pdf_path = os.path.join(pasta_indice, f"1. Relatório de Triagem - {indice}.pdf")
    # Gera o relatório pdf com todos os dados acumulados (e links pra arquivos locais) em pdf
    gerar_relatorio(
        indice_cadastral=indice,
        anexos_count=anexos_count,
        projetos_count=projetos_count,
        pasta_anexos=pasta_indice,
        prps_trabalhador=credenciais["usuario"],    # identifica o trabalhador sem passar credenciais críticas (senhas)
        nome_pdf=pdf_path,
        dados_planta=dados_pb,
        dados_projeto=dados_projeto,
        dados_sisctm=dados_sisctm,
        ic_avulso = VIRTUAL_PRTCL,                  # Avisa pro gerador se o IC está associado à um Protocolo Virtual (triagem por IC)
    )
    logger.info(f"Relatório gerado!\n\n")
