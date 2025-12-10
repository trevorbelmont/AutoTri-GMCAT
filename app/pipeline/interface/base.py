from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
#ABC = Abstract Base Class - permite definir classes abstratas em python

# Define um contrato para qualquer classe que herde de SistemaAutomação (que por sua vez herda de ABC, para implementar métodos abstratos)
# Todo bot que herde de SistemaAutomação deve ter pelo menos o método executar(...) implementado com essa assinatura de argumentos
# ! A definição anterior quebrava o LSP (Princípio da Sustituição de Liskov), uma vez que GoogleMaps.executar(...) possui 2 parâmetros a mais.
# Para manter essa escolha e arquitetura de produção mas de forma mais clara e robusta optou-se por refatorar utilizando Optional
class SistemaAutomacao(ABC):
    @abstractmethod # Este decorator, aplicado ao método executar(...) força que qualquer classe filha defina seu próprio método executar
    # O retorno é definido como 'Any' pois cada classe concreta retorna um tipo diferente em suas implementações de executar(...)
    # O argumento 'indice' é o termo genérico para IC ou Protocolo.
    def executar(
        # Oss 3 Argumentos e tipos obrigatórios (comuns à todas as Classes de serviço em pipeline/sistemas.py)
        self,
        indice: str, 
        credenciais: Dict[str, str], 
        pasta_indice: str,
        # Os argumentos opcionais (até então apenas a Classe GoogleMaps tem precisado)
        # Optional[Dict[str, Any]] = None indica ser um dicionário (se fornecido) ou None, quando omitido.
        dados_sistema1: Optional[Dict[str, Any]] = None, 
        dados_sistema2: Optional[Dict[str, Any]] = None 
        ) -> Any:           # O retorno é any
        """
        Executa coleta de dados e retorna os resultados do sistema.

        :param indice: O termo principal de busca (Índice Cadastral ou Protocolo).
        :param credenciais: Dicionário contendo as credenciais de login para o sistema.
        :param pasta_indice: Caminho completo da pasta de resultados/downloads.
        :param dados_sistema1: Dados opcionais de um sistema anterior (Dict[str, Any]).
        :param dados_sistema2: Dados opcionais de um sistema anterior (Dict[str, Any]).
        :return: O retorno é definido como 'Any' pois cada classe concreta retorna um tipo diferente.
        """
        pass  # Não implementa nada pois isso é como um método virtal da classe SistemaAutomação


'''
Decorators em pythons (@abstractmethod, por exemplo) são açucares sintáticos para alterar classes ou funções de forma legível e reversível.
Neste caso, funciona como uma função de alta ordem (função capaz de receber funções como parâmetro e/ou retorná-las)
'''