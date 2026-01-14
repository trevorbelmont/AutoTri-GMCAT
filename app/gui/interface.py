import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import os
import sys
from utils import logger, log_queue
from utils import format_by_pattern, format_by_pattern2





def resource_path(relative_path: str) -> str:
    """ Retorna o caminho absoluto para recursos (como ícones) (Dev vs PyInstaller) """
    try:
        # Modo PyInstaller: procura a pasta temporária MEIPASS
        base_path = sys._MEIPASS

    except Exception: # Se não achou a pasta MEIPASS, então está rodando no interpretador

        # Modo Desenvolvimento (Baseado na localização do módulo atual, interface.py)
        # O arquivo interface.py está em: .../app/gui/
        # O ícone está em:                .../app/
        
        # Pega a pasta atual do arquivo (app/gui)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Sobe um nível para chegar em 'app/' (onde o ícone deve estar)
        base_path = os.path.dirname(current_dir)

    return os.path.join(base_path, relative_path)


class InterfaceApp:
    """ A classe que define o objeto de interface usando TKinter, callbacks e threads. """
     
    def __init__(self, processar_callback):
        self.processar_callback = processar_callback
        self.root = tk.Tk()
        self.root.title("AutoTri 1.49B - Automação de Triagem")
        
        # Estado da Aplicação (variáveis e evento thread)
        self.credenciais = {}
        self.protocolos = []
        self.indices_avulsos = []
        self.cancelar_event = threading.Event()

        # --- CARREGAMENTO DO ÍCONE ---
        ico_name = "PBH-Iconizado.ico"
        caminho_icone = resource_path(ico_name)

        try:
            self.root.iconbitmap(caminho_icone)
            # Log de Sucesso (Opcional, útil para dev)
            print(f"DEBUG ICONE: Sucesso ao carregar '{ico_name}' em '{caminho_icone}'")
        except Exception as e:
            # Log de Falha Detalhado (O que você pediu)
            print(f"AVISO ICONE: Não foi possível carregar o ícone '{ico_name}' em '{caminho_icone}': {e}")
        # -----------------------------
        
        # Inicializa a Interface
        self._configurar_widgets()
        self._iniciar_leitura_logs()


#==================================== INÍCIO DA DEFINIÇÃO DE LAYOUT =================================================================
# NOTE:  --------> self._NomeDaVarDoWidget_.winfo_exists() checa se o widget existe

    def _configurar_widgets(self):
        """Define todo o layout e widgets da janela."""

        # --- Configuração de Responsividade das Colunads da Interface ---
        self.root.geometry("600x600") 
        self.root.minsize(500, 475)   
            
        self.root.grid_columnconfigure(0, weight=0)     # Coluna 0 (Labels):    Peso 0: Tamanho fixo, não cresce.
        self.root.grid_columnconfigure(1, weight=1)     # Coluna 1 (Inputs):    Peso 1 : Cresce e ocupa todo o espaço horizontal sobrando)
            
        self.root.grid_rowconfigure(11, weight=1)       # Linha 10 (LOG):       Peso 1: É a última linha. Se ajusta à margem Sul.
        
        # NOTE: Na definição dos grids dos tk.Labels(...).grid(...) e tk.Entry().grid(...) e etc... 
        # usaremos stick="w" (West/Esquerda) e stick="e" (East/Direita) para "colar" os widgets nas margens.

        # TODO: Parametrizar as rows de cada seção do código - atualmente está hardcoded (definidas em números fixos no código)

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
                text=  "Protocolo(s):\n(Separados por VÍRGULAS)\n"
                        "Ex. 700649452520, 3100002390202324, 700693692507)",
                justify="left",        #Justifica label à esquerda
                ).grid(row=5, column=0, stick="nw", padx=5, pady=0)
        # wrap=tk.WORD : Define para que palavras (protocolos), separados por vírgula e espaço, 
        # não sejam visual partidos no meio na quebra de linha.
        self.entry_protocolos = tk.scrolledtext.ScrolledText(self.root, height=4,  width=30, wrap=tk.WORD)
        self.entry_protocolos.grid(row=5, column=1, stick= "nsew", padx=5, pady=2)

        #--------------------------- ÍNDICES CADASTRAIS ---------------------------------------

        tk.Label(self.root,
                text=  "Índices Cadastrais:\n(Separados por VÍRGULAS)\n"
                        "Ex: 3120160070011, 9290310040014, 9290280290013",
                justify= "left",
                ).grid(row=6, column=0, stick='nw', padx=5,pady = 15)
        
        # Adiciona o conteúdo do ScrolledText de Índices Cadastrais como uma variável do objeto InterfaceApp
        self.entry_cadastrais = tk.scrolledtext.ScrolledText(self.root, height = 3, width=30, wrap=tk.WORD)
        self.entry_cadastrais.grid(row = 6, column = 1, stick = 'nsew', padx=5, pady=5)

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
        self.btn_confirmar.grid(row=7, column=0, sticky="ew", padx=5, pady=3)

        self.btn_cancelar = tk.Button(self.root, text="Cancelar", command=self._acao_cancelar, state="disabled")
        self.btn_cancelar.grid(row=7, column=1, sticky="ew", padx=5, pady=3)

        # -------------------------- STATUS MESSAGE E BARRA DE PROGRESO-----------------------------
        # --- Segundo Separador (Status e LOG)---
        ttk.Separator(self.root, orient='horizontal').grid(row=8, column=0, columnspan=2, sticky="ew", pady=2)

        # --- Status e Progresso ---
        self.status_label = tk.Label(self.root,  height=2, text="Aguardando entrada...")
        self.status_label.grid(row=9, column=0, sticky="ew", columnspan=2, padx=5, pady=0)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=10, column=0, sticky="ew", columnspan=2, pady=5, padx=1)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(self.root, width=30, height=10, state="disabled")
        self.log_area.grid(row=11, column=0, columnspan=2, pady=10, padx=2, sticky="nsew")

