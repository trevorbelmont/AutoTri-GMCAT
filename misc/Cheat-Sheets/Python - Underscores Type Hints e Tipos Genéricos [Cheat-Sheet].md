# Python Underscores & Type Hints [Cheat-Sheet]

## 1. Convenções de Nomenclatura (Underscores)

O Python NÂO possui modificadores de acesso estritos (`private`, `protected`) no nível da linguagem. O controle é feito via convenção de nomes.

### `_variavel` (Single Leading Underscore)
* **Significado:** "Uso Interno" ou "Protected".
* **Comportamento:**
    * É apenas um aviso para outros programadores.
    * **Importante:** `from modulo import *` **ignora** nomes começando com `_`.
* **Analogia C++:** Membros `protected` (mas acessíveis se você forçar).

### `__variavel` (Double Leading Underscore)
* **Significado:** Evitar colisão de nomes em herança (*Name Mangling*).
* **Comportamento:**
    * O interpretador reescreve a variável `__x` dentro da classe `Base` para `_Base__x`.
    * Torna o acesso externo difícil (mas não impossível).
* **Uso:** Apenas quando há risco real de uma subclasse sobrescrever acidentalmente um atributo interno crítico.
* **Analogia C++:** Membros `private`, com foco em evitar *shadowing*  - ofuscamento de variáveis por colisão de nomes em diferentes escopos (o nome de uma variável interna/local ofusca o acesso à uma variável externa de mesmo nome).

### `__metodo__` (Dunder / Magic Methods) - Dunder = Double Underline
* **Significado:** São métodos especiais reservados pela linguagem Python. Eles não são chamados diretamente pelo nome, mas sim por ações ou operadores.

* **Comportamento Técnico:** Eles definem como seus objetos se comportam com a sintaxe nativa do Python.
* **Uso:** Sobrecarga de operadores e ganchos de ciclo de vida.
    * `__init__`: Construtor.
    * `__str__`: `ToString()`.
    * `__add__`: Operador `+`.
* **Regra de Ouro:** Nunca invente seus próprios nomes assim (ex: ____meu_metodo__ __). Use apenas os que o Python define, pois a linguagem pode criar novos no futuro e quebrar seu código se houver conflito.

### `_` (Lone Underscore / Throwaway)
* **Significado:** "Descartável" ou "Ignorar valor".
* **Uso:** Quando a sintaxe exige uma variável, mas você não vai usá-la.
* **Exemplos:**
    ```python
    # Ignorando o índice do loop
    for _ in range(10):
        print("Repetir")

    # Ignorando valores específicos no desempacotamento
    x, _, z = (10, 20, 30) # x=10, z=30, 20 ignorado
    ```

---

## 2. Type Hints (Tipagem Estática)

O Python é dinâmico, mas Type Hints permitem análise estática (Mypy, Pylance) e documentação. A sintaxe abaixo foca no Python moderno (3.10+).

### Sintaxe Básica
```python
# Variáveis
idade: int = 25
nome: str = "AutoTRI"

# Funções (Parâmetros -> Retorno)
def somar(a: int, b: int) -> int:
    return a + b
```


## 3. Tipos Genéricos (Collections)

Use as classes nativas (lowercase) em vez de importar do módulo `typing`.

```python
# Lista (std::vector)
nomes: list[str] = ["A", "B"]

# Dicionário (std::map)
credenciais: dict[str, int] = {"admin": 1}

# Tupla (std::tuple) - tamanho fixo e tipos mistos
config: tuple[str, int, bool] = ("localhost", 8080, True)

```

### Unions e Optionals (`|`)

Sintaxe moderna introduzida no Python 3.10.

```python
# Union: Aceita int OU float
numero: int | float = 10.5

# Optional: Pode ser str OU None (Nullable)
endereco: str | None = None

```
---
### `Final` e `Any` (Segurança vs. Flexibilidade)

Requer `from typing import Final, Any`.

#### `Final` (Constantes)

Indica que uma variável ou atributo **não deve ser reatribuído** ou sobrescrito em subclasses.

* **Analogia:** `const` (C++) ou `final` (Java).
* **Atenção:** É uma checagem **apenas estática**. O Python *não* impede a alteração em tempo de execução, mas o seu editor (VS Code/Pylance) e o Mypy vão acusar erro.

```python
from typing import Final

# Constante de módulo
MAX_RETRIES: Final[int] = 5

# O código abaixo roda (Python é dinâmico), mas o Linter marcará como ERRO:
# MAX_RETRIES = 6  # ❌ Erro: Cannot assign to Final

class Base:
    # Impede que subclasses sobrescrevam este método
    @final 
    def metodo_critico(self): ...

```

#### `Any` (O "Modo Dinâmico")

É o tipo mais permissivo. Uma variável `Any` aceita qualquer valor e **pode ser usada de qualquer forma** sem que o linter reclame.

* **Analogia:** `void*` (C/C++) ou `Object` (Java), mas sem a necessidade de *casting* explícito.
* **Uso:** Migração gradual de código, bibliotecas sem tipagem ou dados brutos (JSON sem schema).
* **Perigo:** O `Any` "desliga" a segurança da tipagem naquele ponto.

```python
from typing import Any

def processar_payload(dados: Any) -> None:
    # O Linter fica "cego" aqui. Ele assume que você sabe o que está fazendo.
    # Nenhuma destas linhas gerará erro no editor, mesmo que falhem ao rodar:
    dados.fazer_algo()      # ✅ Linter aceita
    print(dados + 10)       # ✅ Linter aceita
    x: str = dados          # ✅ Linter aceita (Any é compatível com tudo)

```
