from utils import logger, section_log

from utils import settings
from core import gerar_relatorio
from .sistemas import Siatu
from .sistemas import Urbano
from .sistemas import Sisctm
from .sistemas import GoogleMaps
from .sistemas import Sigede
from .sistemas import Poligono

import os, logging
from typing import Tuple, Dict, List, Any, Callable, Optional


def processar_protocolo(
    protocolo: str, credenciais: Dict[str, str], pasta_resultados: str
) -> List[str]:
    """Execução do módulo SIGEDE (Protocolos). Captura de ICs no protocolo e cria a pasta do protocolo.
    A lista de índices retornada nessa função será utiliza nas próximas etapas da automação.
    """

    pasta_protocolo = os.path.join(pasta_resultados, protocolo)
    os.makedirs(pasta_protocolo, exist_ok=True)

    lvl = logging.WARNING if settings.LOT_DEBUGGER else logging.INFO

    context = f"PROTOCOLO: {protocolo}"     

    section_log(f"< SIGEDE  - Protocolo: {protocolo} >","-",50,0,lvl)
    indices: List[str] = []
    
    try:
        indices = Sigede().executar(protocolo, credenciais, pasta_protocolo)
        if not indices:
            logger.warning(f"⚠️ {context} | ETAPA: SIGEDE | AVISO: Nenhum IC encontrado ou erro no acesso.\n")
    except Exception as e:
        logger.error(f"🚫🚫 {context} | ETAPA: SIGEDE | ERRO FATAL: {e}\n")

    logger.debug(f"processar_indice: Sigede:  {indices}\n")

    return indices


