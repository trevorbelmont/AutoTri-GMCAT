import traceback
import time
import os
from typing import Dict, Optional, Any, List, Union, Iterable

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from utils import logger


class SisctmAuto:
    """
    Classe para automatizar tarefas relacionadas ao SISCTM via Selenium.

    ... (Docstring omitido por brevidade) ...
    """

    def __init__(
        self,
        driver,
        url: str,
        usuario: str,
        senha: str,
        pasta_download: str,
        timeout: int = 10,          # timeout é definido com valor padrão (se não definido na instanciação do objeto)
        checar_popup: bool = True,  # checar_popup também possui valor padrão (se não definido na instanciação)
    ):
        self.driver = driver
        self.url = url
        self.usuario = usuario
        self.senha = senha
        self.pasta_download = pasta_download
        # WebDriverWait é instanciado aqui e usado como self.wait
        self.wait = WebDriverWait(self.driver, timeout=timeout)
        self.checar_popup = checar_popup 


    def _click(self, element) -> None:
        """Tenta clicar diretamente, se falhar usa JavaScript."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)


    # Define um método universal para localizar elementos e interagir com eles (clicar ou não),
    # utilizando múltiplas estratégias de busca com lógica de fallback.
    #   - Usa **kwargs para definir estratégias de localização (id, xpath, css, etc.).
    #   - A ordem dos kwargs define a prioridade ENTRE estratégias.
    #   - Cada estratégia pode receber uma string única ou uma lista de strings,
    #   onde a ordem interna define o fallback DENTRO da mesma estratégia.
    #
    # TODO: Mover este método para cima na hierarquia de classes
    #       (assim como _click(...), este método é universal para todos os bot-cores).
    def _interact(
        self,
        nome_log: str,
        timeout_tentativa: float = 2.0,
        clicar: bool = True,
        **seletores: Union[str, Iterable[str]]
    ) -> Optional[WebElement]:
        """ Um click ou element finder mais robusto com lógica de fallback em dois níveis e tentativas em várias etapas implementada.
        Localiza um elemento usando estratégias de fallback prioritários, baseados na ordem que os argumentos passados.
        Além da procura do elemento na ordem das estratégias passadas por argumentos, há também prioridade de busca dentro do mesmo tipo de estratégia.
        Retorna o WebElement encontrado para uso posterior, caso necessário.
        
        :param nome_log: Nome para registro no log.
        :param timeout_tentativa: [OPCIONAL - default: 2.0 segs] Tempo máximo de espera pra cada seletor achar o elmento - em segs.
        :param clicar: [[OPCIONAL - default: True] Se True, executa o _click() automaticamente ao encontrar.
        :param **seletores: Pares de estratégia=valor ou estratégia=[valores].
                    A ordem dos argumentos define a prioridade entre estratégias,
                    e a ordem interna, quando usando listas, define o fallback dentro da mesma estratégia.
        :return: O WebElement encontrado ou None, se falhar em todos os seletores.
        
        Exemplo de uso:
            self._interact(
                nome_log="Botão Exemplo",
                id="meu_id",
                xpath=[
                    "//div[@class='primary']",
                    "//div[@class='secondary']"
                ],
                css=".botao-fallback"
            )
        """
        # Define os tipo de métodos de procura válidos (tags do código fonte)
        # Útil para evitar que tags não previstas no selenium sejam testadas
        
        mapa_by = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class_name': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }

        tempo_gasto = 0.0

        for estrategia, valores in seletores.items():
            if estrategia not in mapa_by:
                continue

            by_type = mapa_by[estrategia]

            # Normaliza para lista (mantém compatibilidade)
            if isinstance(valores, str):
                valores = [valores]

            for valor_seletor in valores:
                try:
                    elemento = WebDriverWait(self.driver, timeout_tentativa).until(
                        EC.element_to_be_clickable((by_type, valor_seletor))
                    )

                    tempo_gasto += timeout_tentativa
                    logger.info(
                        f"{nome_log} encontrado via '{estrategia}' "
                        f"em {tempo_gasto:.1f}s."
                    )

                    if clicar:
                        self._click(elemento)

                    return elemento

                except Exception:
                    tempo_gasto += timeout_tentativa
                    continue

        logger.error(
            f"ERRO: {nome_log} não encontrado após todas as tentativas. "
            f"Tempo total: {tempo_gasto:.1f}s."
        )
        return None
    

    def login(self) -> bool:
        """Realiza login no Keycloak PBH em páginas Vue.js."""
        
        try:
            logger.info("Iniciando login no SISCTM")
            self.driver.get(self.url)

            time.sleep(3)

            # Espera o formulário completo aparecer
            self.wait.until(
                lambda driver: driver.find_element(By.ID, "kc-form-servidor-login")
            )

            # Preenche usuário via JS
            campo_usuario = self.driver.find_element(By.ID, "username")
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));",
                campo_usuario,
                self.usuario,
            )
            logger.info("Campo de usuário preenchido via JS")

            
            campo_senha = self.driver.find_element(By.ID, "password")
            # Preenche senha via JS
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));",
                campo_senha,
                self.senha,
            )
            logger.info("Campo de senha preenchido via JS")

            # Clica no botão via JS
            btn_login = self.driver.find_element(By.ID, "kc-login")
            self.driver.execute_script("arguments[0].click();", btn_login)
            logger.info("Login realizado com sucesso")

            time.sleep(10)  # NOTE: o site tem animação e demora pra terminar de carregar,
                            # mas ter uma forma mais rápida que um sleep de 10 sec fixo pode ser bom (não sei se tem)

            # -----------------------------------------------------------
            # NOTE: Bloco de tratamento da Pop-up "Notas de Versão" - Estratégia "Fail Fast"
            # Se checar_popup estiver true, checa se a pop-up apareceu enquanto a página carregava.
            # Timeout curto (3s) para não atrasar execuções.
            # -----------------------------------------------------------

        
            '''NOTE: Após o login pode ocorrer problema do pop-up "Notas de Versão". 
            É algo fácil de resolver manualmente, mas vamos automatizar (visto que alguns usuários não souberam resolver por si só.)
                       
            !!! A ROTINA ABAIXO SÓ ACONTECE SE A VARIÁVEL  'checar_popup' (que possui valor default) estiver definida no construtor !!!
            
            -  Essa rotina acontece depois do time.sleep() acima de 10 segs. O pop-up certamente já apareceu 
            (geralmente é a primeira coisa a ser carregada).
            - Aí procuramos o pop-up e fechamos, e se não apareceu, seguimos.      
            
            TODO: Garantir que, se a checagem de popup estiver true na triagem do primeiro protocolo, ela auto-desliga nas próximas triagens.
            Isso elimina a perda de eficiência de 3 segundos caso o pop-up já tenha sido retirado na triagem anterior.
            (Protocolos são geralmente triados em séries numa única execução do AutoTri).
            '''
            
            if self.checar_popup:
                try:

                    # 1. Procura pelo Checkbox específico da pop-up (via aria-label, que é estável)
                    # Define um timeout máximo de 3 segundos pra visibilidade do "Mostrar Novamente" checkbox no pop-up
                    # NOTE: isso é mais uma dupla segurança - uma vez que já rolou 10 segs de sleep ao fim do login.
                    checkbox_popup = WebDriverWait(self.driver, 3).until(   
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            "//div[@role='checkbox' and @aria-label='Não mostrar novamente']"
                        ))
                    )
                    logger.info("Pop-up 'Notas da Versão' detectada. Iniciando tratamento...")
                    
                    # 2. Marcar "Não mostrar novamente" (se ainda não estiver marcado)
                    is_checked = checkbox_popup.get_attribute("aria-checked")
                    if is_checked == "false":
                        self._click(checkbox_popup)
                        logger.info("Opção 'Não mostrar novamente' marcada.")
                        time.sleep(0.5) # Breve respiro para a animação do check
                    
                    # 3. Fechar a Pop-up - Busca o ícone 'close' visível.
                    btn_fechar = self.driver.find_element(
                        By.XPATH, 
                        "//i[contains(@class, 'material-icons') and text()='close']"
                    )
                    self._click(btn_fechar)
                                        
                    # Espera a pop-up sumir visualmente para não bloquear o próximo clique
                    WebDriverWait(self.driver, 2).until(
                        EC.invisibility_of_element(checkbox_popup) #espera o elemento ficar "invisível" (não existe ou não está visível)
                    )
                    logger.info("Pop-up fechada com sucesso.")
                   
                except TimeoutException:
                    # Se no time sleep de 3 segs não apareceu nada, assumimos que o caminho está livre
                    logger.debug("Caminho livre: Nenhuma pop-up detectada (Fail Fast).")
                except Exception as e:
                    # Se der outro erro, logamos mas não paramos o fluxo (pode ser falso positivo)
                    logger.warning(f"Aviso ao tentar tratar pop-up: {e}")
            # -----------------------------------------------------------
            return True

        except Exception as e:
            logger.error("Erro no login do Keycloak PBH: %s", e)
            return False

    def ativar_camadas(self, indice_cadastral: str) -> bool: 
        """
        Navega pelo menu do sistema, ativa camadas específicas (Endereço, Lote CP) 
        e aplica o filtro pelo Índice Cadastral.

        :param indice_cadastral: O índice do imóvel para busca e filtro.
        :return: True se todas as camadas foram ativadas e o filtro aplicado com sucesso, False caso contrário.
        """
                
        etapa = "início"
        try:
            logger.info("Iniciando navegação pelo sistema SISCTM PBH")

            # Expande o menu
            etapa = "expandir menu"
            logger.debug("Tentando localizar botão de menu (expand_more)...")
            btn_menu = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//i[@class='q-icon on-right notranslate material-icons' and text()='expand_more']",
                    )
                )
            )
            self._click(btn_menu)
            logger.info("Menu expandido com sucesso")
            time.sleep(1)
            
            # Clica no item Fazenda
            etapa = "selecionar Fazenda"
            logger.debug("Localizando item 'Fazenda'...")
            item_fazenda = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[contains(@class,'q-item__section') and contains(text(),'Fazenda')]",
                    )
                )
            )
            self._click(item_fazenda)
            logger.info("Item 'Fazenda' marcado")
            time.sleep(0.5)

            # Desativa IDE-BHGeo
            etapa = "desativar IDE-BHGeo"
            logger.debug("Localizando item 'IDE-BHGeo'...")
            item_idebhgeo = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[contains(@class,'q-item__section') and contains(text(),'IDE-BHGeo')]",
                    )
                )
            )
            self._click(item_idebhgeo)
            logger.info("Item 'IDE-BHGeo' desativado")
            time.sleep(0.5)

            # Abre camadas
            etapa = "abrir camadas"
            logger.debug("Localizando botão de camadas...")
            btn_camadas = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//i[@class='q-icon notranslate material-icons' and text()='layers']",
                    )
                )
            )
            self._click(btn_camadas)
            logger.info("Menu de camadas aberto")
            time.sleep(1)

            # CAMADA ENDEREÇO
            etapa = "selecionar Endereço"
            logger.debug("Localizando item 'Endereço'...")
            menu_endereco = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Endereço']"))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", menu_endereco
            )
            self._click(menu_endereco)
            logger.info("Menu 'Endereço' selecionado")
            time.sleep(0.5)

            etapa = "marcar Endereço PBH"
            logger.debug("Localizando container da camada 'Endereço'...")
            container_endereco = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[text()='Endereço']/ancestor::div[contains(@class,'q-tree__node')]",
                    )
                )
            )
            logger.debug("Localizando checkbox 'Endereço PBH'...")
            endereco_pbh_checkbox = container_endereco.find_element(
                By.XPATH,
                ".//div[contains(@class,'q-tree__node--child')][.//img[contains(@src,'FazendaEnderecoPBH')]]//div[contains(@class,'q-checkbox')]",
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", endereco_pbh_checkbox
            )
            self._click(endereco_pbh_checkbox)
            logger.info("Camada 'Endereço PBH' marcada")
            time.sleep(0.5)

            # CAMADA PARCELAMENTO DO SOLO
            etapa = "selecionar Parcelamento do Solo"
            logger.debug("Localizando item 'Parcelamento do Solo'...")
            menu_parcelamento = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[text()='Parcelamento do Solo']")
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", menu_parcelamento
            )
            self._click(menu_parcelamento)
            logger.info("Menu 'Parcelamento do Solo' selecionado")
            time.sleep(0.5)

            etapa = "marcar Lote CP - ATIVO"
            logger.debug("Localizando container da camada 'Parcelamento do Solo'...")
            container_parcelamento = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[text()='Parcelamento do Solo']/ancestor::div[contains(@class,'q-tree__node')]",
                    )
                )
            )
            logger.debug("Localizando checkbox 'Lote CP - ATIVO'...")
            lote_cp_checkbox = container_parcelamento.find_element(
                By.XPATH,
                ".//div[contains(@class,'q-tree__node--child')][.//img[contains(@src,'FazendaLoteCP')]]//div[contains(@class,'q-checkbox')]",
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", lote_cp_checkbox
            )
            self._click(lote_cp_checkbox)
            logger.info("Camada 'Lote CP - ATIVO' marcada")
            time.sleep(0.5)

            # CAMADA TRIBUTÁRIO E FILTRO
            etapa = "selecionar Tributário"
            logger.debug("Localizando item 'Tributário'...")
            camada_tributario = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Tributário']"))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", camada_tributario
            )
            self._click(camada_tributario)
            logger.info("Camada 'Tributário' selecionada")
            time.sleep(0.5)

            etapa = "abrir menu CTM GEO"
            logger.debug("Localizando container da camada 'Tributário'...")
            camada_tributario_container = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[text()='Tributário']/ancestor::div[contains(@class,'q-tree__node')]",
                    )
                )
            )
            more_vert_icons = camada_tributario_container.find_elements(
                By.XPATH,
                ".//i[@class='q-icon notranslate material-icons' and text()='more_vert']",
            )
            if len(more_vert_icons) >= 4:
                self._click(more_vert_icons[3])
                logger.info("Menu do item 'IPTU CTM GEO' aberto")
            else:
                logger.error(
                    "Não foi encontrado o quarto ícone 'more_vert' dentro da camada Tributário"
                )
                return False

            # Filtro
            etapa = "abrir filtro"
            logger.debug("Localizando botão 'Filtro'...")
            btn_filtro = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Filtro']"))
            )
            self._click(btn_filtro)
            logger.info("Filtro aberto")

            etapa = "selecionar opção de fazer filtro"
            btn_fazer_filtro = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span/i[contains(@class,'mdi-filter-plus')]")
                )
            )
            self._click(btn_fazer_filtro)
            logger.info("Opção de fazer filtro selecionada")

            etapa = "selecionar _INDICE_CADASTRAL"
            item_indice = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@class='q-item__label' and text()='_INDICE_CADASTRAL']",
                    )
                )
            )
            self._click(item_indice)
            logger.info("Item '_INDICE_CADASTRAL' selecionado")

            etapa = "inserir índice cadastral"
            campo_busca = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[@type='search' and contains(@aria-label,'Valor')]",
                    )
                )
            )
            campo_busca.clear()
            campo_busca.send_keys(indice_cadastral)
            logger.info("Índice cadastral inserido: %s", indice_cadastral)

            etapa = "aplicar filtro"
            btn_aplicar = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Aplicar']"))
            )
            self._click(btn_aplicar)
            logger.info("Filtro aplicado com sucesso")
            time.sleep(5)

            etapa = "fechar janela filtro"
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            logger.info("Janela do filtro fechada")
            time.sleep(5)

            etapa = "clique centro do mapa"
            self._clique_centro_mapa()

            etapa = "prints aéreos"
            self._prints_aereo()
            logger.info("Prints aéreos capturados")

            logger.info("Navegação concluída com sucesso")
            return True

        except Exception as e:
            logger.error(
                "Erro na etapa '%s': %s\n%s", etapa, repr(e), traceback.format_exc()
            )
            return False

    def _prints_aereo(self) -> None: 
        """
        Realiza a captura de tela do mapa em duas visualizações: Vetorial e Ortofoto.
        Salva os arquivos 'CTM_Aereo.png' e 'CTM_Orto.png' na pasta de download definida.
        
        :return: None.
        """
        
        # Print AEREO CTM
        time.sleep(15)
        screenshot_path = os.path.join(self.pasta_download, "CTM_Aereo.png")
        self.driver.save_screenshot(screenshot_path)
        logger.info("Print da tela salvo")

        # Clica no elemento "BHMap"
        elemento_bhmap = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@class='q-img__content absolute-full']//div[@class='titulo ellipsis' and text()='BHMap']",
                )
            )
        )
        self._click(elemento_bhmap)
        logger.info("Elemento 'BHMap' clicado")
        time.sleep(2)

        # Seleciona a ortofoto 2015
        elemento_ortofoto = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@class='q-img__content absolute-full']//div[contains(@class,'ellipsis') and text()='Ortofoto 2015']",
                )
            )
        )
        self._click(elemento_ortofoto)
        logger.info("Ortofoto selecionada")
        time.sleep(10)

        # Print AEREO ORTO
        screenshot_path_orto = os.path.join(self.pasta_download, "CTM_Orto.png")
        self.driver.save_screenshot(screenshot_path_orto)
        logger.info("Print da tela salvo")

        return

    def _clique_centro_mapa(self) -> None:
        """
        Clica no centro do mapa (elemento canva).
        """
        try:
            logger.info("Iniciando tentativa de clique no centro do mapa")

            # Tenta localizar o viewport do mapa
            viewport = self.driver.find_element(By.CSS_SELECTOR, "#olmap .ol-viewport")
            logger.info(
                f"Viewport encontrado: tamanho {viewport.size['width']}x{viewport.size['height']}"
            )

            # Cria a ação de mover e clicar
            action = ActionChains(self.driver)
            action.move_to_element(viewport).click().perform()
            logger.info("Clique no centro do mapa realizado")

            time.sleep(5)

        except NoSuchElementException as e:
            logger.error(f"Elemento do mapa não encontrado: {e}")
        except WebDriverException as e:
            logger.error(f"Erro ao executar clique no mapa: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao clicar no mapa: {e}")

    def capturar_areas(self) -> Dict[str, Optional[str]]:
        """
        Captura dados tabulares exibidos no painel lateral de Informações apósa seleção de um lote no mapa.
        A rotina garante previamente o foco no painel de Informações e realiza extrações independentes por bloco funcional, 
        permitindo falhas parciais sem comprometer a execução completa.

    Blocos processados de forma independente:
      - IPTU CTM GEO (áreas e dados cadastrais);
      - Endereço formatado a partir dos campos disponíveis;
      - Lote CP - ATIVO (área informada).
        
        :return: Dicionário contendo os dados extraídos (ou None, em caso de falha total):
                 - 'iptu_ctm_geo_area': Área do IPTU.
                 - 'iptu_ctm_geo_area_terreno': Área do terreno.
                 - 'endereco_ctmgeo': Endereço formatado completo.
                 - 'lote_cp_ativo_area_informada': Área informada do loteamento.
                 Retorna dicionário vazio em caso de erro crítico - Não encontrar o Painel Lateral.
        """
        resultado: Dict[str, Optional[str]] = {} # Dicionário que será retornado

        logger.info("Garantindo foco no painel de informações...")
        # Interage (encontra e clica) com o seletor da aba Informações - Isso garante o foco e visibilidade da tabela
        # Importante para triagem via IC e robustez geral.
        print(self._interact(nome_log="Aba Informações (sidebar)", #HACK: Tirar este rpint de DEBUG
            xpath=[
                # 1) Mais forte
                "//div[contains(@class,'q-item--clickable')]"
                "//i[contains(@class,'mdi-map-marker-question-outline')]"
                "/ancestor::div[contains(@class,'q-item')]",

                # 2) Ícone + subida
                "//i[contains(@class,'mdi-map-marker-question-outline')]"
                "/ancestor::div[contains(@class,'q-item')]",

                # 3) Role + classe funcional
                "//div[@role='listitem' and contains(@class,'q-item--clickable')]",
            ],
            css=[
                # 4) Fallback CSS
                "div.q-item--clickable i.mdi-map-marker-question-outline"
            ]
        ))

        # O seletor da interface atualizada (resolve o problema de captura de áreas falhando)
        PAINEL_SELETOR = "#q-app > div > div.q-drawer-container > aside > div > div.fit.row.no-scroll > div.col.bg-white > div > div.col.relative-position > div"

        try:
            painel = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, PAINEL_SELETOR))
            )
        except TimeoutException:
            logger.warning("ALERTA CRÍTICO: Painel lateral de Informações não encontrado após clique. Retornando vazio na ETAPA SISCTM.")
            return {} # Sai graciosamente sem quebrar o resto do código
                                   
        # Função auxiliar para ativar item
        def ativar_item(nome_item: str) -> Optional[object]:  # str -> Optional[object]
            try:
                item = painel.find_element(
                    By.XPATH,
                    f".//div[contains(@class,'q-item') and .//div[contains(text(),'{nome_item}')]]",
                )
                botao = item.find_element(By.XPATH, ".//div[@role='button']")
                aria = botao.get_attribute("aria-expanded")
                if aria != "true":
                    logger.info(f"{nome_item} não está ativo. Ativando...")
                    botao.click()   # XXX: TODO: migra para utilizar o _click() definido na classe - mais robusto 
                    WebDriverWait(botao, 5).until(
                        lambda x: x.get_attribute("aria-expanded") == "true"
                    )
                    logger.info(f"{nome_item} ativado")
                    time.sleep(3)
                else:
                    logger.info(f"{nome_item} já está ativo")
                return item
            except Exception as e:
                logger.info(
                    f"Erro ao ativar item {nome_item}: Camada {nome_item} não encontrada."
                )
                return None # Garante que a função aninhada sempre retorne algo (None se falhar)

        # ----------------------------------------------------------------------
        # BLOCO INDEPENDENTE:  IPTU CTM GEO (Processamento granular)
        # ----------------------------------------------------------------------
        iptu_item = ativar_item("IPTU CTM GEO")
        
        if iptu_item: 
            # 1.1 Captura Área Construída
            try:
                linha_area = WebDriverWait(iptu_item, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, ".//table//tr[td[contains(text(),'ÁREA')]]/td[2]")
                    )
                )
                valor = linha_area.text.strip()
                resultado["iptu_ctm_geo_area"] = valor
                logger.info(f"[SUCESSO] Área Construída (IPTU): {valor}")
            except TimeoutException:
                logger.warning("Não foi possível capturar área IPTU CTM GEO")
                resultado["iptu_ctm_geo_area"] = None

            # 1.2 Captura Área Terreno
            try:
                linha_area_terreno = WebDriverWait(iptu_item, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, ".//table//tr[td[contains(text(),'AREA_TERRENO')]]/td[2]")
                    )
                )
                valor = linha_area_terreno.text.strip()
                resultado["iptu_ctm_geo_area_terreno"] = valor
                logger.info(f"[SUCESSO] Área Terreno (IPTU): {valor}")
            except TimeoutException:
                logger.warning("Não foi possível capturar AREA TERRENO")
                resultado["iptu_ctm_geo_area_terreno"] = None

            # 1.3 Captura Campos do Endereço
            try:
                campos: Dict[str, str] = {
                    "tipo_logradouro": ".//table//tr[24]/td[2]",
                    "nome_logradouro": ".//table//tr[25]/td[2]",
                    "numero_imovel": ".//table//tr[26]/td[2]",
                    "complemento": ".//table//tr[27]/td[2]",
                    "cep": ".//table//tr[28]/td[2]",
                }

                valores: Dict[str, str] = {} 
                for chave, xpath in campos.items():
                    try:
                        elemento = WebDriverWait(iptu_item, 2).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        valores[chave] = elemento.text.strip()
                    except TimeoutException:
                        valores[chave] = ""

                # Tratamento: Remove pontos do número do imóvel
                valores["numero_imovel"] = valores["numero_imovel"].replace(".", "")

                # Monta o endereço no formato desejado
                endereco = f"{valores['tipo_logradouro']} {valores['nome_logradouro']}, {valores['numero_imovel']}"
                if valores["complemento"]:
                    endereco += f" {valores['complemento']}"
                endereco += f" - Belo Horizonte - MG, {valores['cep']}"

                resultado["endereco_ctmgeo"] = endereco
                logger.info(f"[SUCESSO] Endereço montado: {endereco}")

            except Exception as e:
                logger.warning(f"Não foi possível capturar endereço CTM GEO: {e}")
                resultado["endereco_ctmgeo"] = None
        else:
            logger.warning("IPTU CTM GEO não foi encontrado/ativado! Pulando captura de dados do grupo (IPTU).")


        # ----------------------------------------------------------------------
        # BLOCO INDEPENDENTE: Lote CP - ATIVO (Processamento independente)
        # ----------------------------------------------------------------------
        lote_cp_item = ativar_item("Lote CP - ATIVO")

        if lote_cp_item: 
            try:
                # Captura a tabela e todas as linhas
                tabela = lote_cp_item.find_element(By.TAG_NAME, "table")
                linhas: List[object] = tabela.find_elements(By.TAG_NAME, "tr") 
                
                # Validação: Captura a sexta linha (índice 5) onde deve estar a área
                if len(linhas) >= 6:
                    linha_area = linhas[5]
                    colunas: List[object] = linha_area.find_elements(By.TAG_NAME, "td") 
                    if len(colunas) >= 2:
                        valor: str = colunas[1].text.strip() 
                        resultado["lote_cp_ativo_area_informada"] = valor
                        logger.info(f"[SUCESSO] Área Lote CP: {valor}")
                    else:
                         logger.warning("Não foi possível encontrar a coluna de valor na linha de área.")
                         resultado["lote_cp_ativo_area_informada"] = None
                else:
                    logger.warning("Tabela Lote CP - ATIVO não possui linhas suficientes.")
                    resultado["lote_cp_ativo_area_informada"] = None
                    
            except Exception as e:
                logger.warning(f"Não foi possível capturar área Lote CP - ATIVO: {e}")
                resultado["lote_cp_ativo_area_informada"] = None
        else:
            logger.warning("Lote CP - ATIVO não foi encontrado/ativado, pulando captura de área.")

        return resultado