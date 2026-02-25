from typing import List, Dict, Any, Tuple, Optional
from pipeline.interface import SistemaAutomacao
from core import SiatuAuto, UrbanoAuto, SisctmAuto, GoogleMapsAuto, SigedeAuto,PoligonoAuto
from utils import driver_context, logger, retry, settings


class Sigede(SistemaAutomacao):
    """Adapter para o sistema SIGEDE. Responsável pela busca de protocolos e identificação de índices cadastrais."""

    def executar(
        self, protocolo: str, credenciais: Dict[str, str], pasta_protocolo: str
    ) -> List[str]:
        """Executa a automação do SIGEDE para buscar índices vinculados a um protocolo.

        :return: Lista de ICs associados ao protocolo.
        """

        indices: List[str] = []

        with driver_context(pasta_protocolo) as driver:

            sigede = SigedeAuto(
                driver=driver,
                url="https://cas.pbh.gov.br/cas/login?service=https%3A%2F%2Fsigede.pbh.gov.br%2Fsigede%2Flogin%2Fcas",
                usuario=credenciais["usuario_sigede"],
                senha=credenciais["senha_sigede"],
                pasta_download=pasta_protocolo,
            )

            if sigede.acessar() and sigede.login() and sigede.navegar(protocolo):
                indices = sigede.verificar_tabela()

        logger.info(f"SIGEDE concluído para protocolo {protocolo}.\n")
        return indices


class Siatu(SistemaAutomacao):
    """Adapter para o sistema SIATU.
    Responsável pela orquestração da extração de dados (Planta Básica) e documentos (Anexos) de um IC.
    """

    def executar(
        self, indice: str, credenciais: Dict[str, str], pasta_indice: str
    ) -> Tuple[Dict[str, Any], int]:
        """Executa a automação do SIATU (obter dados cadastrais e documentos) do Índice informado .

        :return: Uma tupla (dados_pb, anexous_count) contendo:
        1. Dicionário com dados da Planta Básica (área, endereço, etc).
        2. Inteiro com a contagem de anexos baixados."""

        dados_pb: Dict[str, Any] = {}
        anexos_count: int = 0

        # Ativa a flag: --unsafely-treat-insecure-origin-as-secure durante a criação do driver_context
        add_config = True


        @retry(max_retries=settings.RETRY_MAX, delay=settings.RETRY_DELAY, exceptions=(Exception,))
        def fluxo_siatu():

            with driver_context(pasta_indice, add_config=add_config) as driver:
                siatu = SiatuAuto(
                    driver=driver,
                    url="https://siatu-producao.pbh.gov.br/seguranca/login?service=https%3A%2F%2Fsiatu-producao.pbh.gov.br%2Faction%2Fmenu",
                    usuario=credenciais["usuario"],
                    senha=credenciais["senha"],
                    pasta_download=pasta_indice,
                )
                # NOTE: o retorno de fluxo Siatu está condicionado à todas etapas serem bem sucedidas - tornar o retorno indepndente?
                if siatu.acessar() and siatu.login() and siatu.navegar():
                    return siatu.planta_basica(indice), siatu.download_anexos(indice)

        try:
            dados_pb, anexos_count = fluxo_siatu()
        except Exception as e:
            logger.error(f"Falha no fluxo do SIATU para índice {indice}: {e}.\n")

        logger.info(f"Siatu concluído para índice {indice}.\n")
        return (dados_pb, anexos_count)


class Urbano(SistemaAutomacao):
    """Adapter para o Portal de Edificações (Urbano).
    Focado na extração de dados de projetos de construção, alvarás e baixas do IC informado.
    """

    def executar(
        self, indice: str, credenciais: Dict[str, str], pasta_indice: str
    ) -> Tuple[Dict[str, Any], int]:
        """Executa a automaçaõ do URBANO - obter documentos de licenciamento e dados construtivos (área).
        :return: Uma tupla (dados_projeto, contagem_projetos).
        """

        dados_projeto: Dict[str, Any] = {}
        projetos_count: int = 0

        with driver_context(pasta_indice) as driver:
            urbano = UrbanoAuto(
                driver=driver,
                url="https://urbano.pbh.gov.br/edificacoes/#/",
                usuario=credenciais["usuario"],
                senha=credenciais["senha"],
                pasta_download=pasta_indice,
            )

            if urbano.acessar() and urbano.login():
                projetos_count, dados_projeto = urbano.download_projeto(indice)

        logger.info(f"Urbano concluído para índice {indice}.\n")
        return (dados_projeto, projetos_count)


