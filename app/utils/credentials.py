import json
import os
from typing import Dict, Generator, Optional
from contextlib import contextmanager
from utils import settings, logger
from utils.settings import DATA_DIR
from utils.security import VaultSecurity
from utils.logger import ROOT
from utils.pastas import set_hidden, set_visible

VAULT_FILE = DATA_DIR / "credentials.tri"

class CredentialManager:
    """A responsável por Gerenciar as Credenciais - venham de onde venham."""

    @staticmethod
    def save_to_vault(creds: Dict[str, str], master_key: str):
        """Cifra o dicionário de credenciais e persiste no disco."""
        salt = VaultSecurity.gerar_salt()
        chave = VaultSecurity.derivar_chave(master_key, salt)
        
        dados_json = json.dumps(creds)
        blob = VaultSecurity.cifrar(dados_json, chave)
        
        set_visible(VAULT_FILE)
        # Estrutura do arquivo: Salt (16 bytes) + Blob Criptografado
        with open(VAULT_FILE, "wb") as f:
            f.write(salt + blob.encode())
        
        logger.info("Credenciais salvas no cofre com sucesso.")
        set_hidden(str(VAULT_FILE))

    @staticmethod
    def load_from_vault(master_key: str) -> Dict[str, str]:
        """Lê do disco, decifra usando a Master Key e retorna o dicionário."""
        if not VAULT_FILE.exists():
            raise FileNotFoundError("Arquivo de cofre (.tri) não encontrado no disco.")

        with open(VAULT_FILE, "rb") as f:
            conteudo = f.read()
            salt = conteudo[:16]
            blob = conteudo[16:].decode()

        chave = VaultSecurity.derivar_chave(master_key, salt)
        dados_json = VaultSecurity.decifrar(blob, chave)
        
        return json.loads(dados_json)

    @staticmethod
    def delete_vault():
        """Remove o arquivo físico do cofre do disco."""
        if VAULT_FILE.exists():
            try:
                os.remove(VAULT_FILE)
                logger.info("[CREDENTIAL MANAGER] Arquivo de cofre excluído com sucesso.")
            except Exception as e:
                logger.error(f"[CREDENTIAL MANAGER] Erro ao excluir cofre: {e}")
                raise
            
    
    @staticmethod
    @contextmanager
    def session_manager(master_key: Optional[str] = None) -> Generator[Dict[str, str], None, None]:
        """
        Context Manager Seguro: Entrega as credenciais e GARANTE a limpeza 
        delas memória global ao sair do bloco 'with'.
        """
        # Prioridade 1: Carrega do Vault se houver chave mestra
        creds = {}
        if master_key:
            try:
                creds = CredentialManager.load_from_vault(master_key)
            except Exception:
                logger.error("Falha ao abrir o cofre. Verifique a senha mestra.")

        # Prioridade 2: Busca da CLI (Sobrescreve o Vault se o usuário injetou via argumento)
        cli_creds = CredentialManager._get_initial_creds()
        
        for k, v in cli_creds.items():
            if v: 
                creds[k] = v

        tem_conteudo = any(valor.strip() for valor in creds.values() if valor)
        try:
            yield creds
        finally:
            settings.limpar_memoria_credenciais()
            creds.clear()
            if tem_conteudo:
                logger.debug("[CREDENTIAL MANAGER] Sessão encerrada e memória limpa.")

    @staticmethod
    def _parse_credential_string(raw_string: str) -> tuple[str, str]:
        """Separa a string bruta no padrão 'usuario::senha'."""
        if not raw_string:
            return ("", "")
        
        try:
            (user, password) = raw_string.split("::", 1)
            return (user.strip(), password.strip())
        except ValueError:
            return ("", "")
        
    @staticmethod
    def _get_initial_creds() -> Dict[str, str]:
        """
        Mapeia o dicionário bruto da CLI para o padrão final do pipeline.
        """
        cli_creds = settings._ARG_CREDS
        clean_creds = {}

        # Mapeamento : raw_key -> prefixo do sistema
        mapa = {
            "sigede_creds_raw": "_sgd_cred",
            "siatu_creds_raw":  "_stu_cred",
        }

        for key_raw, prefix in mapa.items():
            str_brut = cli_creds.get(key_raw)
            user, password = CredentialManager._parse_credential_string(str_brut)  
            clean_creds[f"{prefix}_user"] = user
            clean_creds[f"{prefix}_pass"] = password

        return clean_creds