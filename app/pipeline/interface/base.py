from abc import ABC, abstractmethod
#ABC = Abstract Base Class - permite definir classes abstratas em python

# Define um contrato para qualquer classe que herde de SistemaAutomação (que por sua vez herda de ABC, para implementar métodos abstratos)
# Todo bot que herde de SistemaAutomação deve ter pelo menos o método executar(...) implementado com essa assinatura de argumentos
# - a definição do método pode diferir de bot para bot
class SistemaAutomacao(ABC):
    # TODO: Padronizar os parâmetros da interface executar para contemplar todas as classes definidas em app/pipeline/sistemas.py 
    # (GoogleMaps usa mais parâmetros que o definido aqui.) Princípio da Substituição de Liskov
    @abstractmethod # Este decorator, aplicado ao método executar(...) força que qualquer classe filha defina seu próprio método executar
    def executar(self, indice, credenciais, pasta_indice):
        """Executa coleta de dados e retorna os resultados do sistema"""
        pass  # Não implementa nada pois isso é como um método virtal da classe SistemaAutomação


'''
Decorators em pythons (@abstractmethod, por exemplo) são açucares sintáticos para alterar classes ou funções de forma legível e reversível.
Neste caso, funciona como uma função de alta ordem (função capaz de receber funções como parâmetro e/ou retorná-las)
'''