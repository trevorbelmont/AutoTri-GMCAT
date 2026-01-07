from .interface import iniciar_interface

__all__ = ["iniciar_interface"]

'''NOTE: Temos um encapsulamento da interface. Nosso módulo __init__.py do pacote 'gui' da aplicação não devolve, em caso de importação,
acesso à nossa classe InterfaceApp (que é utilizada na funçõa 'iniciar_interface(...), porém de forma encapsulada e secreta).

Vantagens:
- encapsulamento: quem utiliza a main ou trabalha em outra questões da aplicação não precisa saber como a interface funciona (só que funciona)
    Dificulta instanciar objetos de interface desnecessários. 
- Praticidade: o usuário que altera a app/main.py só chama a função simples e já recebe a janela de interface pronta e funcional.add()
Desvantagens:
- Testes Unitários:  Neste caso seria necessário importar a classe e seus métodos com acesso - para testar cada método.add()
- Type Hitting: quando  explicito em outros arquivos.

NOTE: em caso de importar também a classe inteira com acesso pra instanciação e manuseio a linha __all___ ficaria assim:'''
# XXX:  __all__ = ["iniciar_interface", "InterfaceApp"]
