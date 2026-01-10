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


"""
HACK:===============================================================================
HACK:       🛡️ MÓDULO COM SIGEDE INTERCEPTOR (MAN-IN-THE-MIDDLE)
HACK:===============================================================================
Este arquivo é um substituto temporário para 'app/pipeline/process.py'.
Use-o quando precisar processar ÍNDICES de protocolos que não existem no SIGEDE ou 
que está inacessível, mas cujo Índice Cadastral (IC) podemos ter acesso.

COMO USAR:
1. Edite a seção 'CONFIGURAÇÃO DO BYPASS' abaixo.
2. Faça backup do 'app/pipeline/process.py' original.
3. Substitua o conteúdo de 'process.py' por este código.
4. Rode a automação.
5. Restaure o arquivo original.
===============================================================================
"""

# =============================================================================
# 🛠️ CONFIGURAÇÃO DO BYPASS (Edite aqui)
# =============================================================================

# O "Gatilho": Parte do número ou texto que identifica o protocolo fantasma.
# O script vai procurar se ESSA string existe no que você digitou na interface.
# Se não existir, o programa seguirá normalmente sem alterações. 
# Se existir o fluxo do módulo SIGEDE será sequestrado e os ICs injetados manualmente via lista abaixo.
GHOST_PROTOCOL = "3100337504202503" 

# A "Carga Útil": A lista de Índices Cadastrais (ICs) que deve ser retornada.
# O sistema vai achar que o SIGEDE encontrou esses índices e seguirá normalmente fazendo a traigem dos índices
LISTA_ICS_INJEÇÃO = ["981142W0020015"] 

# =============================================================================
# Lembrando que essa é uma HACKED VERSION da função de processar protocolos (não a standard)
def processar_protocolo(protocolo: str, credenciais: Dict[str, str], pasta_resultados: str) -> List[str]:
    """
    HACK: Execução do módulo SIGEDE com capacidade de INTERCEPTAÇÃO MANUAL para triagem de ICs específicos.
    """
    
    # 1. Preparação do Ambiente (Pasta)
    # Sanitiza o nome para criar a pasta (aceita colchetes, underline, etc)
    nome_pasta_seguro = protocolo.replace("/", "-").replace("\\", "-").replace(":", "")
    pasta_protocolo = os.path.join(pasta_resultados, nome_pasta_seguro)
    os.makedirs(pasta_protocolo, exist_ok=True)

    # 2. Lógica de Interceptação (O "Man-in-the-Middle")
    # Limpa a entrada para comparação (remove pontuação padrão)
    protocolo_limpo = protocolo.replace(".", "").replace("-", "").replace("/", "")
    
    # Verifica se o gatilho está presente na string limpa
    if GHOST_PROTOCOL in protocolo_limpo:
        logger.warning(f"HACK: 🚨 [MITM DETECTADO] Protocolo '{protocolo}' interceptado pelo script de Bypass.")
        logger.warning(f"HACK: ⚠️  O acesso ao SIGEDE será emulado. Injetando os seguintes ÍNDICES Manualmente: {LISTA_ICS_INJEÇÃO}")
        
        # Gera evidência de auditoria (para você saber no futuro o que aconteceu)
        arquivo_aviso = os.path.join(pasta_protocolo, "_RELATORIO_INTERVENCAO_MANUAL.txt")
        with open(arquivo_aviso, "w", encoding="utf-8") as f:
            f.write("=========================================================\n")
            f.write("       RELATÓRIO DE INTERVENÇÃO MANUAL (BYPASS)\n")
            f.write("=========================================================\n\n")
            f.write(f"Protocolo Solicitado: {protocolo}\n")
            f.write(f"Motivo: Protocolo inacessível/fantasma no SIGEDE.\n")
            f.write(f"Ação: O módulo SIGEDE foi ignorado via script 'process_mitm[HACK].py' (geralmente guardado na pasta misc do repositório).\n")
            f.write(f"Dados Injetados (ICs): {LISTA_ICS_INJEÇÃO}\n")
            f.write("\nEste processo gerou documentos baseados estritamente nos ICs acima.\n")

        # Retorna a carga útil manual (bypassando o robô real)
        return LISTA_ICS_INJEÇÃO

    # =========================================================================
    # 3. Fluxo Normal (Para todos os outros protocolos)
    # =========================================================================
    logger.info(f"Processando protocolo {protocolo} via fluxo normal (SIGEDE)...")
    
    # Instancia e roda o robô real
    sigede_bot = Sigede()
    indices_encontrados = sigede_bot.executar(protocolo, credenciais, pasta_protocolo)
    
    return indices_encontrados

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
    logger.info(f"Relatório gerado!\n\n")
