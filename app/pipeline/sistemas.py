from pipeline.interface import SistemaAutomacao   # importa a classe abstrata SistemaAutomação (classe parent)
from core import SiatuAuto, UrbanoAuto, SisctmAuto, GoogleMapsAuto, SigedeAuto
from utils import driver_context, logger, retry

'''
===========================================================================================================================================================
As classes definidas neste módulo são apenas camadas de serviço (Adapters ou Wrappers). 
Elas integram a classe abstrata definida em app/pipeline/interface/base.py com os bots reais respectivos (na pasta app/core). 
Uma das principais vantagens destas camadas é gerenciar o contexto e o tempo de vida dos recursos (por exemplo janelas do Chrome, credenciais e etc)
e interagir com o bot separando a interface dos detalhes internos de navegação (que podem mudar no futuro).
Algumas dessas classes também usam @retry (definido em app/utils/decorators.py) para aumentar a resiliência da automação via repetição TOTAL da automação do webdriver.
===========================================================================================================================================================
'''

'''
(bloco "with": é executado para gerenciamento de contexto. Ele garante que o contexto passado em seguida seja inicializado e "destruído" de forma automática. 
(Similar ao contrutor e destrutor do C++ que garantea a limpeza do recurso quando ele sai de contexto.)
Aqui ele é utilizao para garantir que o driver (que aciona o Chrome e o ChromeDriver) seja liberado automaticamente ao fim da execução.
De forma a garantir processos não ativos ou não intencionais no chrome. Isso é uma implementação de SEGURANÇA E OTIMIZAÇÃO  do sistema. 
'''


''' Define a classe Sigede (camada de serviço) que extende de SistemaAutomação e define o método "virtual" executar(...) - do contrato da classe pai. 
    Faz a injeção e gerenciamento de contexto, ofercendo os recursos necessários para classe de automação real, SigedeAuto, em app/core/sigede.py'''
class Sigede(SistemaAutomacao):
    def executar(self, protocolo, credenciais, pasta_protocolo):
        indices = []    # insancia uma lista de índices a ser retornada ao fim das automações executadas neste método.
        
        # inicializa o contexto driver_context, passando a pasta de download preferencial "pasta_protocolo" 
        # driver_context(pasta) é um método decorado com @contextmanager. Ele adquire e inicializa os recursos (Google Chrome, ChromeDriver e etc) 
        # e libera tais quando sai do contexto.
        with driver_context(pasta_protocolo) as driver:
            # instancia o objeto da classe SigedAuto (em core/sigede.py)
            # Atenção: as credenciais do sistema Sigede parecem serem diferentes dos outros bots
            sigede = SigedeAuto(
                driver=driver,
                url="https://cas.pbh.gov.br/cas/login?service=https%3A%2F%2Fsigede.pbh.gov.br%2Fsigede%2Flogin%2Fcas",
                usuario=credenciais["usuario_sigede"],  # Usa credenciais específicas do sistema sigede
                senha=credenciais["senha_sigede"],
                pasta_download=pasta_protocolo,         # Define a pasta de download neste contexto
            )

            # A objeto da classe SigedeAuto faz toda a automação e,
            #  se todos so passos de navegação deram certos, captura os índices cadastrais associados ao processo
            if sigede.acessar() and sigede.login() and sigede.navegar(protocolo):
                indices = sigede.verificar_tabela()

        logger.info(f"SIGEDE concluído para protocolo {protocolo}")
        return indices  # retorna a lista de índices

''' Define a classe Siato (camada de serviço) que extende de SistemaAutomação e define o método "virtual" executar(...) - do contrato da classe pai. 
    Faz a injeção e gerenciamento de contexto e a lógica de repteição (@retry) e lançamento de exceção, se todas retentativas falharem.
    Faz a integração da classe abstrata, SistemaAutomação com a classe core (que realmente implementa as rotinas do bot),SiatuAuto, em app/core/siatu.py. '''
