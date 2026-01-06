
# Selenium - Automatização Web [Cheat-Sheet]

> **Foco:** Automação Web com Python/Selenium.
> **Contexto:** Manutenção de bots, interação com DOM e estratégias de resiliência.
> **Dependências:** Selenium é uma biblioteca de automação de navegadores (quaisquer que sejam). Nesta aplicação, AutoTri, até então está definido que a automação acontece no Chrome - portanto, neste caso, o chrome é uma dependência externa até então.

---

## 1. 🧭 Localizadores (A Bússola)

Para interagir com um elemento, o Selenium precisa encontrá-lo na árvore do DOM (Document Object Model). A estratégia de localização define a robustez do seu bot.

**Importação Necessária:**

```python
from selenium.webdriver.common.by import By

```

### XPath: A Ferramenta Universal

XPath é uma linguagem de query para selecionar nós em um documento XML/HTML. É a estratégia mais flexível para elementos complexos ou sem ID.

| Sintaxe | Significado | Exemplo Prático |
| --- | --- | --- |
| `//` | Busca em **qualquer lugar** (recursivo). | `//div` (Todos as divs da página) |
| `/` | Busca o filho **direto** (imediato). | `//div/span` (Span que é filho direto de div) |
| `[]` | Filtro de condições. | `//input[@name='login']` |
| `@` | Seleciona um **atributo**. | `//button[@id='submit']` |
| `*` | Curinga (qualquer tag). | `//*[@id='main']` |

#### Funções Úteis de XPath

* **`contains(@attr, 'valor')`**: Busca parcial. Vital para classes dinâmicas ou IDs longos gerados por frameworks.
* *Ex:* `//div[contains(@class, 'q-drawer')]` (Pega `q-drawer-container`, `q-drawer-open`, etc).


* **`text()='Valor'`**: Busca pelo texto exato visível.
* *Ex:* `//button[text()='Salvar']`.


* **`contains(text(), 'Valor')`**: Busca parcial de texto.
* *Ex:* `//a[contains(text(), 'Imprimir')]`.


* **Lógica (`and`/`or`)**: Combina condições.
* *Ex:* `//input[@type='password' and @name='senha']`.

### Outros Localizadores Úteis

Embora o XPath resolva tudo, outros seletores podem ser mais performáticos ou legíveis:

* **`By.ID`**: A opção mais rápida e segura, se o elemento tiver um ID único e estático.
* *Ex:* `driver.find_element(By.ID, "username")`.


* **`By.CSS_SELECTOR`**: Sintaxe nativa do CSS. Mais limpo que XPath para classes, mas pior para texto.
* *Ex:* `button.btn-primary` (Classe), `#header` (ID), `div > span` (Hierarquia).


* **`By.NAME`**: Comum em formulários antigos.
* *Ex:* `driver.find_element(By.NAME, "email")`.

---

## 2. 🐞 Debugging Rápido (Ferramentas do Navegador)

Antes de rodar o código Python, valide seus seletores diretamente no navegador. Isso economiza o tempo de *startup* do bot.

**Atalho Principal:** `F12` ou `Ctrl + Shift + I` (Abre o DevTools).

### A. Inspeção Visual (O "Select Element")

A maneira mais rápida de encontrar o código fonte de um botão ou texto.

1. Clique no ícone **"Select an element"**  no canto superior esquerdo do DevTools (ou use `Ctrl + Shift + C`).
2. Passe o mouse sobre o elemento na página (ele ficará destacado em azul).
3. Clique no elemento. O DevTools pulará automaticamente para a linha correspondente no HTML (DOM).

### B. Testando Seletores no Console

Não "chute" um XPath no Python. Teste se ele funciona e se é único no Console do navegador.

1. No DevTools, clique na aba **Console**.
2. Use as funções de teste nativas do Chrome:

| Tipo | Comando no Console | Retorno |
| --- | --- | --- |
| **XPath** | `$x("//div[@id='menu']")` | Retorna um Array com os elementos encontrados. |
| **CSS** | `$$("div.menu")` | Retorna uma NodeList com os elementos. |

**Como interpretar o retorno:**

* **Array vazio `[]**`: Seu seletor está errado ou o elemento não existe.
* **Array com 1 elemento**: **Perfeito**. É um seletor único.
* **Array com vários elementos**: Seu seletor é genérico demais. O Selenium pegará o primeiro da lista, o que pode ser o elemento errado. Refine seu XPath.

