import os
import shutil
from datetime import datetime
from pipeline import processar_indice, processar_protocolo
from utils import logger, abrir_pasta, criar_pasta_resultados, log_path
from gui import iniciar_interface


def main():
    # função principal do orquestrador (definida dentro da main)
    def processar(credenciais, protocolos, cancelar_event, atualizar_progresso):
        # Cria pasta_resultados - neste método o momento 'agora' das Time Stamps são definidos
        # NOTE: a Time Stamp da pasta resultados será propagada para o início do Logger e demais coisas.
        pasta_resultados = criar_pasta_resultados()
        
        
        # Extrai o nome da pasta para usar no cabeçalho
        # Ex: "Resultados - 08 de janeiro de 2026 14h25"
        nome_pasta = os.path.basename(pasta_resultados)
        # Corta o que não é uma Time Stamp (legível) e fica só com o "08 de janeiro de 2026 14h25"
        timestamp_legivel = nome_pasta.replace("Resultados - ", "")

        # Escreve o cabeçalho do nosso LOG unificiado (arquivo e GUI)
        # NOTE: as 3 linhas de código acima são executadas para garantir 100% de coerência e sincronia entre o arquivo LOG.txt e o nome da pasta 'Resultados - <...>'
        logger.info(f"===== Triagem iniciada em {timestamp_legivel} ====")
        
        # --- Formata a lista para ficar mais legível [sem colchetes nem áspas simples] -----
        # Quebra a lista em pedaços (chunks) de 3 itens
        chunks = [protocolos[i:i + 3] for i in range(0, len(protocolos), 3)]
        # Junta com quebra de linha e identação visual
        lista_formatada = "\n ".join([", ".join(chunk) for chunk in chunks])
        logger.info(f"Protocolos identificados ({len(protocolos)}):\n {lista_formatada}")
        
        logger.info("==========================================================\n\n")

        count_protocol = 0
        count_IC = 0
        inicio_exec = datetime.now()
        try:
            for i, protocolo in enumerate(protocolos, 1):
                # No Log que avisa "Relatório Gerado\n\n" (em pipeline/process.py) já há um respiro de dois breaklines
                # ao fim do processamento e geração do relatóri de cada protocolo.

                # string do Separador visual (poderia ser uma funçaõ do tamanho da tela mas... )
                # Também define o titulo.center( len(separador) ), logo abaixo    
                separador: str = "=" * 50 
                
                # Mensagem com contagem (Ex: 6/9) para noção de progresso
                titulo = f"▶ INICIANDO PROTOCOLO {i}/{len(protocolos)}: {protocolo}"

                # Loga o bloco formatado
                logger.info(separador)
                logger.info(titulo.center( len(separador) )) # .center() centraliza o texto na linha (de acordo com o tamanho separador)
                logger.info(separador + "\n")
                # ---------------------------------

                if cancelar_event.is_set():
                    logger.info("Processamento cancelado pelo usuário.")
                    break

                count_protocol += 1
                protocolo_normalizado = (
                    protocolo.replace("-", "").replace("/", "").replace(".", "")
                )

                try:
                    indices = processar_protocolo(
                        protocolo_normalizado, credenciais, pasta_resultados
                    )
                except Exception as e:
                    logger.error(f"Erro no protocolo {protocolo}: {e}")
                    indices = []

                if indices:
                    for indice in indices:
                        if cancelar_event.is_set():
                            break
                        count_IC += 1
                        indice_normalizado = indice.replace("-", "")
                        try:
                            processar_indice(
                                indice_normalizado,
                                credenciais,
                                protocolo,
                                pasta_resultados,
                            )
                        except Exception as e:
                            logger.error(f"Erro no índice {indice}: {e}")

                atualizar_progresso(i)

            if not cancelar_event.is_set():
                if os.path.exists(pasta_resultados):
                    logger.info(f"\nAbrindo pasta de resultados: {pasta_resultados}")
                    abrir_pasta(pasta_resultados)
                else:
                    logger.warning(
                        f"Pasta de resultados não encontrada: {pasta_resultados}"
                    )

        except Exception as e:
            logger.error(f"Erro crítico: {e}")

        finally:
            duracao = datetime.now() - inicio_exec
            minutos, segundos = divmod(duracao.total_seconds(), 60)
            logger.info(f"Protocolos processados: {count_protocol}")
            logger.info(f"ICs processados: {count_IC}")
            logger.info(f"Tempo: {int(minutos)} min {int(segundos)} seg")
            # --- Persistência do Arquivo de LOG (enviado pra pasta de Resultados) ---
            if os.path.exists(pasta_resultados) and log_path.exists():
                # LOGS NESTE BLOCO NÃO VÃO PARA O ARQUIVO COPIADO -  pois são apenas sobre sucesso do copiar>colar>renomear
                try:
                    # Pega o nome da pasta para manter o timestamp sincronizado
                    nome_pasta = os.path.basename(pasta_resultados)
                    # Str do novo nome do arquivo na pasta Resultados - ex: "Detalhes da Triagem - xx de Onzeiro de 2099 16h20.txt"
                    novo_nome = f"Detalhes da Triagem - {nome_pasta.replace('Resultados - ', '')}.txt"
                    
                    destino = os.path.join(pasta_resultados, novo_nome)
                    # Usa shutil.copy() para fazer uma cópia do arquivo na pasta raíz pra pasta destino (Resultados - ...)
                    shutil.copy(log_path, destino)
                    logger.info(f"Log persistente salvo na pasta de Resultados:\n{destino}")
                except Exception as e:
                    logger.error(f"Erro ao salvar cópia do log persistente na pasta destino:\n({destino})\n{e}")
            # -----------------------------------------------
            root.after(0, resetar_interface) # A main (não interface.py) está resetando a interface
            # Reseta a interface DEPOIS de tentar mover o log pra past de Resultados

    root, resetar_interface, _ = iniciar_interface(processar)
    root.mainloop()


if __name__ == "__main__":
    main()