class Siatu(SistemaAutomacao):
    # Define o método virtual do contrato (SitemasAutomação - classe pai).add()
    # indice = Nº do Índice Cadastral qa ser buscado no sistema do SIATU
    def executar(self, indice, credenciais, pasta_indice):
        dados_pb = {}       # dicionário de plantas básicas a ser preenchido durante a automação (?)
        anexos_count = 0    # contador de anexos
        add_config = True   # Esta variável determinará a flag de segurança do chrome na hora de criar o driver_context (e por consequência o navegador e ChromeDriver).
                            # Ela ativará a flag: --unsafely-treat-insecure-origin-as-secure. A camada de serviço é a responsável por determinar essa configuração extra de segurança.

        # Decorators são funções de alta ordem: basicamente ele está determinando o número de retentativas da função que é aplicado, 
        # o atraso entre as tentativas e tipos de exceções que diparam a repetição. (definido em app/utils/decorators.py)
        @retry(max_retries=4, delay=5, exceptions=(Exception,))
        def fluxo_siatu():

            # Gerencia contexto: Incializa, gerencia e libera os recurso do driver_context durante a automação
            with driver_context(pasta_indice, add_config=add_config) as driver:
                # Cria o objeto da classe de automação que realmente fará a busca usando o webdriver.
                # Classe SiatuAuto definida em app/core/siatu
                siatu = SiatuAuto(
                    driver=driver,
                    url="https://siatu-producao.pbh.gov.br/seguranca/login?service=https%3A%2F%2Fsiatu-producao.pbh.gov.br%2Faction%2Fmenu",
                    usuario=credenciais["usuario"],     # usa as credenciais padrões
                    senha=credenciais["senha"],         # usa as credenciais padrões
                    pasta_download=pasta_indice,
                )
                # Se a automação foi bem sucedida no Siato, faz download e retorna os dados planta básica, faz download dos anexos e retorna a quantidade de anexos (daquele Índice Cadastral)
                if siatu.acessar() and siatu.login() and siatu.navegar():
                    return siatu.planta_basica(indice), siatu.download_anexos(indice)

        try:
            # Tenta a execução da função definida (com o decorator), se falhar a última vez (definida no @retry) a exceção é lançada
            dados_pb, anexos_count = fluxo_siatu()
        except Exception as e: # Regista a falha no log e continua os processos.
            logger.error(f"Falha no fluxo do SIATU para índice {indice}: {e}")

        # Se bem sucedido registra o sucesso (e o índice bem sucedido) e retorna os dados da planta básica e o número de anexos.
        logger.info(f"Siatu concluído para índice {indice}")
        return dados_pb, anexos_count


''' Define a classe Urbano (camada de serviço) que estende de SistemaAutomação e define o método "virtual" executar(...) - do contrato da classe pai. 
Faz a injeção e gerenciamento de contexto do WebDriver, fornecendo os recursos necessários (driver configurado e credenciais) para a classe de automação real, UrbanoAuto, em app/core/urbano.py. 
Esta camada é responsável por orquestrar a busca por dados técnicos (alvarás, baixas e etc) no sistema urbano usando o objeto UrbanoAuto (core da automação) '''
class Urbano(SistemaAutomacao):
    # Definição do método executar herdado, mas não definido, do contrato de SistemasAutomação
    def executar(self, indice, credenciais, pasta_indice):
        #instancia variáveis a serem retornadas
        dados_projeto = {}
        projetos_count = 0

        # Gerencia contexto: Incializa, gerencia e libera os recurso do driver_context durante a automação
        with driver_context(pasta_indice) as driver:
            # Instancia objeto da Classe UrbanoAuto (onde é implementado o core da automação), passando os parâmetros da automação. 
            # Classe UrbanoAuto definida em app/core/urbano.py
            urbano = UrbanoAuto(
                driver=driver,
                url="https://urbano.pbh.gov.br/edificacoes/#/",
                usuario=credenciais["usuario"],         # credenciais padrão
                senha=credenciais["senha"],             # credenciais padrão
                pasta_download=pasta_indice,
            )

            # Se a automação de acessar a página e fazer login foi bem sucedida, faz o download dos dados técnicos e guarda os dados do projeto no dict dados_projeto
            if urbano.acessar() and urbano.login():
                projetos_count, dados_projeto = urbano.download_projeto(indice)
            # ¬ em caso de falhas na automação, este método não trata falhas de download ou acesso.
            # Internamente urbaano.download_projeto(...), no entanto, loga falhas e implementa tratamento de exceções.

        # Registra conclusão do da tarefa no logger e retorna o dict com os dados do projeto e o número de projetos.
        logger.info(f"Urbano concluído para índice {indice}")
        return dados_projeto, projetos_count

