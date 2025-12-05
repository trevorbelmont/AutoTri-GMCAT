from .base import SistemaAutomacao    # Classe abstrata
# importação relativa (diretórios relativos):
# from .<nomeDoMódulo> : o ponto indica que importa o módulo a partir do diretório atual (do arquivo atual)
# from ..<nomeDoutroMódulo> : importaria um módulo do diretório pai.

'''
__init__.py : um diretório contendo um módulo __init__.py é considerado um package (pacote).
Ao importar este diretório/pacote o módulo __init__  é executado primeiro.
O que este módulo tá basicamente fazendo é colocando a classe abstrata SistemaAutomação no mesmo namespace do pacote "interface"
(o que facilita importação) e definindo o que será importado caso outro módulo faça uma importação curinga deste pacote.

'''

__all__ = ["SistemaAutomacao"]
'''
A variável __all__ é uma convenção Python que controla o que é importado quando um usuário faz uma importação curinga (wildcard import *).
Isso encapsula o código previnindo que uma importação wildcard acesso outros métodos que não queremos que sejam importados.
'''