class Sisctm(SistemaAutomacao):
    """Adapter para o sistema de Mapa (SISCTM).
    Responsável pela captura de evidências visuais (Prints) e dados geoespaciais (Áreas) o IC informado.
    """

    def executar(
        self, indice: str, credenciais: Dict[str, str], pasta_indice: str
    ) -> Dict[str, Any]:
        """
        Executa a navegação e automação do Sistema SISCTM (prints, áreas e informações)
        :return: Dicionário com dados geográficos (área terreno, área construída, endereço oficial).
        """
        dados_sisctm: Dict[str, Any] = {}

        with driver_context(pasta_indice) as driver:
            sisctm = SisctmAuto(
                driver=driver,
                url="https://acesso.pbh.gov.br/auth/realms/PBH/protocol/openid-connect/auth?client_id=sisctm-mapa&redirect_uri=https%3A%2F%2Fsisctm.pbh.gov.br%2Fmapa%2Flogin",
                usuario=credenciais["usuario"],
                senha=credenciais["senha"],
                pasta_download=pasta_indice,
            )

            if sisctm.login() and sisctm.ativar_camadas(indice):
                dados_sisctm = sisctm.capturar_areas()

        logger.info(f"SISCTM concluído para índice {indice}.\n")
        return dados_sisctm

class Poligono(SistemaAutomacao):
    """
    Adapter para o serviço de Geoprocessamento (WFS).
    Responsável por baixar o arquivo KML do terreno para visualização no Google Earth.
    """

    def _formatar_ic_excecao(self, ic: str) -> str:
        """
        Formata índices que fogem ao padrão de 13 caracteres (6-3-4).
        Ex: 981142W0020015 -> 981142W002 0015
        """
        if len(ic) > 13:
            # Pega os últimos 4 (lote) e o restante vira a primeira parte
            return f"{ic[:-4]} {ic[-4:]}"
        return ic

    
    def executar(
        self, 
        indice: str, 
        pasta_indice: str
    ) -> bool:
        """
        Executa a captura do polígono KML. 
        """
        
        poligono_bot = PoligonoAuto(pasta_download=pasta_indice)

        sucesso = poligono_bot.capturar_kml(indice)

        if not sucesso:
            ic_lower = indice.lower().strip()
            logger.info(f"Tentando novamente com IC na formatação: {ic_lower}")
            sucesso = poligono_bot.capturar_kml(ic_lower)

        if sucesso:
            logger.info(f"Arquivo KML gerado com sucesso para {indice}.\n")
        else:
            logger.warning(f"Não foi possível obter o KML para {indice}.\n")

        return sucesso

class GoogleMaps(SistemaAutomacao):
    """Adapter para o Google Maps.
    Gera evidências visuais (Satélite/Fachada) baseadas em endereços encontrados nos sistemas anteriores.
    """

    def executar(
        self,
        indice: str,
        dados_sisctm: Optional[Dict[str, Any]],
        dados_pb: Optional[Dict[str, Any]],
        pasta_indice: str,
    ) -> None:
        """Orquestra a busca e captura de imagens no Google Maps (com os dados de Sistm, Siatu e índice (do Sigede)."""
        if dados_sisctm or dados_pb:
            # Define o endereço priorizando os dados extraídos do SISCTM, quando disponíveis.
            endereco = (
                dados_sisctm.get("endereco_ctmgeo")
                or dados_pb.get("endereco_imovel")
                or "Não encontrado"
            )

        with driver_context(pasta_indice) as driver:
            google = GoogleMapsAuto(
                driver,
                url="https://www.google.com/maps/",
                endereco=endereco,
                pasta_download=pasta_indice,
            )

            if google.acessar_google_maps():
                google.navegar()

        logger.info(f"Google Maps concluído para índice {indice}.\n")
