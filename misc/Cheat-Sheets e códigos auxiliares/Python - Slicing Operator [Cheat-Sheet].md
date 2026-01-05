# slicing operator, [], Cheat-Sheet

O operador de acesso `[]` sobrecarrega o método especial `__getitem__(self, item)`.
- Para acesso a um único item, como `s[n]`, a chamada se torna `s.__getitem__(n)`.
- Para fatiamento, como `s[inicio:fim:passo]`, o Python cria um objeto `slice` e a chamada se torna `s.__getitem__(slice(inicio, fim, passo))`.

O fatiamento `s[inicio:fim]` funciona como um intervalo matemático `[inicio, fim)`, ou seja, fechado no início (inclusivo) e aberto no fim (exclusivo). Por exemplo, `s[2:7]` pega os elementos dos índices 2, 3, 4, 5 e 6, parando *antes* de chegar ao índice 7.

---
**String de Exemplo:** `s = "abcdefghij"`
---

#### Acesso a um Único Elemento (Indexação)

* **Pegar o 4º elemento (índice 3)**
    * `s[3]` -> `"d"`
    * *Explicação*: Acessa o elemento no índice 3 (a contagem começa em 0).
* **Pegar o último elemento**
    * `s[-1]` -> `"j"`
    * *Explicação*: Índices negativos contam a partir do final.

#### Básico e Cópia

* **A string inteira (cria uma cópia)**
    * `s[:]` ou `s[::]` -> `"abcdefghij"`

#### Prefixos (Pegando o Começo)

* **Os primeiros 4 caracteres**
    * `s[:4]` -> `"abcd"`

#### Sufixos (Pegando o Final)

* **Tudo a partir do índice 6**
    * `s[6:]` -> `"ghij"`
* **Os últimos 4 caracteres**
    * `s[-4:]` -> `"ghij"`
* **Tudo, exceto os 2 últimos caracteres**
    * `s[:-2]` -> `"abcdefgh"`

#### Fatias do Meio

* **Do índice 2 até o 5 (não incluso)**
    * `s[2:5]` -> `"cde"`
* **Usando índices negativos**
    * `s[-5:-2]` -> `"fgh"`

#### Passo (Saltitando)

* **Índices pares (começando do 0)**
    * `s[::2]` -> `"acegi"`
* **Índices ímpares (começando do 1)**
    * `s[1::2]` -> `"bdfhj"`

#### Inversão (Passo Negativo)

* **Inverter a string inteira**
    * `s[::-1]` -> `"jihgfedcba"`
* **Inverter um trecho (do índice 7 ao 4)**
    * `s[7:3:-1]` -> `"hgfe"`