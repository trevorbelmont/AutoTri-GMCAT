
# 🐍 Guia de Tags e Documentação em Python

## 1. Tags de Comentário (Lembretes e Alertas)

Utilizadas com `#` para organizar o fluxo de trabalho. As IDEs costumam colorir estas tags automaticamente.

```python
# TODO: funcionalidade pendente ou tarefa a ser realizada.
# FIXME: código quebrado que necessita de correção urgente.
# XXX: lógica problemática, ineficiente ou que requer atenção extra.
# HACK: solução temporária, técnica não convencional ou "gambiarra".
# NOTE: explicação sobre o raciocínio ou decisão técnica adotada.
# BUG: registro de um erro conhecido identificado neste trecho.
# REVIEW: pedido de revisão ou segunda opinião sobre a lógica.
# DEPRECATED: alerta de código obsoleto que será removido no futuro.
```

### 2. Docstrings (Documentação Estruturada)

Utilizadas entre `"""` logo abaixo da definição de classes ou funções. Seguem padrões como Google Style ou reStructuredText (reST).

###Exemplo de DocString em Métodos:

```python
def processar_pedido(cliente_id, itens, urgente=False):
    """
    Explica o que este método (ou classe) é e/ou faz.
    NOTE: [Uma Linha em branco é obrigatória entre a explicação do método/classe e os artefatos da DocString (param, return, yelds e etc)].

    :param cliente_id: (int) Explica que o parâmetro client_id é utilizado como int e o que ele representa...
    :param itens: (list) Lista de dicionários contendo 'sku' e 'quantidade'.
    :param urgente: (bool) Define se o pedido deve furar a fila de logística.
    
    :return: (dict) Aqui explica o que é retornado no método (seu tipo e o que é exatamente)
    :yields: esta tag descreve o que um "generator" (gerador) retorna em cada iteração 
             quando a função utiliza a palavra-chave 'yield' em vez de 'return'. 
             Neste exemplo, produziria uma sequência de números.
             
    :raises ValueError: esta tag indica ao desenvolvedor quais exceções (erros) a 
                        função pode disparar intencionalmente. Aqui, indica que um 
                        ValueError será lançado se a 'condicao' for negativa.
    """
    if condicao < 0:
        raise ValueError("A condição não pode ser negativa.")
    
    for i in range(10):
        yield i

```
###Exemplo de DocString em Classes:

```python
class ServidorWeb:
    """
    Comenta a razão de existir, responsabilidade e/ou comportamento (dos objetos) da Classe.

    :deprecated: Esta classe será substituída pela 'ServidorAsync' na v3.0.
    :see: Consulte a documentação da RFC 7231 para métodos suportados.
    """
    pass

```

---

### Resumo das Diferenças

| Recurso | Escopo | Público-alvo | Ferramenta |
| --- | --- | --- | --- |
| **Tags (`#`)** | Lógica interna | O desenvolvedor que está lendo/editando o código. | IDE (Todo Tree, PyCharm) |
| **Docstrings (`"""`)** | Interface (API) | Quem vai **usar** a sua função ou classe em outros módulos. | `help()`, Sphinx, Pydoc |
