import os
import shutil
from datetime import datetime
from pipeline import processar_indice, processar_protocolo
from utils import logger, log_path, section_log, abrir_pasta, criar_pasta_resultados
from gui import iniciar_interface


def main():

    # função aninhada principal do orquestrador (definida dentro da main)
    def processar(credenciais, protocolos, ics_avulsos, cancelar_event, atualizar_progresso_gui, atualizar_status_gui ):

        # Cria pasta_resultados - neste método o momento 'agora' das Time Stamps são definidos
        # NOTE: a Time Stamp da pasta resultados será propagada para o início do Logger e demais coisas.
        pasta_resultados = criar_pasta_resultados()
        
        
        # Extrai o nome da pasta para usar no cabeçalho
        # Ex: "Resultados - 08 de janeiro de 2026 14h25"
        nome_pasta = os.path.basename(pasta_resultados)
        # Corta o que não é uma Time Stamp (legível) e fica só com o "08 de janeiro de 2026 14h25"
        timestamp_legivel = nome_pasta.replace("Resultados - ", "")
         # NOTE: as 3 linhas de código acima são executadas para garantir 100% de coerência e sincronia entre o arquivo LOG.txt e o nome da pasta 'Resultados - <...>'

        # Escreve o cabeçalho do LOG unificiado (arquivo e GUI)
        # TODO: Modificar os separadores hardcoded para usar a função section_log() definida em logger.py
        logger.info(f"===== Triagem iniciada em {timestamp_legivel} ====")
        
        # --- Formata a lista  de PROTOCOLOS para ficar mais legível [sem colchetes nem áspas simples] -----
        # Quebra a lista em pedaços (chunks) de 3 itens
        chunks = [protocolos[i:i + 3] for i in range(0, len(protocolos), 3)]
        # Junta com quebra de linha, recuo (tabulação) e identação visual de 3 em 3 PROTOCOLOS (por linha)
        lista_formatada = "\n ".join([f"\t{', '.join(chunk)}" for chunk in chunks])
        logger.info(f"PROTOCOLOS identificados p/ triagem    ({len(protocolos)}):\n{lista_formatada}")

        # Loga os ÍNDICES CADASTRAIS avulsos se houver
        if ics_avulsos:
            # Reutiliza variáveis e lista usada em protocolos
            chunks = [ics_avulsos[i:i + 3] for i in range(0, len(ics_avulsos), 3)]
            # Junta com quebra de linha, recuo (tabulação) e identação visual de 3 em 3 ICs (por linha)
            lista_formatada = "\n ".join([f"\t{', '.join(chunk)}" for chunk in chunks])
            logger.info(f"ÍNDICES CADASTRAIS (avulsos) identificados para trigeem    ({len(ics_avulsos)}):\n{lista_formatada}")
        
        logger.info("==========================================================\n\n")

        count_protocol = 0
        count_IC = 0
        inicio_exec = datetime.now()

        # Instancia a fila de trabalho que conterá protocolos reais e um protocolo virtual (para triagem de ICs)
        process_queue = []  # process_queue é uma lista de dicts (lista de dicionários de protocolo)

        # ID do protocolo virtual que encapsula os ICs avulsos na traigem
        ID_ICs: str = "Triagem por ICs"   # Determina o nome da pasta de triagem de ICs
                            

        # ------ Prenchimento da fila de trabalho, process_queue, com os dicts de protocolos: ------

        '''Todo protocolo será representado por um dict com chaves:
                'tipo'          (str):              'REAL' / 'VIRTUAL' 
                'id'            (str):              'número' / 'nome' - Identificação do protocolo (p/ estrutura de pastas) 
                'ics_a_priori'  (str list / None):  A Lista de ICs se já sabemos à priori (protocolo Virtual) 
                                                    ou None (protocolos reais)

        NOTE:   Protocolos Reais não possuem lista de ICs associados à priori (Isso é descoberto na etapa SIGEDE).
                Intencionalmente temos APENAS UM protocolo virtual, que encapsula todo os ICs avulsos à serem triados. 
                O campo 'id' determina o nome da pasta onde os protocolos / ICs avulsos são salvos.     '''


        for p in protocolos:                        # Add os dicts de protocolos (reais)
            process_queue.append({
                'tipo': 'REAL',                     # Requer SIGEDE (para determianr os ICs associados ao protocolo)
                'id': p,                            # Número do protocolo
                'ics_a_priori': None                # Não sabemos os índices cadastrais ainda
            })

        
        if ics_avulsos:                         # Add os ICs avulsos no protocolo virtual
            process_queue.append({
                'tipo': 'VIRTUAL',                   # Pula SIGEDE
                'id': ID_ICs,                       # Nome da pasta (Protocolo Virtual)
                'ics_a_priori': ics_avulsos        # Já temos a lista de ICs! (conseguida do campo de triagem de ICs na interface
            })

        total_tarefas = len(process_queue)

        try:
            # Usa enumarate para tornar 'protocolos' iterável. o '1' indica indexação partindo de 1 (não zero)
            # i: mero indexador (one-based); task: place holder p/ os dicts de protocolos em process_queue
            for i, task in enumerate(process_queue, 1):

                # Extrai dados da task (protocolo) atual
                id_atual = task['id']                   # Ex: "700..." ou "TRIAGEM_AVULSA"
                tipo = task['tipo']                     # protocolo "REAL" ou "VIRTUAL" ?
                lista_ic_prot = task['ics_a_priori']    # None ou uma lista de ICs (strings)


                if tipo == 'REAL':
                    titulo_log = f"▶ INICIANDO ETAPA {i}/{total_tarefas}. PROTOCOLO: {id_atual}"
                    titulo_status = f"▶ ETAPA {i}/{total_tarefas}:  PROTOCOLO:  {id_atual} ◀"
                    msg_status = f"{titulo_status}\nSIGEDE" # Avisa que vai rodar Sigede pro protocolo
                else:
                    titulo_log = f"▶ INICIANDO ETAPA {i}/{total_tarefas}.  {len(task['ics_a_priori'])} ICs"
                    titulo_status = f"▶  ETAPA  {i}/{total_tarefas}:  IC:  {id_atual}  ◀"
                    msg_status = f"{titulo_status}\nIniciando..." # Não roda Sigede


                # NOTE: No Log que avisa "Relatório Gerado\n\n" (em pipeline/process.py) já há um respiro de dois breaklines
                # ao fim do processamento e geração do relatório de cada protocolo.

                # NOTE: string do Separador visual (poderia ser uma funçaõ do tamanho da tela mas... )
                # Também define a média para o titulo.center( len(separador) ), logo abaixo    
                separador: str = "=" * 55 
                
                # Atualiza StatusText e Loga o bloco formatado do início do processamento de um novo protocolo
                atualizar_status_gui(msg_status)
                logger.info(separador)
                logger.info(titulo_log.center( len(separador) )) # .center() centraliza o texto na linha (de acordo com o tamanho separador)
                logger.info(separador + "\n")
                # ---------------------------------

                if cancelar_event.is_set():
                    logger.info("Processamento cancelado pelo usuário.")
                    break
                
                # Normaliza a string do protocolo (tira '-' , '/' e '.')
                protocolo_normalizado = (id_atual.replace("-", "").replace("/", "").replace(".", ""))
                count_protocol += 1     # utilizado no bloco finally (não é redundante com o i [index do for])
                                        # TODO: O LOG e count protocol não reflete o nº de prot bem sucedidos
                                        # Uma terceria variável de controle e contagem após o sucesso do SIGEDE
                
                '''# Tupla de informação sobre o estado do processamento de protocolos
                protCountTuple = (i, len(protocolos) )  # O progresso do processamento (Atual, Total)'''
                indices_para_processar = []

                try:
                    if tipo == 'REAL':  # Se é um protocolo REAL
                        # Normaliza e processa (chama SIGEDE p/ obter índices e criar pastas)
                        proto_normalizado = id_atual.replace("-", "").replace("/", "").replace(".", "")
                        indices_para_processar = processar_protocolo(proto_normalizado, credenciais, pasta_resultados)
                    
                    else:               # Se é um protocolo VIRTUAL (triagem por índices)
                        indices_para_processar = task['ics_a_priori']     # Associa índices ao protocolo virtual
                        
                        # Cria a pasta manualmente, já que a etapa de obtenção de índices (SIGEDE) não vai rodar e criar
                        # O nome da pasta para para triagem por IC, referenciado por 'id_atual' é definido acima na str ID_ICs
                        caminho_pasta_virtual = os.path.join(pasta_resultados, id_atual)
                        os.makedirs(caminho_pasta_virtual, exist_ok=True)
                        logger.info(f"Triagem de Lote avulso de ICs. {len(indices_para_processar)} índices foram fornecidos manualmente.")

                except Exception as e:
                    logger.error(f"Erro na etapa de obtenção de índices para {id_atual}: {e}")
                    indices_para_processar = []

                # Processamento dos Índices daquele Protocolo
                if indices_para_processar:
                    total_ics = len(indices_para_processar)
                    j: int = 1 # se tem índices, tem pelo menos 1 (j é nosso índice de índices usado no log ^^)
                    for indice in indices_para_processar:
                        if cancelar_event.is_set():
                            break
                        count_IC += 1
                        indice_normalizado = indice.replace("-", "")
                        try:
                            
                            section_log(f"[ Indice: {indice} ({j}/{total_ics}) ] ",'_') # Adiciona seção SIATU pra cada índice nos LOGS
                            VIRTUAL_PRTCL: bool = (task['tipo'] != 'REAL')              # True se protocolo VIRTUAL' (False qdo 'REAL')
                            
                            # Define o um status dinâmico para o Status Text - Ex: "ETAPA 1/2: 700... ◀ [IC 1/5]"
                            status_dinamico = f"{titulo_status}\n[IC {j}/{total_ics}]" # Ex: "ETAPA 1/2: 700... ◀ [IC 1/5]"
                            
                            processar_indice(
                                indice_normalizado,
                                credenciais,
                                id_atual,
                                pasta_resultados,
                                status_title=status_dinamico,            # Passa  status_dinamico no 'status_title' para maior granularidade
                                statusUpdater=atualizar_status_gui,       # Método para atualizar o status da gui (um método da classe InterfaceApp)
                                VIRTUAL_PRTCL=VIRTUAL_PRTCL,              # O IC atual está num protocolo Virtual?         
                            )
                            j += 1      # incrementa o contador de ICs (Index de índices ^^)
                            
                        except Exception as e:
                            logger.error(f"Erro no índice {indice}: {e}")

                atualizar_progresso_gui(i)

            if not cancelar_event.is_set():
                if os.path.exists(pasta_resultados):
                    logger.info(f"\nAbrindo pasta de resultados: {pasta_resultados}")
                    abrir_pasta(pasta_resultados)
                else:
                    logger.warning(
                        f"Pasta de resultados não encontrada: {pasta_resultados}"
                    )

        except Exception as e:
            logger.error(f"Erro crítico no loop de triagem principal: {e}")

        finally:
            duracao = datetime.now() - inicio_exec
            minutos, segundos = divmod(duracao.total_seconds(), 60)
            logger.info(f"Protocolos processados: {count_protocol}")
            logger.info(f"ICs processados: {count_IC}")
            logger.info(f"Tempo: {int(minutos)} min {int(segundos)} seg")
            # --- Persistência do Arquivo de LOG (enviado pra pasta de Resultados) ---
            if os.path.exists(pasta_resultados) and log_path.exists():
                # OS LOGS NESTE BLOCO TRY ABAIXO NÃO VÃO PARA O ARQUIVO COPIADO -  pois são apenas sobre sucesso do copiar>colar>renomear
                try:
                    # Pega o nome da pasta para manter o timestamp sincronizado
                    nome_pasta = os.path.basename(pasta_resultados)
                    # Str do novo nome do arquivo na pasta Resultados - ex: "Detalhes da Triagem - xx de Onzeiro de 2099 16h20.txt"
                    novo_nome = f"Detalhes da Triagem - {nome_pasta.replace('Resultados - ', '')}.txt"
                    
                    destino = os.path.join(pasta_resultados, novo_nome)
                    # Usa shutil.copy() para fazer uma cópia do arquivo na pasta raíz pra pasta destino (Resultados - ...)
                    shutil.copy(log_path, destino)
                    logger.info(f"Log persistente salvo na pasta de Resultados:\n{destino}\n\n")
                except Exception as e:
                    logger.error(f"Erro ao salvar cópia do log persistente na pasta destino:\n({destino})\n{e}\n\n")
            # -----------------------------------------------
            root.after(0, resetar_interface) # A main está resetando a interface (não interface.py)
            # Reseta a interface DEPOIS de mover o log pra past de Resultados

    root, resetar_interface, _ = iniciar_interface(processar)
    root.mainloop()


if __name__ == "__main__":
    main()