def processar_indice(
    indice: str,
    credenciais: Dict[str, str],
    protocolo: str,
    pasta_resultados: str,
    status_title: Optional[str] = "",
    statusUpdater: Optional[Callable[[str], None]] = None,
    progressBarUpdater: Optional[Callable[[float], None]] = None,
    progressBarDict: Optional[Dict[str, float]] = None,
    VIRTUAL_PRTCL: bool = False,
):
    """
    Execução dos módulos SIATU, URBANO e SISCTM para o IC especificado. Também Gera relatório e Cria a pasta do IC.
    """
    indice = indice.upper().strip()
    porcao_de_progresso = 1.0
    context = f"PROTOCOLO: {protocolo} | IC: {indice}"
    lvl = logging.WARNING if settings.LOT_DEBUGGER else logging.INFO

    if (
        progressBarDict is not None
        and progressBarDict.get("n_cadastrais_associados", 0) > 0
    ):
        porcao_de_progresso = 1.0 / progressBarDict["n_cadastrais_associados"]
    else:
        porcao_de_progresso = 0

    pasta_indice = os.path.join(pasta_resultados, protocolo, indice)
    os.makedirs(pasta_indice, exist_ok=True)

    status_title = status_title if (status_title) else f"Protocolo : {protocolo}"
    # ------- STATUS, LOG e EXECUÇÃO :: SIATU ------
    if statusUpdater:
        status = f"{status_title}  -  SIATU  :  ({indice})"
        statusUpdater(status)
    section_log(f"< SIATU  -  IC: {indice} >", level = lvl)

    dados_pb: Dict[str, Any]
    anexos_count: int

    try:
        (dados_pb, anexos_count) = Siatu().executar(indice, credenciais, pasta_indice)
        if not dados_pb:
            logger.warning(f"⚠️ {context} | ETAPA: SIATU | AVISO: dados_pb não capturados.\n")
    except Exception as e:
        logger.error(f"🚫 {context} | ETAPA: SIATU | ERRO FATAL: {e}\n")
        dados_pb, anexos_count = {}, 0
    
    logger.debug(f"processar_indice: Siatu: {dados_pb, anexos_count}\n")

    # Calcula e atualiza a progress bar para após o Siatu
    if progressBarUpdater and progressBarDict:
        increment = (progressBarDict["peso_tarefa"] * 0.2) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: URBANO ------
    if statusUpdater:
        status = f"{status_title}  -  URBANO  :  ({indice})"
        statusUpdater(status)
    section_log(f"< URBANO  -  IC: {indice} >", level = lvl)

    dados_projeto: Dict[str, Any]
    projetos_count: int

    try:
        (dados_projeto, projetos_count) = Urbano().executar(indice, credenciais, pasta_indice)
        if not dados_projeto:
            logger.warning(f"⚠️ {context} | ETAPA: URBANO | AVISO: Falha na captura de projetos/alvarás.\n")
    except Exception as e:
        logger.error(f"🚫 {context} | ETAPA: URBANO | ERRO: {e}\n")
        dados_projeto, projetos_count = {}, 0

    logger.debug(f"processar_indice: Urbano: {dados_projeto, projetos_count}\n")

    # Calcula e atualiza a progress bar para após o Urbano
    if progressBarUpdater and progressBarDict:
        increment = (progressBarDict["peso_tarefa"] * 0.2) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: SISTM ------
    if statusUpdater:
        status = f"{status_title}  -  SISCTM  :  ({indice})"
        statusUpdater(status)
    section_log(f"< SISCTM  -  IC: {indice} >", level = lvl )

    logger.debug("processar_indice: - pré execução do Sisctm.executar()")
    logger.debug(indice)
    logger.debug(f"{pasta_indice}\n")

    dados_sisctm: Dict[str, Any] = {}
    try:
        dados_sisctm = Sisctm().executar(indice, credenciais, pasta_indice)
        if not dados_sisctm:
            logger.warning(f"⚠️ {context} | ETAPA: SISCTM | AVISO: Falha na captura de áreas IPTU/GEO.\n")
    except Exception as e:
        logger.error(f"🚫 {context} | ETAPA: SISCTM | ERRO: {e}\n")

    logger.debug(f"processar_indice: Sisctm: \n{dados_sisctm}\n")

    # Calcula e atualiza a progress bar para após o Sisctm
    if progressBarUpdater and progressBarDict:
        taxa = 0.35 if VIRTUAL_PRTCL else 0.25
        increment = (progressBarDict["peso_tarefa"] * taxa) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: POLÍGONO ------
    if statusUpdater:
        status = f"{status_title}  -  POLÍGONO KML :  ({indice})"
        statusUpdater(status)
    section_log(f"< POLÍGONO  -  IC: {indice} >", level = lvl)    
    
    kml_gerado: bool = False
    try:
        kml_gerado = Poligono().executar(indice, pasta_indice)
        if not kml_gerado:
            logger.warning(f"⚠️ {context} | ETAPA: POLÍGONO | AVISO: KML não disponível.\n")
    except Exception as e:
        logger.error(f"🚫 {context} | ETAPA: POLÍGONO | Não foi possível obter o polígono. ERRO: {e}\n")
    
    if kml_gerado:
        logger.info(f"Sucesso: Polígono KML integrado à pasta do IC {indice}.\n")
        
    # Calcula e atualiza a progress bar para após o Polígono
    if progressBarUpdater and progressBarDict:
        increment = (progressBarDict["peso_tarefa"] * 0.05) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])
    

    # ------ STATUS, LOG e EXECUÇÃO :: GOOGLE MAPS ------
    if statusUpdater:
        status = f"{status_title}  -  G-MAPS  :  ({indice})"
        statusUpdater(status)
    section_log(f"< GOOGLE MAPS  -  IC: {indice} >", level = lvl)
    try:
        GoogleMaps().executar(indice, dados_sisctm, dados_pb, pasta_indice)
    except Exception as e:
        logger.error(f"🚫 {context} | ETAPA: GOOGLE MAPS | ERRO: {e}\n")

    # Calcula e atualiza a progress bar para após o Google Maps
    if progressBarUpdater and progressBarDict:  # Calcula
        increment = (progressBarDict["peso_tarefa"] * 0.2) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ GERANDO RELATÓRIO ------ :
    if statusUpdater:
        status = f"{status_title}  -  GERANDO RELATÓRIO  :  ({indice})"
        statusUpdater(status)
    section_log(f"<  RELATÓRIO do IC: {indice} >")

    pdf_path = os.path.join(pasta_indice, f"1. Relatório de Triagem - {indice}.pdf")
    gerar_relatorio(
        indice_cadastral=indice,
        anexos_count=anexos_count,
        projetos_count=projetos_count,
        pasta_anexos=pasta_indice,
        prps_trabalhador=credenciais["usuario"],
        nome_pdf=pdf_path,
        dados_planta=dados_pb,
        dados_projeto=dados_projeto,
        dados_sisctm=dados_sisctm,
        ic_avulso=VIRTUAL_PRTCL,
    )
    logger.log(lvl,f"Relatório gerado para {context}!\n\n")
