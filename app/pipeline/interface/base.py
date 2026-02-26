from abc import ABC, abstractmethod
from typing import Any


class SistemaAutomacao(ABC):
    # TODO: Padronizar os parâmetros da interface executar para contemplar todas as classes definidas (LSP)
    @abstractmethod
    def executar(self, indice, credenciais, pasta_indice) -> Any:
        """Executa coleta de dados e retorna os resultados do sistema"""
        pass
