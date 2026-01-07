import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import os
from utils import logger, log_queue


class InterfaceApp:
    def __init__(self, processar_callback):
        self.processar_callback = processar_callback
        self.root = tk.Tk()
        self.root.title("Automação de Triagem")
        
        # Estado da Aplicação
        self.credenciais = {}
        self.protocolos = []
        self.cancelar_event = threading.Event()
        
        # Inicializa a Interface
        self._configurar_widgets()
        self._iniciar_leitura_logs()


#==================================== INÍCIO DA DEFINIÇÃO DE LAYOUT =================================================================

    def _configurar_widgets(self):
        """Define todo o layout e widgets da janela."""

        # --- Configuração de Responsividade das Colunads da Interface ---
        self.root.geometry("550x550") 
        self.root.minsize(500, 400)   
            
        self.root.grid_columnconfigure(0, weight=0)     # Coluna 0 (Labels):    Peso 0: Tamanho fixo, não cresce.
        self.root.grid_columnconfigure(1, weight=1)     # Coluna 1 (Inputs):    Peso 1 : Cresce e ocupa todo o espaço horizontal sobrando)
            
        self.root.grid_rowconfigure(10, weight=1)       # Linha 10 (LOG):       Peso 1: É a última linha. Se ajusta à margem Sul.
        
        # NOTE: Na definição dos grids dos tk.Labels(...).grid(...) e tk.Entry().grid(...) e etc... 
        # usaremos stick="w" (West/Esquerda) e stick="e" (East/Direita) para "colar" os widgets nas margens.

        # --- Credenciais ---
        '''     >>> Widgets: tkinter.Label(...) e tkinter.Entry(...) - Elementos da tkinter padrão:

        Cria uma Label na janela principal (self.root) com  texto "Usuário SIGEDE". Sem o grid (...) a label existe apenas na RAM, mas não é desenhada
        Grid(): posiciona e renderiza a label na devida posição; stick = "w" (west): alinhamento à marge Oeste/Esquerda; padx/padx = respiro (pra não colar nas bordas)'''
        tk.Label(self.root, text="Usuário SIGEDE:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        '''Cria um campo de entrada na janela principal (self.root) de largura 30.
        É importante observar que estes campos de ENTRADA são criado pertencendo a self (ao objeto da Classe InterfaceApp).
        Isso é especialmente importante pois precisaremos referenciá-los para extrair a string que o usuário escrever neles -
        - a extração ocorrerá na função _acao_confirmar(). Neste caso assim: " self.credenciais["usuario"] = self.entry_usuario.get()"'''
        self.entry_usuario_sigede = tk.Entry(self.root, width=30)
        
        '''Posiciona e desenha o campo de entrada usando .grid(...) - usa stick="e": alinhando o campo à margem Direita.
            Os outros widgets seguem similarmente ao primeiro.'''
        self.entry_usuario_sigede.grid(row=0, column=1, sticky='e', padx=5, pady=5)

        tk.Label(self.root, text="Senha SIGEDE:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_senha_sigede = tk.Entry(self.root, show="*", width=30)
        self.entry_senha_sigede.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        
        tk.Label(self.root, text="Usuário SIATU:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_usuario = tk.Entry(self.root, width = 30)
        self.entry_usuario.grid(row=2, column=1, sticky='e', padx=5, pady=5)

        tk.Label(self.root, text="Senha SIATU:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_senha = tk.Entry(self.root, show="*", width=30)
        self.entry_senha.grid(row=3, column=1, sticky='e', padx=5, pady=5)

        # --- Primeiro Separador (Protocolos e Botões)---
        # sticky="ew": Estica de ponta a ponta
        ttk.Separator(self.root, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)

        # --------------------------------------- Protocolos ---------------------------------------
        '''     >>> Widget: tkinter.scrolledtext.ScrolledText() - Elemento NÃO NATIVO, presente no módulo tkinter.scrolledtext
        Parâmetros Críticos:
        - width=x, height=y: Definem o tamanho do campo (em caracteres).
        - self.root: é o master (a que janela este widget pertence.) Neste caso self.root é a janela principal (e única).
        !!! Como é um espaço para texto que será extraído mais tarde (não pode ser perdido),
            atribuímos ele como uma variável do objeto self e depois posicionamos 
            e renderizamos o widget com o .grid(...), NORMALMENTE.
        '''
        tk.Label(self.root,
                 text=  "Protocolo(s):\n(Separados por ESPAÇO ou VÍRGULAS)\n\n"
                        "Ex. 7463527921,48302891,700675062505)",
                 justify="left",        #Justifica label à esquerda
                 ).grid(row=5, column=0, stick="nw", padx=5, pady=0)
        # wrap=tk.WORD : Define para que palavras (protocolos), separados por vírgula e espaço, 
        # não sejam visual partidos no meio na quebra de linha.
        self.entry_protocolos = tk.scrolledtext.ScrolledText(self.root, height=4,  width=30, wrap=tk.WORD)
        self.entry_protocolos.grid(row=5, column=1, stick= "nsew", padx=5, pady=5)


        # --------------------------------------- Botões ---------------------------------------
        '''     >>> Widget: tkinter.Button() - Elemento interativo padrão:

        Parâmetros Críticos:
        - command=self._acao_confirmar: Passagem de Referência (Callback).
        !!! ATENÇÃO: Passamos o nome da função SEM parênteses '()'. 
          Se usássemos 'command=self.func()', o Python executaria a função IMEDIATAMENTE 
          durante a criação da janela, e atribuiria o retorno (None) ao botão.
          Queremos passar o endereço da função para ser chamada apenas no evento 'click'.
        '''
        self.btn_confirmar = tk.Button(self.root, text="Iniciar", command=self._acao_confirmar)
        self.btn_confirmar.grid(row=6, column=0, sticky="ew", padx=5, pady=3)

        self.btn_cancelar = tk.Button(self.root, text="Cancelar", command=self._acao_cancelar, state="disabled")
        self.btn_cancelar.grid(row=6, column=1, sticky="ew", padx=5, pady=3)

        # --- Segundo Separador (Status e LOG)---
        ttk.Separator(self.root, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky="ew", pady=2)

        # --- Status e Progresso ---
        self.status_label = tk.Label(self.root, text="Aguardando entrada...")
        self.status_label.grid(row=8, column=0, sticky="ew", columnspan=2, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=9, column=0, sticky="ew", columnspan=2, pady=5, padx=5)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(self.root, width=30, height=10, state="disabled")
        self.log_area.grid(row=10, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")

#====================================  FIM DA DEFINIÇÃO DE LAYOUT =================================================================


    def _acao_confirmar(self):
        """Valida dados e inicia o processamento."""
        try:
            self.credenciais["usuario"] = self.entry_usuario.get()
            self.credenciais["senha"] = self.entry_senha.get()
            self.credenciais["usuario_sigede"] = self.entry_usuario_sigede.get()
            self.credenciais["senha_sigede"] = self.entry_senha_sigede.get()

            # ============= TRATAMENTO DO TEXTO NO CAMPO DE PROTOCOLOS (ScrolledText)=============
            # ("1.0", "end-1c"): Pega todo o texto exceto o último caractere de quebra de linha (automaticamente adicionado pelo TKinter).
            texto_bruto = self.entry_protocolos.get("1.0", "end-1c")
            
            # Normaliza: Transforma quebras de linha e espaços (eventualmente colocados pelo usuário ou automáticas) em vírgulas
            texto_normalizado = texto_bruto.replace("\n", ",") # Troca 'ENTER' por vírgula -Permite que o usuário cole uma coluna do Excel ou digite com vírgulas
            texto_normalizado = texto_normalizado.replace(" ", ",") # Troca Espaço por vírgula (mtos espaços viram muitas vírgulas mas não compromete a lista)
            
            # Cria a lista bruta separando as entradas pelas vírgulas da string normalizada acima (texto_normalizado)
            raw_protocolos = texto_normalizado.split(",")
            
            # Limpa e filtra (Sua List Comprehension)
            self.protocolos.clear()
            self.protocolos.extend([p.strip() for p in raw_protocolos if p.strip()])
            # SINTAX NOTE:  [ (p.strip()) for p in raw_protocolos if(p.strip()) ] : uma compreensão de lista (CONTRAÇAÕ DE FOR): com parênteses adicionais apenas para clareza dos campos
            ''' O Loop (for p in raw_protocolos): "Para cada item (que chamaremos de p) dentro da lista raw_protocolos..."
                O Filtro (if p.strip()): "...verifique se p.strip() é verdadeiro. (não vazio após o strip)
                A Ação (strip()) - [no início]: Se passou no filtro, remove espaços em branco e add à lista.       
            NOTE: self.protocolos.extend([p.strip() for p in raw_protocolos if p.strip()] )   NOTE: Equivale à:
                    for p in raw_protocolos:
                    if p.strip():          # Se não for vazio
                    protocols.append(p.strip()) # Limpa e adiciona
            '''
            # Registra no log (e no arquivo) a lista de protocolos (limpada) que será processada
            logger.info(f"Protocolos identificados ({len(self.protocolos)}): {self.protocolos}")

            # Checa se as entradas estão preenchidas (não checa validade de credenciais - que é feita em tempo de execução)
            self._validar_entradas()

            # Prepara UI para execução
            self._alternar_estado_ui(processando=True)
            self.cancelar_event.clear()
            self.progress_bar["maximum"] = len(self.protocolos)
            self.progress_bar["value"] = 0

            # Inicia Thread
            threading.Thread(target=self._executar_thread, daemon=True).start()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))

    def _validar_entradas(self):
        if not self.credenciais["usuario"] or not self.credenciais["senha"]:
            raise ValueError("Usuário e senha do SIATU são obrigatórios")
        if not self.credenciais["usuario_sigede"] or not self.credenciais["senha_sigede"]:
            raise ValueError("Usuário e senha do SIGEDE são obrigatórios")
        if not self.protocolos:
            raise ValueError("Informe ao menos um protocolo.")

    def _acao_cancelar(self):
        """Sinaliza o cancelamento."""
        if messagebox.askyesno("Confirmar", "Deseja realmente cancelar?"):
            self.cancelar_event.set()
            self.status_label.config(text="Cancelando... aguarde.")
            self.btn_cancelar.config(state="disabled")

    def _executar_thread(self):
        """Wrapper para rodar o callback na thread."""
        try:
            self.processar_callback(
                self.credenciais,
                self.protocolos,
                self.cancelar_event,
                self.atualizar_progresso
            )
        except Exception as e:
            logger.error(f"Erro na thread de processamento: {e}")
        finally:
            # Garante que o reset da UI aconteça na thread principal do Tkinter
            self.root.after(0, self.resetar_interface)

    def atualizar_progresso(self, valor):
        """Callback passado para o processamento atualizar a barra."""
        self.progress_bar["value"] = valor
        self.root.update_idletasks()

    def resetar_interface(self):
        """Restaura o estado inicial da UI após o fim do processo."""
        self.status_label.config(text="Processamento finalizado.")
        self._alternar_estado_ui(processando=False)
        messagebox.showinfo("Concluído", "O processamento foi finalizado.")

    def _alternar_estado_ui(self, processando: bool):
        """Habilita ou desabilita widgets baseado no estado."""
        state_input = "disabled" if processando else "normal"
        state_cancel = "normal" if processando else "disabled"
        
        self.btn_confirmar.config(state=state_input)
        self.entry_protocolos.config(state=state_input)
        self.btn_cancelar.config(state=state_cancel)
        
        if processando:
            self.status_label.config(text="Processando...")

    def _iniciar_leitura_logs(self):
        """Inicia o loop de atualização de logs."""
        self.atualizar_logs()

    def atualizar_logs(self):
        """Consome a fila de logs com Smart Auto-Scroll."""
        try:
            # Se não tem nada, nem perde tempo processando lógica de UI
            if log_queue.empty():
                return 

            # Checa se o usuário está com a Scroll-Bar do logger no final (Smart Scroll)
            # .yview() retorna a tupla, topo, base), da parte visualizada pelo ScrolledText. 
            # Domínio: [0.0 , 1.0].  Se base == 1.0, está no fim.
            posicao_atual = self.log_area.yview()
            estava_no_fim = (posicao_atual[1] == 1.0) 
            self.log_area.config(state="normal")
            
            # Insere TODAS as mensagens pendentes de uma vez (Batch update)
            while not log_queue.empty():
                msg = log_queue.get_nowait()
                self.log_area.insert(tk.END, msg + "\n")
            
            # Só rola a tela se o usuário já estava acompanhando o final
            if estava_no_fim:
                self.log_area.see(tk.END)
            
            self.log_area.config(state="disabled")

        except Exception:
            pass
        finally:
            # Agenda a próxima verificação
            self.root.after(100, self.atualizar_logs)

# --- Função Wrapper para manter compatibilidade com main.py ---
def iniciar_interface(processar_callback):
    """
    Função de entrada original mantida para compatibilidade.
    Instancia a classe e retorna o que o main.py espera.
    """
    app = InterfaceApp(processar_callback)
    
    # O main.py espera receber: root, função_reset, evento_cancelar
    return app.root, app.resetar_interface, app.cancelar_event
