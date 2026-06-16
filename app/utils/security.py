import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey
from utils.logger import logger

class VaultSecurity:
    """
    Motor de segurança do AutoTri. 
    Responsável pela matemática de proteção de dados sem conhecimento da regra de negócio.
    """

    @staticmethod
    def gerar_salt() -> bytes:
        """Gera um salt aleatório de 16 bytes para derivação de chave."""
        return os.urandom(16)

    @staticmethod
    def derivar_chave(senha: str, salt: bytes) -> bytes:
        """
        Transforma uma senha textual em uma chave criptográfica de 32 bytes.
        Utiliza 100.000 iterações de PBKDF2 para mitigar ataques de força bruta.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        logger.info("Chave candidata derivada com sucesso.")
        return base64.urlsafe_b64encode(kdf.derive(senha.encode()))

    @staticmethod
    def cifrar(dados: str, chave: bytes) -> str:
        """Cifra uma string de dados e retorna o token criptografado."""
        f = Fernet(chave)
        logger.info("String cifrado em token criptografado com sucesso!")
        return f.encrypt(dados.encode()).decode()

    @staticmethod
    def decifrar(token: str, chave: bytes) -> str:
        """
        Decifra um token. 
        Lança Exception se a chave for inválida ou o dado estiver corrompido.
        """
        try:
            f = Fernet(chave)
            return f.decrypt(token.encode()).decode()
        except InvalidKey:
            logger.error("Chave mestra incorreta ou cofre corrompido.")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na decifragem: chave Mestra inválida! {e}")
            raise