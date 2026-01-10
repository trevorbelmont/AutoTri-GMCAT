# function decorators : @decorator

### O que é um Decorator?

Um **decorator** em Python é, em sua essência, uma função que "decora" ou "embrulha" outra função para adicionar uma nova funcionalidade a ela, sem alterar o código da função original.

Pense nisso como colocar uma função em uma "caixa de presente". A função original é o presente, e o decorator é a caixa com o laço, que adiciona algo a mais à apresentação e ao comportamento.

Tecnicamente, a sintaxe com o símbolo `@` é um "açúcar sintático" (uma forma mais legível) para uma operação padrão: passar uma função como argumento para outra.

Por exemplo, escrever isto:

```python
@meu_decorator
def ola():
    print("Olá!")
```

É exatamente o mesmo que escrever isto:

```python
def ola():
    print("Olá!")

# A função 'ola' é passada para o decorator,
# e a variável 'ola' agora aponta para a nova função (modificada) que o decorator retornou.
ola = meu_decorator(ola)
```

-----

### `@classmethod`

  * **O que é:** Transforma um método para que ele receba a **classe** como o primeiro argumento, em vez da instância.
  * **Sintaxe:**
    ```python
    @classmethod
    def nome_do_metodo(cls, arg1, arg2, ...):
        # ...
    ```
  * **Primeiro Argumento:** A própria classe, convencionalmente chamada de `cls`.
  * **Quando Usar:** Principalmente para criar "métodos de fábrica" (factory methods), que são construtores alternativos. Útil quando você precisa criar uma instância da sua classe a partir de um tipo de dado diferente (ex: um dicionário, uma string formatada, etc.).
  * **Exemplo Prático:**
    ```python
    import datetime

    class Pessoa:
        def __init__(self, nome, idade):
            self.nome = nome
            self.idade = idade

        @classmethod
        def a_partir_do_ano_de_nascimento(cls, nome, ano_nascimento):
            ano_atual = datetime.date.today().year
            idade = ano_atual - ano_nascimento
            # 'cls' é a classe Pessoa, então cls(...) é o mesmo que Pessoa(...)
            return cls(nome, idade)

    # Uso:
    p1 = Pessoa("Ana", 25)
    p2 = Pessoa.a_partir_do_ano_de_nascimento("Beto", 2000)

    # A idade é calculada com base na data atual da execução.
    print(f"A idade de Beto é: {p2.idade}")
    ```

-----

### `@staticmethod`

  * **O que é:** Transforma um método em uma função normal que "mora" dentro da classe. Ele não recebe nenhum primeiro argumento especial (nem a instância `self`, nem a classe `cls`).
  * **Sintaxe:**
    ```python
    @staticmethod
    def nome_do_metodo(arg1, arg2, ...):
        # ...
    ```
  * **Primeiro Argumento:** Nenhum.
  * **Quando Usar:** Para funções utilitárias que têm uma conexão lógica com a classe, mas não dependem de nenhum estado (nem da instância, nem da classe).
  * **Exemplo Prático:**
    ```python
    class ValidadorMatematico:
        @staticmethod
        def eh_par(numero):
            # Este método não precisa saber nada sobre uma instância
            # ou a classe ValidadorMatematico para funcionar.
            return numero % 2 == 0

    # Uso:
    # Note que você pode chamar a partir da classe...
    print(f"10 é par? {ValidadorMatematico.eh_par(10)}") # Saída: True
    # ...ou de uma instância, mas é incomum e não faz diferença.
    val = ValidadorMatematico()
    print(f"7 é par? {val.eh_par(7)}") # Saída: False
    ```

-----

### `@property`

  * **O que é:** Transforma um método em um atributo "getter" (somente leitura). Permite que você acesse o método como se fosse um atributo normal, sem usar parênteses `()`.
  * **Sintaxe:**
    ```python
    @property
    def nome_do_metodo(self):
        # ...
    ```
  * **Primeiro Argumento:** A instância (`self`), pois geralmente calcula um valor com base nos atributos da instância.
  * **Quando Usar:** Para atributos cujo valor é derivado de outros atributos. Isso permite expor uma API limpa, escondendo a lógica de cálculo.
  * **Exemplo Prático:**
    ```python
    class Retangulo:
        def __init__(self, largura, altura):
            self.largura = largura
            self.altura = altura

        @property
        def area(self):
            # Este método é executado quando 'r.area' é acessado.
            return self.largura * self.altura

    # Uso:
    r = Retangulo(10, 5)
    # Acessado como um atributo, não como um método r.area()
    print(f"A área é: {r.area}") # Saída: 50

    # Tentar atribuir um valor a 'r.area' daria um erro,
    # pois por padrão ele é somente leitura.
    # r.area = 100 # AttributeError
    ```