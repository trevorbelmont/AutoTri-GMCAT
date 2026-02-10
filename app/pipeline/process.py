from utils import logger, section_log
from utils import settings
from core import gerar_relatorio
from .sistemas import Siatu
from .sistemas import Urbano
from .sistemas import Sisctm
from .sistemas import GoogleMaps
from .sistemas import Sigede

import os
from typing import Tuple, Dict, List, Any, Callable, Optional


def processar_protocolo(
    protocolo: str, credenciais: Dict[str, str], pasta_resultados: str
) -> List[str]:
    """Execução do módulo SIGEDE (Protocolos). Captura de ICs no protocolo e cria a pasta do protocolo.
    A lista de índices retornada nessa função será utiliza nas próximas etapas da automação.
    """

    pasta_protocolo = os.path.join(pasta_resultados, protocolo)
    os.makedirs(pasta_protocolo, exist_ok=True)

    section_log(f"< SIGEDE  - Protocolo: {protocolo} >")
    indices: List[str] = Sigede().executar(protocolo, credenciais, pasta_protocolo)

    logger.debug(f"processar_indice: Sigede:  {indices}")

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

    porcao_de_progresso = 1.0

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
    section_log(f"< SIATU  -  IC: {indice} >")

    dados_pb: Dict[str, Any]
    anexos_count: int

    (dados_pb, anexos_count) = Siatu().executar(indice, credenciais, pasta_indice)

    logger.debug(f"processar_indice: Siatu: {dados_pb, anexos_count}")

    # Calcula e atualiza a progress bar para após o Siatu
    if progressBarUpdater and progressBarDict:
        increment = (progressBarDict["peso_tarefa"] * 0.2) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: URBANO ------
    if statusUpdater:
        status = f"{status_title}  -  URBANO  :  ({indice})"
        statusUpdater(status)
    section_log(f"< URBANO  -  IC: {indice} >")

    dados_projeto: Dict[str, Any]
    projetos_count: int

    (dados_projeto, projetos_count) = Urbano().executar(
        indice, credenciais, pasta_indice
    )

    logger.debug(f"processar_indice: Urbano: {dados_projeto, projetos_count}")

    # Calcula e atualiza a progress bar para após o Urbano
    if progressBarUpdater and progressBarDict:
        increment = (progressBarDict["peso_tarefa"] * 0.2) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: SISTM ------
    if statusUpdater:
        status = f"{status_title}  -  SISCTM  :  ({indice})"
        statusUpdater(status)
    section_log(f"< SISCTM  -  IC: {indice} >")

    logger.debug("processar_indice: - pré execução do Sisctm.executar()")
    logger.debug(indice)
    logger.debug(pasta_indice)

    dados_sisctm: Dict[str, Any] = {}
    dados_sisctm = Sisctm().executar(indice, credenciais, pasta_indice)
    logger.debug(f"processar_indice: Sisctm: \n{dados_sisctm}")

    # Calcula e atualiza a progress bar para após o Sisctm
    if progressBarUpdater and progressBarDict:
        taxa = 0.4 if VIRTUAL_PRTCL else 0.3
        increment = (progressBarDict["peso_tarefa"] * taxa) * porcao_de_progresso
        progressBarDict["atual"] += increment
        progressBarUpdater(progressBarDict["atual"])

    # ------ STATUS, LOG e EXECUÇÃO :: GOOGLE MAPS ------
    if statusUpdater:
        status = f"{status_title}  -  G-MAPS  :  ({indice})"
        statusUpdater(status)
    section_log(f"< GOOGLE MAPS  -  IC: {indice} >")
    GoogleMaps().executar(indice, dados_sisctm, dados_pb, pasta_indice)

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
    logger.info(f"Relatório gerado!\n\n")
