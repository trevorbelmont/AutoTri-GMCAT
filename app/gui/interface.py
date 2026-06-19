import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, simpledialog
import threading
import os
import sys
from utils import logger, log_queue, settings, CredentialManager
from utils import format_by_pattern, format_by_pattern2, resource_path
from typing import Callable, Optional, Dict, Any


import time
from datetime import timedelta


class InterfaceApp:
    """A classe que define o objeto de interface usando TKinter, callbacks e threads."""

    def __init__(
        self, processar_callback: Callable, default_creds_CRD_MNGR: Dict[str, str]
    ):
        """Construtor do objeto InterfaceApp que é chamado no fim deste módulo na função wrapper, _iniciar_interface()."""

        self.processar_callback = processar_callback
        self.root = tk.Tk()
        self.root.title("AutoTri 1.63b - Automação de Triagem")

        # Guarda as credenciais default (vindas do Credential Manager) que podem ser vazias.
        self.default_creds = default_creds_CRD_MNGR

        self.credenciais = {}
        self.protocolos = []
        self.indices_avulsos = []
        self.cancelar_event = threading.Event()

        ico_name = "PBH-Iconizado.ico"
        caminho_icone = resource_path(ico_name)

        try:
            self.root.iconbitmap(caminho_icone)
            logger.debug(
                f"DEBUG ICONE: Sucesso ao carregar '{ico_name}' em '{caminho_icone}'"
            )
        except Exception as e:
            logger.debug(
                f"DEBUG - AVISO ICONE: Não foi possível carregar o ícone '{ico_name}' em '{caminho_icone}': {e}"
            )

        # Inicializa a Interface
        self._configurar_widgets()
        self._iniciar_leitura_logs()
        self.root.after(500, self._verificar_vault_ao_iniciar)

    def _configurar_widgets(self):
        """Define todo o layout e widgets da janela. E, se houver credenciais legadas do CrentialManager, auto-preenche."""

        self.root.geometry("600x600")
        self.root.minsize(500, 475)

        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(11, weight=1)

        tk.Label(self.root, text="Usuário SIGEDE:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.entry_usuario_sigede = tk.Entry(self.root, width=30)
        self.entry_usuario_sigede.grid(row=0, column=1, sticky="e", padx=5, pady=5)

        tk.Label(self.root, text="Senha SIGEDE:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.entry_senha_sigede = tk.Entry(self.root, show="*", width=30)
        self.entry_senha_sigede.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        tk.Label(self.root, text="Usuário SIATU:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.entry_usuario = tk.Entry(self.root, width=30)
        self.entry_usuario.grid(row=2, column=1, sticky="e", padx=5, pady=5)

        tk.Label(self.root, text="Senha SIATU:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.entry_senha = tk.Entry(self.root, show="*", width=30)
        self.entry_senha.grid(row=3, column=1, sticky="e", padx=5, pady=5)

        # ---- Se houver Credencias legadas do Credential Manager (CLI), auto-preenche.
        if self.default_creds.get("_sgd_cred_user"):
            self.entry_usuario_sigede.insert(0, self.default_creds["_sgd_cred_user"])
        if self.default_creds.get("_sgd_cred_pass"):
            self.entry_senha_sigede.insert(0, self.default_creds["_sgd_cred_pass"])
        if self.default_creds.get("_stu_cred_user"):
            self.entry_usuario.insert(0, self.default_creds["_stu_cred_user"])
        if self.default_creds.get("_stu_cred_pass"):
            self.entry_senha.insert(0, self.default_creds["_stu_cred_pass"])

        ttk.Separator(self.root, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=2
        )

        # --------------------------------------- Protocolos ---------------------------------------
        tk.Label(
            self.root,
            text="Protocolo(s):\n(Separados por VÍRGULAS)\n"
            "Ex. 700649452520, 3100002390202324, 700693692507)",
            justify="left",
        ).grid(row=5, column=0, stick="nw", padx=5, pady=0)
        self.entry_protocolos = tk.scrolledtext.ScrolledText(
            self.root, height=4, width=30, wrap=tk.WORD
        )
        self.entry_protocolos.grid(row=5, column=1, stick="nsew", padx=5, pady=2)

        # --------------------------- ÍNDICES CADASTRAIS ---------------------------------------
        tk.Label(
            self.root,
            text="Índices Cadastrais:\n(15 Caracteres sparados por VÍRGULAS)\n"
            "Ex: 312016 007 0011, 312024A025 0010, 929028A829B0013",
            justify="left",
        ).grid(row=6, column=0, stick="nw", padx=5, pady=15)
        self.entry_cadastrais = tk.scrolledtext.ScrolledText(
            self.root, height=3, width=30, wrap=tk.WORD
        )
        self.entry_cadastrais.grid(row=6, column=1, stick="nsew", padx=5, pady=5)

        # --------------------------------------- Botões ---------------------------------------
        self.btn_confirmar = tk.Button(
            self.root, text="Iniciar", command=self._acao_confirmar
        )
        self.btn_confirmar.grid(row=7, column=0, sticky="ew", padx=5, pady=3)

        self.btn_cancelar = tk.Button(
            self.root, text="Cancelar", command=self._acao_cancelar, state="disabled"
        )
        self.btn_cancelar.grid(row=7, column=1, sticky="ew", padx=5, pady=3)

        ttk.Separator(self.root, orient="horizontal").grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=2
        )

        # -------------------------- STATUS MESSAGE E BARRA DE PROGRESO-----------------------------
        self.status_label = tk.Label(self.root, height=2, text="Aguardando entrada...")
        self.status_label.grid(
            row=9, column=0, sticky="ew", columnspan=2, padx=5, pady=0
        )

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=500, mode="determinate"
        )
        self.progress_bar.grid(
            row=10, column=0, sticky="ew", columnspan=2, pady=5, padx=1
        )

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(
            self.root, width=30, height=10, state="disabled"
        )
        self.log_area.grid(
            row=11, column=0, columnspan=2, pady=5, padx=2, sticky="nsew"
        )

        # ---- Timers e Settings ----
        self.timers_label = tk.Label(self.root, text="--:-- / --:--", justify="center")
        self.timers_label.grid(
            row=12, column=0, sticky="ew", columnspan=2, pady=0, padx=0
        )
        self.btn_settings = tk.Button(
            self.root, 
            text="⚙️ Configurações de Execução e Cofre", 
            command=self._abrir_janela_settings,
            bg="#f0f0f0"
        )
        self.btn_settings.grid(row=13, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    def _acao_confirmar(self):
        """Valida dados e inicia o processamento dentro de um try.
        Se alguma excessão for lançada (na validação de dados, por exemplo),
        Este método captura a exceção, NÃO COMEÇA A TRIAGEM e exibe a message box de erro de validação
        """

        try:
            self.credenciais["usuario"] = self.entry_usuario.get()
            self.credenciais["senha"] = self.entry_senha.get()
            self.credenciais["usuario_sigede"] = self.entry_usuario_sigede.get()
            self.credenciais["senha_sigede"] = self.entry_senha_sigede.get()

            texto_protocolos_bruto = self.entry_protocolos.get("1.0", "end-1c")

            texto_protocolos_normalizado = texto_protocolos_bruto.replace("\n", ",")
            texto_protocolos_normalizado = texto_protocolos_normalizado.replace(
                " ", ","
            )

            raw_protocolos = texto_protocolos_normalizado.split(",")

            self.protocolos.clear()
            self.protocolos.extend([p.strip() for p in raw_protocolos if p.strip()])

            texto_indices_bruto = self.entry_cadastrais.get("1.0", "end-1c")
            texto_indices_normalizado = texto_indices_bruto.replace("\n", ",")
            raw_indices = texto_indices_normalizado.split(",")

            self.indices_avulsos.clear()

            for i in raw_indices:
                idc_limpo = i.strip()

                if not idc_limpo:
                    continue

                if len(idc_limpo) == 15:
                    self.indices_avulsos.append(idc_limpo)
                else:
                    logger.warning(
                        f"Índice Cadastra {i} não será triado pois não está no padrão de 15 caracteres esperado."
                    )

            self._validar_entradas()
            self._alternar_estado_ui(processando=True)
            self.cancelar_event.clear()
            self.progress_bar["maximum"] = 100
            self.progress_bar["value"] = 0

            threading.Thread(target=self._executar_thread, daemon=True).start()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))

    def _validar_entradas(self) -> None:
        """Verifica se os campos obrigatórios foram preenchidos,
        caso contrário lança exceção 'ValueError' para ser tratada pelo caller.
        """
        if not self.credenciais["usuario"] or not self.credenciais["senha"]:
            raise ValueError("Usuário e senha do SIATU são obrigatórios")
        if (not self.credenciais["usuario_sigede"]
            or not self.credenciais["senha_sigede"]
        ):
            raise ValueError("Usuário e senha do SIGEDE são obrigatórios")
        if not self.protocolos and not self.indices_avulsos:
            raise ValueError(
                "Informe ao menos um protocolo ou índice cadastral para a triagem."
            )

    def _acao_cancelar(self):
        """Sinaliza o cancelamento."""
        if messagebox.askyesno("Confirmar", "Deseja realmente cancelar?"):
            self.cancelar_event.set()
            self.status_label.config(text="Cancelando... aguarde.")
            self.btn_cancelar.config(state="disabled")

    def _executar_thread(self):
        """Wrapper para rodar o callback na thread.
        Nesse método que o processamento efetivo dos protocolos e ICs é chamado."""

        try:
            self.processar_callback(
                self.credenciais,
                self.protocolos,
                self.indices_avulsos,
                self.cancelar_event,
                self.atualizar_progresso,
                self.atualizar_status,
                self.iniciar_cronometro_simples,
            )
        except Exception as e:
            logger.error(f"Erro na thread de processamento: {e}")
            self.root.after(0, self.resetar_interface)

    def atualizar_status(self, texto: str):
        """Atualiza o texto da label de status na GUI."""
        self.status_label.config(text=texto)
        self.root.update_idletasks()  # Força atualização visual imediata

    def atualizar_progresso(self, valor: float):
        """Callback passado para o processamento atualizar a barra de progresso."""
        self.progress_bar["value"] = valor
        self.root.update_idletasks()

    def iniciar_cronometro_simples(self, estimativa_segundos: int):
        """Inicia contagem baseada numa estimativa fixa recebida da main."""
        self.inicio = time.time()
        self.estimativa = estimativa_segundos
        self.rodando = True
        self._atualizar_relogio()

    def _atualizar_relogio(self):
        if not self.rodando:
            return

        agora = time.time()
        decorrido = int(agora - self.inicio)

        # Formata no padrão humano (00:00:00)
        str_decorrido = str(timedelta(seconds=decorrido))
        str_estimado = str(timedelta(seconds=int(self.estimativa)))

        self.timers_label.config(
            text=f"Tempo: {str_decorrido}  /  Estimado: ~{str_estimado}"
        )

        self.root.after(1000, self._atualizar_relogio)

    def parar_cronometro(self):
        self.rodando = False

    def resetar_interface(self):
        """Restaura o estado inicial da UI após o fim do processo."""
        self.parar_cronometro()
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
            if log_queue.empty():
                return

            # Checa se o usuário está com a Scroll-Bar do logger no final (Smart Scroll)
            posicao_atual = self.log_area.yview()
            estava_no_fim = posicao_atual[1] == 1.0
            self.log_area.config(state="normal")

            while not log_queue.empty():
                msg = log_queue.get_nowait()
                self.log_area.insert(tk.END, msg + "\n")

            if estava_no_fim:
                self.log_area.see(tk.END)

            self.log_area.config(state="disabled")

        except Exception:
            pass
        finally:
            self.root.after(100, self.atualizar_logs)

    # ======= Métodos do Vault Security & Settings ======= #

    def _verificar_vault_ao_iniciar(self):
        """Detecta a presença do cofre e oferece carregamento automático."""
        from utils.credentials import VAULT_FILE
        if VAULT_FILE.exists():
            logger.info("Cofre de credenciais identificado.")
            if messagebox.askyesno("Cofre Detectado", "Existe um cofre de credenciais salvo. Deseja carregar agora?"):
                logger.info("Aguardando entrada da senha mestra.")
                self._acao_carregar_vault()
                
    def _preencher_campos_interface(self, creds: Dict[str, str]):
        """Mapeia os dados do dicionário para os widgets da interface."""
        # SIGEDE
        if creds.get("_sgd_cred_user"):
            self.entry_usuario_sigede.delete(0, tk.END)
            self.entry_usuario_sigede.insert(0, creds["_sgd_cred_user"])
        if creds.get("_sgd_cred_pass"):
            self.entry_senha_sigede.delete(0, tk.END)
            self.entry_senha_sigede.insert(0, creds["_sgd_cred_pass"])
        
        # SIATU
        if creds.get("_stu_cred_user"):
            self.entry_usuario.delete(0, tk.END)
            self.entry_usuario.insert(0, creds["_stu_cred_user"])
        if creds.get("_stu_cred_pass"):
            self.entry_senha.delete(0, tk.END)
            self.entry_senha.insert(0, creds["_stu_cred_pass"])

    def _acao_carregar_vault(self):
        """Solicita a Master Key e preenche a interface."""
        senha_mestra = simpledialog.askstring("Chave Mestra", "Digite a senha para abrir o cofre:", show='*')
        if senha_mestra:
            try:
                creds = CredentialManager.load_from_vault(senha_mestra)
                
                if not creds:
                    messagebox.showwarning("Aviso", "O cofre foi aberto, mas está vazio.")
                    logger.warning("O Cofre foi aberto mas está vazio!")
                    return

                self._preencher_campos_interface(creds)
                messagebox.showinfo("Sucesso", "Credenciais carregadas do cofre.")
                logger.info("Credenciais carregadas do cofre via chave-mestra com sucesso.")
            except FileNotFoundError as e:
                messagebox.showwarning("Cofre Ausente", str(e))
                logger.error(f"Cofre Ausente! {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao abrir cofre: {e}")
                logger.error(f"Falha ao abrir cofre: {e}")

    def _acao_salvar_vault(self):
        """Captura os campos atuais e salva no cofre criptografado."""
        creds_atuais = {
            "_sgd_cred_user": self.entry_usuario_sigede.get(),
            "_sgd_cred_pass": self.entry_senha_sigede.get(),
            "_stu_cred_user": self.entry_usuario.get(),
            "_stu_cred_pass": self.entry_senha.get()
        }
        
        senha_mestra = simpledialog.askstring("Nova Chave Mestra", "Defina uma senha para proteger este cofre:", show='*')
        if senha_mestra:
            try:
                CredentialManager.save_to_vault(creds_atuais, senha_mestra)
                messagebox.showinfo("Sucesso", "Cofre criado/atualizado com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar cofre: {e}")

    def _abrir_janela_settings(self):
        """Abre a janela secundária de configurações e segurança (UX Condensada)."""
        janela = tk.Toplevel(self.root)
        janela.title("Configurações Adicionais e Segurança")

        x = self.root.winfo_x() + self.root.winfo_width() + 5
        y = self.root.winfo_y()
        janela.geometry(f"450x530+{x}+{y}")
        janela.minsize(450,400)

        janela.transient(self.root)
        #janela.grab_set() #grab_set() força o focus na janela de config

        # --- SEÇÃO DE SEGURANÇA (Cofre) ---
        lbl_sec = tk.LabelFrame(janela, text=" Gerenciamento de Cofre de Credenciais (Criptografia) ", padx=10, pady=10)
        lbl_sec.pack(fill="x", padx=10, pady=5)

        tk.Button(lbl_sec, text="🔓 Carregar Credenciais do Cofre", command=self._acao_carregar_vault).pack(fill="x", pady=2)
        tk.Button(lbl_sec, text="🔒 Salvar/Atualizar Credenciais Atuais no Cofre", command=self._acao_salvar_vault).pack(fill="x", pady=2)

        # --- SEÇÃO DE EXECUÇÃO (Settings.py) ---
        lbl_exec = tk.LabelFrame(janela, text=" Parâmetros de Execução e Performance ", padx=10, pady=10)
        lbl_exec.pack(fill="x", padx=10, pady=5)

        campos_numericos = [
            ("Máximo de Retentativas (Retry):", "RETRY_MAX", settings.RETRY_MAX),
            ("Delay entre Retries (seg):", "RETRY_DELAY", settings.RETRY_DELAY),
            ("Timeout de Espera (seg):", "TIMEOUT_ESPERA", settings.TIMEOUT_ESPERA),
            ("Timeout de Download (seg):", "TIMEOUT_DOWNLOAD", settings.TIMEOUT_DOWNLOAD),
        ]

        entries = {}
        for i, (label_text, attr_name, current_val) in enumerate(campos_numericos):
            tk.Label(lbl_exec, text=label_text).grid(row=i, column=0, sticky="w", pady=2)
            ent = tk.Entry(lbl_exec, width=10)
            ent.insert(0, str(current_val))
            ent.grid(row=i, column=1, sticky="e", pady=2)
            entries[attr_name] = ent

        # Campos de Seleção (Booleanos)
        var_debug = tk.BooleanVar(value=settings.DEBUG)
        tk.Checkbutton(lbl_exec, text="Ativar Modo Debug (Logs verbosos)", variable=var_debug).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)

        var_headless = tk.BooleanVar(value=settings.NOT_HEADLESS)
        tk.Checkbutton(lbl_exec, text="Exibir Navegador (Desativar Headless)", variable=var_headless).grid(row=5, column=0, columnspan=2, sticky="w", pady=2)

        var_lot = tk.BooleanVar(value=settings.LOT_DEBUGGER)
        tk.Checkbutton(lbl_exec, text="Gerar Log de Erros dedicado (Triagem em Lote)", variable=var_lot).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)

        def salvar_settings():
            try:
                settings.RETRY_MAX = int(entries["RETRY_MAX"].get())
                settings.RETRY_DELAY = float(entries["RETRY_DELAY"].get())
                settings.TIMEOUT_ESPERA = float(entries["TIMEOUT_ESPERA"].get())
                settings.TIMEOUT_DOWNLOAD = float(entries["TIMEOUT_DOWNLOAD"].get())
                
                settings.DEBUG = var_debug.get()
                settings.NOT_HEADLESS = var_headless.get()
                settings.LOT_DEBUGGER = var_lot.get()

                # Aplicação imediata do nível de log se o Debug mudar
                import logging
                if settings.DEBUG:
                    logger.setLevel(logging.DEBUG)
                else:
                    logger.setLevel(logging.INFO)

                logger.debug(
                    f"[SETTINGS] Nova Configuração Aplicada:\n"
                    f"       DEBUG={settings.DEBUG}, NOT_HEADLESS={settings.NOT_HEADLESS},\n"
                    f"       TIMEOUT={settings.TIMEOUT_ESPERA}s, TIMEOUT_DOWNLOAD={settings.TIMEOUT_DOWNLOAD}s\n"
                    f"       RETRY_MAX={settings.RETRY_MAX}, RETRY_DELAY={settings.RETRY_DELAY},\n"
                    f"       LOT_DEBUGGER = {settings.LOT_DEBUGGER},\n"
                    f"       DATA_DIR = {settings.DATA_DIR}\n")

                messagebox.showinfo("Sucesso", "Configurações aplicadas com sucesso.")
                janela.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Certifique-se de que os campos de Retry e Timeout contenham apenas números.")

        tk.Button(janela, text="Aplicar Configurações", command=salvar_settings, bg="#e1f5fe").pack(pady=5)

        
        lbl_file = tk.LabelFrame(janela, text=" Manutenção do Sistema ", padx=10, pady=10)
        lbl_file.pack(fill="x", padx=10, pady=5)

        tk.Button(
            lbl_file, 
            text="💾 Salvar Minhas Preferências de Configuração", 
            command=lambda: [salvar_settings(), settings.save_config()], 
            bg="#c8e6c9"
        ).pack(fill="x", pady=2)

        tk.Button(
            lbl_file, 
            text="🗑️ Excluir Cofre de Senhas", 
            command=self._acao_limpar_vault, 
            fg="red"
        ).pack(fill="x", pady=2)

        # Botão para resetar o config.json
        tk.Button(
            lbl_file, 
            text="🔄 Restaurar Padrões (Reset)", 
            command=self._acao_resetar_config
        ).pack(fill="x", pady=2)

    def _acao_limpar_vault(self):
        if messagebox.askyesno("Confirmar", "Deseja excluir o cofre de senhas? Isso apagará suas credenciais. Continuar"):
            try:
                CredentialManager.delete_vault()
                for entry in [self.entry_usuario_sigede, self.entry_senha_sigede, self.entry_usuario, self.entry_senha]:
                    entry.delete(0, tk.END)
                messagebox.showinfo("Sucesso", "Cofre removido.")
                logger.warning("Cofre de credenciais limpo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao deletar cofre criptografado de credenciais (credentials.tri) ou limpar campos da interface: {e}")

    def _acao_resetar_config(self):
        """Reseta configurações para configurações default de fábrica."""
        if messagebox.askyesno("Resetar", "Restaurar configurações para os  padrões de fábrica? O app será fechado. Continuar?"):
            settings.reset_to_defaults()
            messagebox.showinfo("Reset", "Configurações limpas. Reinicie o AutoTri.")
            self.root.destroy()


def iniciar_interface(
    processar_callback: Callable, default_creds_CRD_MNGR: Dict[str, str] = None
):
    """
    Wrapper: Função de entrada original mantida para compatibilidade.
    Instancia a classe e retorna o que o main.py espera.
    """

    if default_creds_CRD_MNGR is None:
        default_creds_CRD_MNGR = {}
    app = InterfaceApp(processar_callback, default_creds_CRD_MNGR)

    return (
        app.root,
        app.resetar_interface,
        app.cancelar_event,
        app.iniciar_cronometro_simples,
    )
