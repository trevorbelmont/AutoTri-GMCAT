from typing import Dict, Generator
from contextlib import contextmanager
from utils import settings
from utils import logger

class CredentialManager:
    '''A responsável por Gerenciar as Credenciais - venham de onde venham.'''


    '''def __init__(): pass NOTE: poderíamos definir um construtor para forçar CredManager ser de fato uma Classe...
    Não o faremos pq aqui seria mais interessante usar o __init__ implícito, (ao invés de impedir instanciação com erros ou forçar o pass)
    que nesse caso faz CredManager ser tratado como namespace. Ao invés de classe - em nível de interpretação.'''


    @staticmethod
    @contextmanager
    def session_manager() -> Generator[Dict[str, str], None, None]:
        """
        Context Manager Seguro: Entrega as credenciais e GARANTE a limpeza delas memória global ao sair do bloco 'with' e em sessions.
        """
        
        creds = CredentialManager._get_initial_creds()
        tem_conteudo = any(valor.strip() for valor in creds.values() if valor)
        try:
            yield creds
        finally:
            settings.limpar_memoria_credenciais()
            creds.clear()   # Limpa o dict de creds (aqui e na interface.py)
            if tem_conteudo:
                logger.debug("[CREDENTIAL MANAGER] Credenciais injetadas na interface e removidas da memória Python com Sucesso.\n\n")


    @staticmethod
    def _parse_credential_string(raw_string: str) -> tuple[str, str]:

        if not raw_string:
            return ("","")
        
        try:
            #NOTE: robustez: separa apenas no PRIMEIRO "::" - como esperado e viável -> ".split("::", 1)"
            # Logo, utomaticamente escapa dois pontos, ":", na senha (mas não no usuário)
            (user, password) = raw_string.split("::",1)
            return (user.strip(), password.strip())
        except ValueError:
            return ("","")
        
    @staticmethod
    def _get_initial_creds() -> Dict[str, str]:
        ''' Processa o dict de strings_de_cred brutas e mapeia pra um dict usável final. Se não houver credencial definida pra um dos campos, retorna string vazia "" para apenas aquele campo ficar em branco.
        :return: Dicionário de credenciais padronizado e pronto pra uso no pipeline.'''
        cli_creds = settings._ARG_CREDS
        clean_creds = {}

        #NOTE: Define um mapa de atributos para saber quais procurar de forma elegante
        # Os atributos (chaves do dict) são independentes: ou seja: não quebra se não achar um deles.
        mapa = {
        #   "key_dict_settings"     : "key_prefix_dict_final" (o prefixo da chave no dicionário final)
            "sigede_creds_raw"       : "_sgd_cred",
            "siatu_creds_raw"        :  "_stu_cred",
        }

        for key_raw, prefix in mapa.items():
            str_brut = cli_creds.get(key_raw)

            user, password = CredentialManager._parse_credential_string(str_brut)  

            # Preenche o dict final - de retorno (usando os prefixos do mapa nas chaves)
            clean_creds [f"{prefix}_user"] = user
            clean_creds [f"{prefix}_pass"] = password

        return clean_creds