#====================================  FIM DA DEFINIÇÃO DE LAYOUT =================================================================


    def _acao_confirmar(self):
        """Valida dados e inicia o processamento dentro de um try. 
        Se alguma excessão for lançadas (na validação de dados, por exemplo),
        Este método captura a exceção, NÃO COMEÇA A TRIAGEM e exibe a message box de erro de validação"""

        try:
            self.credenciais["usuario"] = self.entry_usuario.get()
            self.credenciais["senha"] = self.entry_senha.get()
            self.credenciais["usuario_sigede"] = self.entry_usuario_sigede.get()
            self.credenciais["senha_sigede"] = self.entry_senha_sigede.get()

            # ============= TRATAMENTO DO TEXTO DO  CAMPO DE PROTOCOLOS (ScrolledText) =============
            # ("1.0", "end-1c"): Pega todo o texto exceto o último caractere de quebra de linha (automaticamente adicionado pelo TKinter).
            texto_protocolos_bruto = self.entry_protocolos.get("1.0", "end-1c")
            
            # Normaliza: Transforma quebras de linha e espaços (eventualmente colocados pelo usuário ou automáticas) em vírgulas
            texto_protocolos_normalizado = texto_protocolos_bruto.replace("\n", ",") # Troca 'ENTER' por vírgula -Permite que o usuário cole uma coluna do Excel ou digite com vírgulas
            texto_protocolos_normalizado = texto_protocolos_normalizado.replace(" ", ",") # Troca Espaço por vírgula (mtos espaços viram muitas vírgulas mas não compromete a lista)
            
            # Cria a lista bruta separando as entradas pelas vírgulas da string normalizada acima (texto_normalizado)
            raw_protocolos = texto_protocolos_normalizado.split(",")
            
            # Limpa (reseta) e cria a lista de protocolos (com List Comprehension)
            self.protocolos.clear()
            self.protocolos.extend([p.strip() for p in raw_protocolos if p.strip()])

            # SINTAX NOTE:  [ (p.strip()) for p in raw_protocolos if(p.strip()) ] : uma compreensão de lista (CONTRAÇAÕ DE FOR): com parênteses adicionais apenas para clareza dos campos
            ''' O Loop (for p in raw_protocolos): "Para cada item (que chamaremos de p) dentro da lista raw_protocolos..."
                O Filtro (if p.strip()): "...verifique se p.strip() é verdadeiro. (não vazio após o strip)
                A Ação (strip()) - [no início]: Se passou no filtro, remove espaços em branco e add à lista.       
            NOTE: self.protocolos.extend([p.strip() for p in raw_protocolos if p.strip()] )   NOTE: Equivale à:
                    for p in raw_protocolos:
                    if p.strip():               # Se não for vazio
                    protocols.append(p.strip()) # Limpa e adiciona
            '''

            # ============= TRATAMENTO DO CAMPO DE ÍNDICES (ScrolledText) =============
            texto_indices_bruto = self.entry_cadastrais.get("1.0", "end-1c")
            # fazemos as duas sanitazações em cadeia (como com os protocolos) só que na mesma linha de código
            texto_indices_normalizado = texto_indices_bruto.replace("\n", ",").replace(" ", ",") 
            raw_indices = texto_indices_normalizado.split(',')  # criamos a lista, separando pelas vírgulas (dos índices normalizados)

            # Limpa (reseta) e cria a lista de índices (com List Comprehension)
            self.indices_avulsos.clear()
            
            # Padrão PBH: 6 dígitos (Regional) + Espaço + 3 dígitos (Quadra) + Espaço + 4 dígitos (Lote)
            MASK_PBH = "###### ### ####" 

            for i in raw_indices:
                if not i.strip(): continue
                
                
                ic_fmt = format_by_pattern2(i.strip(), MASK_PBH)
                
                if ic_fmt:
                    self.indices_avulsos.append(ic_fmt)
            
            # ---------------- BARREIRA DE VALIDAÇÃO ----------------
            # Checa se as entradas estão preenchidas (não checa validade de credenciais - que é feita em tempo de execução)
            self._validar_entradas()
            # Se esta função encontrar erro, ela lançará ValueError.
            # O código pulará IMEDIATAMENTE a triagem e seguirá bloco 'except ValueError', onde a message box de erro é exibida.
            # -------------------------------------------------------
            

            # Prepara UI para execução e DETERMINA O MAXIMUM (TOTAL) DA BARRA DE PROGRESSO
            self._alternar_estado_ui(processando=True)
            self.cancelar_event.clear()
            self.progress_bar["maximum"] = len(self.protocolos)
            self.progress_bar["value"] = 0

            # Inicia Thread
            threading.Thread(target=self._executar_thread, daemon=True).start()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))

    def _validar_entradas(self)-> None:
        """Verifica se os campos obrigatórios foram preenchidos,
        caso contrário lança exceção 'ValueError' para ser tratada pelo caller.
        
        Raises:
            ValueError: Se credenciais estiverem vazias OU
                        Se não houver nem Protocolo nem Índice para processar.
                        (A exceção lançada interrompe o fluxo de quem chamou este método - e deve tratar a exceção).
        """
        if not self.credenciais["usuario"] or not self.credenciais["senha"]:
            raise ValueError("Usuário e senha do SIATU são obrigatórios")
        if not self.credenciais["usuario_sigede"] or not self.credenciais["senha_sigede"]:
            raise ValueError("Usuário e senha do SIGEDE são obrigatórios")
        if not self.protocolos and not self.indices_avulsos:
            raise ValueError("Informe ao menos um protocolo ou índice cadastral para a triagem.")

    def _acao_cancelar(self):
        """Sinaliza o cancelamento."""
        if messagebox.askyesno("Confirmar", "Deseja realmente cancelar?"):
            self.cancelar_event.set()
            self.status_label.config(text="Cancelando... aguarde.")
            self.btn_cancelar.config(state="disabled")


    def _executar_thread(self):
        """Wrapper para rodar o callback na thread.
        Nesse método que o processamento efetivo dos protocolos e ICs é chamado.
        self.processar_callback(...) é uma função injetada por dependência na criação do objeto InterfaceApp.
        A função (dependência injetada) é a função aninhada processar(...) definida na função main de main.py.
        O método atual, _executar_thread(self), dispara o processamento usando a função injetada no objeto interface."""
        try:
            # Chama a função 'processar(...)' definida dentro da main - em main.py - como função aninhada.
            # A chamada de 'processar(...)' da main é feita pela dependência injetada no objeto,
            # aqui a referenciada por processar_callback(...) - que aponta para 'processar(...)' definida na main.
            self.processar_callback(
                self.credenciais,
                self.protocolos,
                self.indices_avulsos,
                self.cancelar_event,
                self.atualizar_progresso,
                self.atualizar_status 
            )
        except Exception as e:
            # Se der erro CRÍTICO na thread (antes do main tratar), faz o log do Erro e.....
            logger.error(f"Erro na thread de processamento: {e}")
            # Como aconteceu um erro crítico, FORÇA O RESET DA INTERFACE (pra não travar em "Processando...")
            # Este RESET normalmente é chamado ao fim do processamento na main.py - chamamos aqui SÓ EM CASO DE ERRO NA THREAD
            self.root.after(0, self.resetar_interface) 

    # Método auxiliar chamado para atualizar o texto do Status de processamento
    def atualizar_status(self, texto: str):
        """Atualiza o texto da label de status na GUI."""
        self.status_label.config(text=texto)
        self.root.update_idletasks() # Força atualização visual imediata

    # Método auxiliar para atualizar para atualização da barra de progresso.
    def atualizar_progresso(self, valor):
        """Callback passado para o processamento atualizar a barra de progresso.
        TODO: atualmente atualiza apenas processamendo de protocolos: 
        colocar granularidade de fases (do processamento de ICs) na barra de progresso)?"""
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
