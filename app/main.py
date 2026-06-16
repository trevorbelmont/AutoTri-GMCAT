import logging
import os
import shutil
from datetime import datetime
from pipeline import processar_indice, processar_protocolo
from utils import logger, log_path, section_log, reset_log_file, lot_logger_config
from utils import settings, CredentialManager
from utils import abrir_pasta, criar_pasta_resultados
from gui import iniciar_interface

def main():

    
    # função aninhada principal do orquestrador
    def processar(credenciais, protocolos, ics_avulsos, cancelar_event, atualizar_progresso_gui, atualizar_status_gui, iniciar_timer ):

        reset_log_file()

        pasta_resultados = criar_pasta_resultados()
        lot_logger_config(pasta_resultados,settings.LOT_DEBUGGER)
        
        lvl = logging.WARNING if settings.LOT_DEBUGGER else logging.INFO

        nome_pasta = os.path.basename(pasta_resultados)
        timestamp_legivel = nome_pasta.replace("Resultados - ", "")

        logger.debug("\n\n")
        section_log(f" Triagem iniciada em {timestamp_legivel} ",'=',60)
        logger.info(f"v. {root.title()}")
        
        
        chunks = [protocolos[i:i + 3] for i in range(0, len(protocolos), 3)]
        lista_formatada = "\n ".join([f"\t\t{', '.join(chunk)}" for chunk in chunks])
        logger.info(f"PROTOCOLOS identificados p/ triagem    ({len(protocolos)}):\n{lista_formatada}")

        if ics_avulsos:
            chunks = [ics_avulsos[i:i + 3] for i in range(0, len(ics_avulsos), 3)]
            lista_formatada = "\n ".join([f"\t\t{', '.join(chunk)}" for chunk in chunks])
            logger.info(f"ICs (avulsos) identificados para trigem    ({len(ics_avulsos)}):\n{lista_formatada}") 
        section_log("",'=',60, addEndLines=2)
        
        count_protocol = 0
        count_IC = 0
        inicio_exec = datetime.now()

        # CÁLCULO SIMPLES DE TEMPO ESTIMADO (em segs)
        MEDIA_PROTOCOLO = 295
        MEDIA_IC_AVULSO = 260
        
        qtd_prot = len(protocolos)
        qtd_avulsos = len(ics_avulsos) if ics_avulsos else 0
        margem_estimativa = 68
        tempo_total_estimado = (qtd_prot * MEDIA_PROTOCOLO) + (qtd_avulsos * MEDIA_IC_AVULSO) + margem_estimativa
        iniciar_timer(tempo_total_estimado)

        process_queue = []
        # ID do protocolo virtual que encapsula os ICs avulsos na traigem
        ID_ICs: str = "Triagem por ICs"
                            
        for p in protocolos:
            process_queue.append({
                'tipo': 'REAL',
                'id': p,
                'ics_a_priori': None
            })
        
        if ics_avulsos:
            process_queue.append({
                'tipo': 'VIRTUAL',
                'id': ID_ICs,
                'ics_a_priori': ics_avulsos
            })

        total_etapas: int = len(process_queue)
        total_tarefas = len(protocolos) + len(ics_avulsos)
        progressBarDict = {}
        progressBarDict["peso_tarefa"]= 100.0/(total_tarefas)
        progressBarDict["atual"] = 0.0
        progressBarDict["n_cadastrais_associados"] = 1
        
        try:
            for i, task in enumerate(process_queue, 1):

                # Extrai dados da task (protocolo) atual
                id_atual = task['id']
                tipo = task['tipo']
                lista_ic_prot = task['ics_a_priori']


                if tipo == 'REAL':
                    titulo_log = f"▶ INICIANDO ETAPA {i}/{total_etapas}. PROTOCOLO: {id_atual}"
                    titulo_status = f"▶ ETAPA {i}/{total_etapas}:  PROTOCOLO:  {id_atual} ◀"
                    msg_status = f"{titulo_status}\nSIGEDE"
                else:
                    titulo_log = f"▶ INICIANDO ETAPA {i}/{total_etapas}.  {len(task['ics_a_priori'])} ICs"
                    titulo_status = f"▶  ETAPA  {i}/{total_etapas}:  IC:  {id_atual}  ◀"
                    msg_status = f"{titulo_status}\nIniciando..."

                
                separador: str = "=" * 55 
                atualizar_status_gui(msg_status)
                logger.log(lvl,f"{separador}")
                logger.log(lvl, f"{titulo_log.center( len(separador) )}") 
                logger.log(lvl, f"{separador}" + "\n")

                if cancelar_event.is_set():
                    logger.info("Processamento cancelado pelo usuário.")
                    break
                
                protocolo_normalizado = (id_atual.replace("-", "").replace("/", "").replace(".", ""))
                count_protocol += 1
                indices_para_processar = []

                try:
                    if tipo == 'REAL':
                        proto_normalizado = id_atual.replace("-", "").replace("/", "").replace(".", "")
                        indices_para_processar = processar_protocolo(proto_normalizado, credenciais, pasta_resultados)
                        progressBarDict["atual"] += progressBarDict["peso_tarefa"]*0.1
                        atualizar_progresso_gui(progressBarDict["atual"])
                        progressBarDict["n_cadastrais_associados"] = len(indices_para_processar)

                    else:
                        indices_para_processar = task['ics_a_priori']
                        progressBarDict["n_cadastrais_associados"] = len(indices_para_processar)
        
                        caminho_pasta_virtual = os.path.join(pasta_resultados, id_atual)
                        os.makedirs(caminho_pasta_virtual, exist_ok=True)
                        logger.info(f"Triagem de Lote avulso de ICs. {len(indices_para_processar)} índices foram fornecidos manualmente.")

                except Exception as e:
                    logger.error(f"Erro na etapa de obtenção de índices para {id_atual}: {e}")
                    indices_para_processar = []

                # Processamento dos Índices daquele Protocolo (Virtual ou Real)
                if indices_para_processar:
                    total_ics = len(indices_para_processar)
                    j: int = 1
                    for indice in indices_para_processar:
                        if cancelar_event.is_set():
                            break
                        count_IC += 1
                        indice_normalizado = indice.replace("-", "")
                        try:
                            
                            section_log(f"[ Indice: {indice} ({j}/{total_ics}) ] ",'_')
                            VIRTUAL_PRTCL: bool = (task['tipo'] != 'REAL') 
                            
                            # Define o um status dinâmico para o Status Text - Ex: "ETAPA 1/2: <protocol> ◀ [IC j/5]"
                            status_dinamico = f"{titulo_status}\n[IC {j}/{total_ics}]"
                            
                            processar_indice(
                                indice_normalizado,
                                credenciais,
                                id_atual,
                                pasta_resultados,
                                status_title=status_dinamico,
                                statusUpdater=atualizar_status_gui,
                                progressBarUpdater = atualizar_progresso_gui,
                                progressBarDict= progressBarDict,
                                VIRTUAL_PRTCL=VIRTUAL_PRTCL,    
                            )
                            j += 1
                            
                        except Exception as e:
                            logger.error(f"Erro no índice {indice}: {e}")
                        
                elif not indices_para_processar:
                    progressBarDict["atual"] += progressBarDict["peso_tarefa"]*0.9


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
            final_log_total_protocol = count_protocol if not ics_avulsos else count_protocol-1
            logger.info(f"Protocolos processados: {final_log_total_protocol}")
            logger.info(f"ICs processados: {count_IC}")
            logger.info(f"Tempo: {int(minutos)} min {int(segundos)} seg")
            if progressBarDict["atual"] != 100.0:
                progressBarDict["atual"] = 100.0
                atualizar_progresso_gui(progressBarDict['atual'])
            
            # --- Persistência do Arquivo de LOG (enviado pra pasta de Resultados) ---
            if os.path.exists(pasta_resultados) and log_path.exists():
                try:
                    nome_pasta = os.path.basename(pasta_resultados)
                    novo_nome = f"Detalhes da Triagem - {nome_pasta.replace('Resultados - ', '')}.txt"
                    
                    destino = os.path.join(pasta_resultados, novo_nome)
                    # Usa shutil.copy() para fazer uma cópia do arquivo na pasta raíz pra pasta destino (Resultados - ...)
                    shutil.copy(log_path, destino)
                    logger.info(f"Log persistente salvo na pasta de Resultados:\n{destino}\n\n")
                except Exception as e:
                    logger.error(f"Erro ao salvar cópia do log persistente na pasta destino:\n({destino})\n{e}\n\n")
            
            
            root.after(0, resetar_interface)

    settings.setup()
    with CredentialManager.session_manager() as creds_iniciais:
        root, resetar_interface, _, iniciar_timer = iniciar_interface(processar, creds_iniciais)
        del creds_iniciais

    root.mainloop()


if __name__ == "__main__":
    main()
