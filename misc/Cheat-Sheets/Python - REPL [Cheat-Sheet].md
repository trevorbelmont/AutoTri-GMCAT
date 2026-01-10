# Guia de Utilização do REPL Python no VS Code

Este documento descreve os três métodos principais para execução interativa de código Python dentro do Visual Studio Code: a **Janela Interativa (Interactive Window)**, o **Terminal Integrado** e o **Console de Depuração (Debug Console)**.

## Pré-requisitos

Para o correto funcionamento das funcionalidades descritas, é necessário:

1. Ter a extensão **Python** (da Microsoft) instalada no VS Code.
2. Ter a extensão **Pylance** instalada (recomendado para suporte a tipos).
3. Um interpretador Python selecionado no ambiente (`Ctrl + Shift + P` > `Python: Select Interpreter`).

---

## 1. Python Interactive Window (Modo Célula)

Este método oferece uma experiência similar ao Jupyter Notebook, permitindo execução de blocos de código mantendo o estado das variáveis na memória. É ideal para testes de lógica e manipulação de dados.

### Execução

Para enviar código para a janela interativa:

1. Selecione o trecho de código desejado no editor.
2. Pressione `Shift` + `Enter`.
3. A janela abrirá lateralmente exibindo o resultado.

**Definição de Células:**
É possível dividir um arquivo `.py` padrão em células lógicas utilizando o marcador `# %%`. O VS Code exibirá botões "Run Cell" logo acima do marcador.

```python
# %%
import pandas as pd
# Ao clicar em "Run Cell" ou Shift+Enter, apenas este bloco é executado.
df = pd.read_csv('dados.csv')

# %%
# As variáveis da célula anterior persistem na memória.
print(df.head())

```

### Importação de Pacotes

No modo interativo, a importação ocorre na primeira execução da célula que contém o comando `import`.

* **Atenção:** Se o código de um módulo importado for alterado externamente, a Janela Interativa não o atualiza automaticamente. É necessário usar a função de *restart kernel* (botão na topo da Janela Interativa) e rodar as células novamente.

---

## 2. Terminal Integrado (REPL Clássico)

Este é o método padrão de execução via shell, útil para testes rápidos de sintaxe ou verificação de ambiente.

### Inicialização

1. Abra o terminal integrado com `Ctrl + '` (aspas simples) ou via menu *View > Terminal*.
2. Inicie o interpretador:

* **Windows:**
```powershell
python

```


* **Linux / WSL:**
```bash
python3

```


*(Nota: Em sistemas Linux, o comando `python` pode referir-se à versão 2.x ou não existir, a menos que um alias tenha sido configurado).*

### Importação e Recarregamento (Reload)

Diferente da Janela Interativa, o terminal padrão não permite reexecutar imports para atualizar lógica de código modificado sem reiniciar o interpretador. Para contornar isso durante refatorações, utiliza-se a biblioteca `importlib`.

**Exemplo de fluxo de trabalho:**

```python
import meu_modulo

# ... O usuário altera o código dentro de 'meu_modulo.py' ...

# Para refletir as alterações sem fechar o terminal:
import importlib
importlib.reload(meu_modulo)

```

---

## 3. Console de Depuração (Debug Console)

Este método permite interagir com o código paralisado em um ponto específico da execução. É a ferramenta mais robusta para inspeção de escopo local e estado de objetos.

### Configuração de Breakpoints (Pontos de Parada)

1. Localize a linha de código onde a execução deve pausar.
2. Clique na **margem esquerda (gutter)** ao lado do número da linha. Um círculo vermelho aparecerá.
3. Alternativamente, posicione o cursor na linha e pressione `F9`.

### Inicialização

1. Pressione `F5` para iniciar a depuração (selecione "Python File" se solicitado).
2. A execução será interrompida na linha marcada com o breakpoint.

### Utilização do Console

Com a execução pausada, abra a aba **Debug Console** (geralmente localizada na parte inferior, ao lado do Terminal).

* **Inspeção:** Digite o nome de qualquer variável visível no escopo atual para ver seu valor.
* **Execução:** É possível chamar métodos, alterar valores de variáveis ou executar lógica complexa usando o estado atual da aplicação.
```python
# Exemplo no prompt do Debug Console:
usuario.nome = "Novo Nome Teste"  # Altera o valor em tempo real na memória
self.calcular_total()             # Executa um método da classe instanciada

```

Este ambiente tem acesso completo ao contexto local (`locals()`) e global (`globals()`) do ponto onde o código parou.