''' Define a classe Sisctm (camada de serviço) que estende de SistemaAutomação e define o método "virtual" executar(...) - do contrato da classe pai. 
Faz a injeção e gerenciamento de contexto do WebDriver, fornecendo os recursos necessários (driver configurado e credenciais) para a classe de automação real, SisctmAuto, em app/core/sisctm.py. 
Esta camada é responsável por automatizar o acesso ao mapa geográfico, ativar camadas específicas e extrair dados de área e endereço. '''
class Sisctm(SistemaAutomacao):
    # Definição da função executar(...) herdada, porém não definida, da classe pai, SistemaAutomacao
    def executar(self, indice, credenciais, pasta_indice):
        # Inicia dicionário a ser retornado
        dados_sisctm = {}

        # Gerencia contexto: Incializa, gerencia e libera os recurso do driver_context durante a automação
        with driver_context(pasta_indice) as driver:
            # Instancia o bot core, SisctmAuto, definindo as variáveis de automação. Classe SisctmAuto definida em app/core/sisctm.py
            sisctm = SisctmAuto(
                driver=driver,
                url="https://acesso.pbh.gov.br/auth/realms/PBH/protocol/openid-connect/auth?client_id=sisctm-mapa&redirect_uri=https%3A%2F%2Fsisctm.pbh.gov.br%2Fmapa%2Flogin",
                usuario=credenciais["usuario"],     # credenciais padrão
                senha=credenciais["senha"],         # credenciais padrão
                pasta_download=pasta_indice,
            )

            # Se a automação for bem sucedida (focar mapa, ativar filtros e etc) os dados da tabela são capturados
            # sisctm.ativar_camadas(...) chama _prints_aereo(...), que realiza captura de tela. Imagens estão sendo geradas. 
            if sisctm.login() and sisctm.ativar_camadas(indice):
                dados_sisctm = sisctm.capturar_areas()

        logger.info(f"SISCTM concluído para índice {indice}")
        return dados_sisctm     # os dados retornados nesse método serão utilizados na automação do GoogleMaps

''' Define a classe GoogleMaps (camada de serviço) que estende de SistemaAutomação e define o método "virtual" executar(...) - do contrato da classe pai. 
Esta é a última etapa de automação. A classe não retorna nada e não requer credenciais. Seu papel é orquestrar os dados dos bots anteriores, encontrar o endereço mais confiável, 
e injetá-lo no bot de automação real, GoogleMapsAuto (em app/core/google.py), para obter documentação visual (prints de mapa e fachada). '''
class GoogleMaps(SistemaAutomacao):
    # Define o método legado do contrato. Desta vez não são necessárias credenciais mas dados de endereço
    def executar(self, indice, dados_sisctm, dados_pb, pasta_indice):
        # bloco executado se pelo menos uma das automações anteriores, Sisctm ou Siatu, foi bem sucedida. Usa os dados retornados pelas funções.
        if dados_sisctm or dados_pb:
            # Define o endereço priorizando os dados extraídos do SISCTM, quando disponíveis, em detrimento dos dados SIATU.
            endereco = (
                dados_sisctm.get("endereco_ctmgeo")
                or dados_pb.get("endereco_imovel")
                or "Não encontrado"
            )
            
        # Inicia o contexto driver_context, que será usado para o navegador do Google Maps.
        with driver_context(pasta_indice) as driver:
            # Instancia o objeto da classe GoogleMapsAuto (em core/google.py)
            # Injeção de Dependência: Passa o driver, o endereço escolhido e a pasta para salvar os prints.
            google = GoogleMapsAuto(
                driver,
                url="https://www.google.com/maps/",
                endereco=endereco,
                pasta_download=pasta_indice,
            )

            # Se o acesso ao G-Maps foi bem sucedido, o bot executa a rotina de busca, ativação de satélite e prints (aéreo e fachada).
            if google.acessar_google_maps():
                google.navegar()            # Tratamentos de exceções e logging de erros são feitos dentro deste método, navegar().

        # Registra a conclusão da automação do G-Maps. Esta classe não retorna nada.
        logger.info(f"Google Maps concluído para índice {indice}")
