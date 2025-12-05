from .process import processar_indice, processar_protocolo
# importa as funções processa_indice e processar_protocolo do módulo process.py no mesmo diertório

""" Traz os métodos importados para o namespace do pacote pipeline - resolvendo as funções (útil na hora de importar no arquivo main.py)"""
__all__ = [
    "processar_indice",
    "processar_protocolo",
]