---

## 3. ⏳ Sincronização (Waits)

A web é assíncrona; o seu script é síncrono. Se o script tentar interagir com um elemento antes de ele ser renderizado, ocorrerá `NoSuchElementException`.

**Importações Necessárias:**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

```

### O "Jeito Errado" vs. "Jeito Certo"

* **❌ `time.sleep(5)`:** Pausa forçada.
* *Problema:* Se carregar em 1s, você perde 4s. Se demorar 6s, o script quebra.


* **✅ `WebDriverWait` (Explicit Wait):** Pausa inteligente.
* *Vantagem:* Espera *até* uma condição ser verdadeira ou o tempo estourar. Avança imediatamente assim que possível.



### Condições Esperadas (`EC`) - A Nuance Importante

Escolher a condição errada é a causa #1 de falhas intermitentes ("Flaky tests").

| Condição (`EC. ...`) | O que verifica? | Quando usar? |
| --- | --- | --- |
| **`presence_of_element_located`** | O elemento existe no HTML (DOM)? | Para verificar dados ocultos ou meta-tags. **Cuidado:** O elemento pode estar invisível. |
| **`visibility_of_element_located`** | Existe no DOM **E** tem altura/largura > 0? | Para ler textos ou verificar se algo apareceu na tela. |
| **`element_to_be_clickable`** | É visível **E** está habilitado para interação? | Obrigatório para **botões** e **links**. |
| **`invisibility_of_element`** | O elemento sumiu (ou não existe)? | Útil para esperar um "Loading..." ou Spinner desaparecer antes de prosseguir. |

**Exemplo de Uso:**

```python
wait = WebDriverWait(driver, 10) # Timeout de 10s

# Espera o botão existir E ser clicável
botao = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
botao.click()

```

---

## 4. 🖱️ Interação Híbrida (Nativo vs. JS Injection)

O Selenium tenta simular um usuário real. Às vezes, o site impede isso (elementos sobrepostos por pop-ups transparentes, animações, etc.).

### Interação Nativa (`.click()`)

Simula o mouse do sistema operacional.

* **Validações:** Verifica se o elemento está no *viewport*, se não está coberto e se é interativo.
* **Erro Comum:** `ElementClickInterceptedException` (Algo está na frente).

### Interação via JavaScript (`execute_script`)

A "Marreta". Executa um comando direto na engine JavaScript do navegador, ignorando validações visuais.

```python
# Sintaxe: driver.execute_script(script, *args)
driver.execute_script("arguments[0].click();", elemento)

```

**Conceito de Marshalling (Ponte Python -> JS):**
Quando você passa o objeto `elemento` (Python) como argumento, o Selenium o converte internamente para uma referência ao Nó do DOM (JavaScript). No script JS, ele é acessado via `arguments[0]`.

**Pattern de Resiliência (Try/Except):**

```python
def safe_click(driver, element):
    try:
        # Tenta ser um "bom cidadão" primeiro
        element.click()
    except Exception:
        # Força bruta se falhar
        driver.execute_script("arguments[0].click();", element)

```

---

## 5. 🪟 Navegação e Contexto (Iframes e Abas)

O Selenium só "enxerga" o contexto atual. Se um elemento está dentro de um `<iframe>` ou em uma nova aba, o Selenium dirá que ele não existe até você trocar o foco.

### Iframes (Página dentro de página)

Muito comum em sistemas corporativos antigos ou widgets de login.

```python
# 1. Entrar no Iframe
iframe = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(iframe)

# ... agora você pode interagir com os elementos internos ...

# 2. Sair do Iframe (Voltar para a página principal)
driver.switch_to.default_content()

```

### Janelas e Abas (Window Handles)

Cada aba/janela tem um ID único (`handle`).

```python
janela_principal = driver.current_window_handle

# [Ação que abre nova aba, ex: clicar num link target="_blank"]

# Lista de todas as janelas abertas
todas_janelas = driver.window_handles 

# Trocar para a nova janela (geralmente a última da lista)
for janela in todas_janelas:
    if janela != janela_principal:
        driver.switch_to.window(janela)
        break

# ... fazer algo na nova aba ...

# Fechar aba e voltar
driver.close() 
driver.switch_to.window(janela_principal)

```