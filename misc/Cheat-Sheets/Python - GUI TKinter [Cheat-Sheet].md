# Tkinter GUI Development [Cheat-Sheet & Reference]
> **Foco:** Desenvolvimento de interfaces gráficas desktop em Python (bibloitoeca Nativa).

> **Contexto:** Manutenção do `AutoTRI` (migração de script funcional para OOP).

> **Link Documentação:** [Documentação TKINTER - PYTHON](https://docs.python.org/pt-br/3.12/library/tk.html)

> **Sobre Fontes no TKinter**: [GeeksForGeeks - Com Exemplos](https://www.geeksforgeeks.org/python/how-to-change-the-tkinter-label-font-size/)

---

## 1. Exemplo Label e Entry (sintaxe)

Entendo a lógica de instanciação e renderização/posicionamento de widgets básicos do TKinter.

```python
# --- 1. CRIANDO O RÓTULO (LABEL) ---
# Abordagem: "Fire and Forget" (Disparar e Esquecer)
# Motivo: Não precisamos ler nem alterar esse texto depois (é estático).

tk.Label(
    self.root,              # Pai (Parent/Master): O widget pertence à janela principal.
    text="Usuário SIGEDE:"  # Propriedade: O texto que será exibido.
).grid(                     # Geometria: Posiciona imediatamente na tela.
    row=0, 
    column=0, 
    sticky="w",             # 'w' (West/Oeste): Alinha o texto à esquerda da célula.
    padx=5, pady=5          # Padding: Margens externas (pixels) para respiro.
)
# Nota: O objeto Label é criado na memória, desenhado e a referência Python é perdida.
# O Tkinter (Tcl/Tk engine) mantém ele vivo visualmente.


# --- 2. CRIANDO O CAMPO DE TEXTO (ENTRY) ---
# Abordagem: "Instanciar, Guardar, depois Posicionar"
# Motivo: Precisamos ler o input do usuário depois (usando .get()).

# Passo A: Instanciação e Atribuição Dinâmica
# Criamos o objeto e o "amarramos" à instância da classe (self).
# Em Python, atributos podem ser criados dinamicamente em qualquer método.
self.entry_usuario_sigede = tk.Entry(self.root) 

# Passo B: Posicionamento
# Pegamos o objeto guardado e aplicamos a geometria.
self.entry_usuario_sigede.grid(
    row=2,                  # Linha da grade (inteiro, começa em 0).
    column=1,               # Coluna da grade.
    padx=5, pady=5
)

```

---

## 2. Gerenciadores de Geometria (Layout)

O Tkinter tem 3 formas de posicionar elementos. **Nunca misture `pack` e `grid` no mesmo container (Frame/Janela), ou a aplicação travará.**

### A. `.grid()` (O Planilha Excel)

O mais poderoso para formulários e layouts estruturados. Divide a janela em linhas e colunas invisíveis.

**Parâmetros Principais:**

* **`row` / `column**`: Inteiros (0, 1, 2...). Não aceita floats.
* **`rowspan` / `columnspan**`: Faz o widget ocupar X linhas ou colunas (mesclagem de células).
* **`padx` / `pady**`: Margem externa (pixels).
* **`ipadx` / `ipady**`: Margem interna (aumenta o tamanho do widget).
* **`sticky`**: Pontos cardeais para alinhar ou esticar o widget dentro da célula.
* `"n", "s", "e", "w"` (Cima, Baixo, Dir, Esq).
* `"ns"` (Estica verticalmente).
* `"ew"` (Estica horizontalmente).
* `"nsew"` (Estica em todas as direções / Preenche tudo).

### 2.A.1 - Grid Dinâmico e Introspecção

Ao contrário de arrays ou matrizes fixas, o Grid do Tkinter é **elástico e infinito**.
* **Dimensão:** Não é necessário declarar o tamanho (ex: 10x10). Se você colocar um widget na `row=100`, o Tkinter cria essa linha.
* **Colapso:** Linhas e colunas vazias têm **tamanho zero** (0 pixels) a menos que configuradas com peso.

## Tornando Responsivo (`weight`)
Para que botões ou áreas aumentem/diminuam quando a janela é redimensionada, você deve configurar o **peso** da linha ou coluna no container pai.

```python
# A coluna 0 ocupará todo o espaço extra disponível
root.grid_columnconfigure(0, weight=1)

# Se tiver duas colunas com weight=1, elas dividem o espaço (50%/50%)
root.grid_columnconfigure(1, weight=1)
```

### **Responsividade (O Segredo):**
Para o Grid funcionar bem ao maximizar a janela ou botões ou áreas aumentem/diminuam quando a janela é redimensionada, você deve configurar o **peso** das linhas/colunas no container pai:

```python
# A coluna 1 vai crescer se a janela esticar
root.grid_columnconfigure(1, weight=1) 
# A linha 5 vai crescer verticalmente
root.grid_rowconfigure(5, weight=1)

```


## Introspecção do Grid

Métodos úteis para lógica dinâmica (descobrir onde colocar o próximo item):

* **`.grid_size()`**: Retorna uma tupla `(colunas, linhas)` representando o índice da **próxima** célula disponível (tamanho total atual).
* **`.grid_slaves(row=x, column=y)`**: Retorna uma lista de widgets que estão dentro de uma célula específica (ou todos se não passar argumentos).

## Exemplo Prático: Grid Dinâmico

Este script demonstra como preencher um grid sequencialmente e manter a responsividade.

```python
import tkinter as tk
import random

class GridLab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grid Lab - Responsividade")
        self.geometry("600x400")
        
        # Botão no topo (Pack)
        tk.Button(self, text="Adicionar Item", command=self.add_item).pack(fill="x")

        # Container do Grid (Frame)
        self.grid_frame = tk.Frame(self, bg="#ddd")
        self.grid_frame.pack(fill="both", expand=True)

        # Configura 4 colunas para serem elásticas (dividem a largura da janela)
        self.cols_max = 4
        for i in range(self.cols_max):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def add_item(self):
        # Descobre quantos itens já existem para calcular a próxima posição
        widgets = self.grid_frame.grid_slaves()
        count = len(widgets)
        
        # Matemática de Matriz (Index -> Row/Col)
        proxima_col = count % self.cols_max
        proxima_row = count // self.cols_max

        # Configura a nova linha para ser elástica também
        self.grid_frame.grid_rowconfigure(proxima_row, weight=1)

        # Cria e posiciona
        cor = f"#{random.randint(0, 0xFFFFFF):06x}"
        btn = tk.Button(self.grid_frame, text=f"R:{proxima_row} C:{proxima_col}", bg=cor, fg="white")
        
        # sticky="nsew" faz o botão preencher a célula inteira (crescer)
        btn.grid(row=proxima_row, column=proxima_col, sticky="nsew", padx=2, pady=2)
        
        # Debug: Mostra tamanho atual do grid
        cols, rows = self.grid_frame.grid_size()
        print(f"Dimensão atual do Grid: {cols}x{rows}")

if __name__ == "__main__":
    GridLab().mainloop()

```




### B. `.pack()` (A Pilha de Caixas)

Empilha widgets nas laterais. Bom para barras de botões ou layouts simples.

**Parâmetros Principais:**

* **`side`**: `"top"` (padrão), `"bottom"`, `"left"`, `"right"`.
* **`fill`**: Preenchimento do espaço alocado. `"x"`, `"y"`, `"both"`, `"none"`.
* **`expand`**: `True` (ocupa espaço extra não utilizado), `False`.
* **`anchor`**: Alinhamento (pontos cardeais "n", "sw", "center").

### C. `.place()` (Posicionamento Absoluto)

Coloca o widget em uma coordenada X/Y exata.

* **Uso:** Evite. Quebra facilmente em monitores com resoluções diferentes.
* **Exemplo:** `btn.place(x=50, y=100)`.

---

## 3. Widgets Essenciais (Os Blocos de Construção)

| Widget | Função | Parâmetros Comuns Úteis |
| --- | --- | --- |
| **Label** | Texto estático ou Imagem. | `text`, `image`, `font=("Arial", 12, "bold")`, `bg` (fundo), `fg` (cor texto). |
| **Button** | Botão clicável. | `command` (função sem parênteses), `state` ("normal"/"disabled"). |
| **Entry** | Input de texto (linha única). | `show="*"` (senha), `width` (caracteres). Métodos: `.get()`, `.insert(0, "txt")`, `.delete(0, END)`. |
| **Text** | Input de texto (multilinha). | `height`, `width`. Métodos: `.get("1.0", END)`, `.see(END)` (scroll). |
| **Frame** | Container para agrupar outros widgets. | `bd` (borda), `relief` ("sunken", "raised"). Útil para organizar layouts complexos. |
| **Checkbutton** | Caixa de seleção (On/Off). | `variable` (liga a um BooleanVar), `onvalue`, `offvalue`. |
| **Radiobutton** | Seleção única (várias opções). | `variable` (liga todos a uma mesma var), `value`. |
| **Combobox** | Dropdown (Lista selecionável). | (Do pacote `ttk`). `values=["A", "B"]`, `state="readonly"`. |

### 3.1 Exemplo Completo de uso Sintático
Observemos a função _create_layout(self), na classe da Interface abaixo. Nela podemos ver uma sintaxe dos uso de cada widget com alguns de seus parâmetros.

```python
import tkinter as tk
from tkinter import ttk  # Necessário para Combobox, Progressbar, Notebook
from tkinter import scrolledtext

class WidgetShowcase(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Widgets Cheat-Sheet")
        self.geometry("400x650")

        self._init_vars()
        self._create_layout()

    def _init_vars(self):
        """Inicializa variáveis de controle (binding)."""
        self.var_nome = tk.StringVar()
        self.var_senha = tk.StringVar()
        self.var_termos = tk.BooleanVar(value=False)
        self.var_genero = tk.StringVar(value="Neutro")
        self.var_pais = tk.StringVar()

    def _create_layout(self):
        # 1. FRAME (Container)
        # Útil para agrupar elementos visualmente.
        # bd=Borda, relief="groove" (efeito visual 3D)
        main_frame = tk.Frame(self, bd=2, relief="groove", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 2. LABEL (Texto Estático)
        # fg=Cor da fonte, font=(Familia, Tamanho, Estilo)
        lbl_title = tk.Label(main_frame, text="Cadastro de Usuário", font=("Arial", 14, "bold"), fg="#333")
        lbl_title.pack(pady=(0, 15)) # pady=(Cima, Baixo)

        # 3. ENTRY (Input de Linha Única)
        # Liga à variável self.var_nome
        tk.Label(main_frame, text="Nome Completo:").pack(anchor="w")
        self.ent_nome = tk.Entry(main_frame, textvariable=self.var_nome, width=40)
        self.ent_nome.pack(pady=5)

        # ENTRY com Máscara (Senha)
        # show="*" substitui caracteres digitados
        tk.Label(main_frame, text="Senha:").pack(anchor="w")
        self.ent_senha = tk.Entry(main_frame, textvariable=self.var_senha, show="*", width=40)
        self.ent_senha.pack(pady=5)

        # 4. COMBOBOX (Dropdown - Pacote ttk)
        # values=Lista de opções, state="readonly" (impede digitar valor novo)
        tk.Label(main_frame, text="País:").pack(anchor="w")
        self.combo_pais = ttk.Combobox(main_frame, textvariable=self.var_pais)
        self.combo_pais["values"] = ["Brasil", "Argentina", "Uruguai", "Outro"]
        self.combo_pais.current(0) # Seleciona o primeiro índice por padrão
        self.combo_pais.pack(fill="x", pady=5)

        # 5. RADIOBUTTON (Seleção Única)
        # Todos compartilham a MESMA variável (self.var_genero), mas têm VALUES diferentes.
        lbl_radio = tk.Label(main_frame, text="Gênero:", font=("Arial", 10, "italic"))
        lbl_radio.pack(anchor="w", marginTop=10)
        
        radio_frame = tk.Frame(main_frame) # Frame aninhado para alinhar lado a lado
        radio_frame.pack(anchor="w")
        
        tk.Radiobutton(radio_frame, text="Masculino", variable=self.var_genero, value="M").pack(side="left")
        tk.Radiobutton(radio_frame, text="Feminino", variable=self.var_genero, value="F").pack(side="left")
        tk.Radiobutton(radio_frame, text="Outro", variable=self.var_genero, value="Neutro").pack(side="left")

        # 6. TEXT (Input Multilinha)
        # ScrolledText é um Text + Scrollbar vertical automático
        tk.Label(main_frame, text="Biografia:").pack(anchor="w", pady=(10, 0))
        self.txt_bio = scrolledtext.ScrolledText(main_frame, height=4, width=40)
        self.txt_bio.pack(pady=5)
        # Inserir texto padrão:
        self.txt_bio.insert("1.0", "Digite sua biografia aqui...") 

        # 7. CHECKBUTTON (Caixa de Seleção)
        # onvalue/offvalue definem o que é salvo na variável (padrão é 1/0 ou True/False)
        self.chk_termos = tk.Checkbutton(
            main_frame, 
            text="Aceito os Termos de Uso", 
            variable=self.var_termos,
            onvalue=True, 
            offvalue=False
        )
        self.chk_termos.pack(pady=10)

        # 8. BUTTON (Ação)
        # command=Função (sem parênteses)
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        self.btn_salvar = tk.Button(
            btn_frame, 
            text="Salvar Dados", 
            bg="#4CAF50", fg="white", # Cores (Fundo/Texto)
            command=self._imprimir_dados
        )
        self.btn_salvar.pack(side="right", padx=5)

        self.btn_limpar = tk.Button(btn_frame, text="Limpar", command=self._limpar_form)
        self.btn_limpar.pack(side="right")

    def _imprimir_dados(self):
        """Exemplo de como recuperar os valores."""
        print("--- DADOS ---")
        print(f"Nome: {self.var_nome.get()}") # Via Variável
        print(f"Senha: {self.ent_senha.get()}") # Via Widget direto
        print(f"País: {self.combo_pais.get()}")
        print(f"Gênero: {self.var_genero.get()}")
        # Text Widget precisa de índices ("linha.coluna" até "fim")
        print(f"Bio: {self.txt_bio.get('1.0', tk.END).strip()}") 
        print(f"Termos Aceitos? {self.var_termos.get()}")

    def _limpar_form(self):
        self.var_nome.set("")
        self.var_senha.set("")
        self.var_pais.set("")
        self.var_genero.set("Neutro")
        self.var_termos.set(False)
        self.txt_bio.delete("1.0", tk.END) # Limpa widget Text

if __name__ == "__main__":
    app = WidgetShowcase()
    app.mainloop()
```


---

## 4. Variáveis de Controle (Tkinter Variables)

Em vez de manipular widgets diretamente (`entry.get()`), o Tkinter permite criar variáveis especiais que se **sincronizam automaticamente** com a interface.

* `tk.StringVar()`
* `tk.IntVar()`
* `tk.BooleanVar()`

**Exemplo:**

```python
# Cria a variável
self.nome_var = tk.StringVar()
self.nome_var.set("Texto Inicial")

# Amarra ao Entry
entry = tk.Entry(self.root, textvariable=self.nome_var)

# Leitura (sem acessar o widget)
print(self.nome_var.get()) 

# Escrita (atualiza a tela automaticamente)
self.nome_var.set("Novo Valor") 

```

---

## 5. Eventos e Binding

Permite reagir a ações do usuário que não são apenas "clicar num botão".

**Sintaxe:** `widget.bind('<Evento>', funcao_callback)`

**Eventos Comuns:**

* `<Return>`: Tecla Enter.
* `<Key>`: Qualquer tecla.
* `<Button-1>`: Clique esquerdo do mouse.
* `<FocusIn>` / `<FocusOut>`: Usuário entrou/saiu do campo.
* `<Configure>`: A janela foi redimensionada.

**Exemplo:**

```python
def ao_apertar_enter(event):
    print("Enter pressionado!")

self.entry_usuario.bind('<Return>', ao_apertar_enter)

```

---

## 6. Threading e Performance (Não travar a GUI)

O Tkinter roda em um loop infinito (`mainloop`). Se você colocar um `time.sleep(10)` ou rodar o Selenium na thread principal, a janela congela ("Não Respondendo").

### O Jeito Certo:

1. **Processamento Pesado:** Rode em uma `threading.Thread`.
2. **Atualização de GUI:** A thread secundária **não deve** tocar na GUI diretamente. Ela deve atualizar dados (filas/variáveis).
3. **Polling (`root.after`):** A GUI verifica periodicamente se há novidades e se atualiza.

```python
# Agendamento de Tarefa (Polling)
# Executa 'self.atualizar_logs' a cada 1000ms (1s) sem travar a interface
self.root.after(1000, self.atualizar_logs)

```

---

## 7. Protocolos de Janela

Intercepta comandos do sistema operacional para a janela.

* **`WM_DELETE_WINDOW`**: Ocorre quando o usuário clica no "X" para fechar.

```python
def fechar_seguro():
    if messagebox.askokcancel("Sair", "Deseja fechar?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", fechar_seguro)

```
---
---
# 8. Sobre Unidades de Medida no TKinter


## 8.1. A "Regra de Ouro" (Texto vs. Gráfico)

* **Se o Widget serve para exibir TEXTO** (`Label`, `Entry`, `Button`, `Text`):
* As medidas (`width`, `height`) são em **CARACTERES** (média da largura da letra '0' na fonte atual).


* **Se o Widget serve para LAYOUT ou IMAGEM** (`Frame`, `Canvas`, `Progressbar`, padding):
* As medidas são em **PIXELS** de tela.



---

## 8.2. Análise Detalhada

### A. Unidades de Texto (Caracteres)

Usado em: `tk.Entry`, `tk.Label`, `tk.Button`, `tk.Text`, `scrolledtext.ScrolledText`.

* **`width`:** Número de caracteres.
* `width=30` no seu `Entry` significa: "Largo o suficiente para caberem aproximadamente 30 letras".
* **Pegadinha:** Se você aumentar o tamanho da fonte (`font=("Arial", 20)`), o widget vai crescer em pixels, mesmo mantendo `width=30`, porque a letra ficou maior.


* **`height`:** Número de linhas.
* `height=5` no seu `ScrolledText` significa: "Alto o suficiente para mostrar 5 linhas de texto".
* *Nota:* `tk.Entry` não tem `height` (é sempre 1 linha).



### B. Unidades de Tela (Pixels)

Usado em: `tk.Frame`, `tk.Canvas`, `ttk.Separator`, gerenciadores de geometria (`grid`, `pack`).

* **`width` / `height`:** Tamanho exato em pixels.
* Se você criar um `tk.Frame(width=100, height=100)`, ele será um quadrado de 100x100 pixels.


* **`padx` / `pady`:** Espaçamento em pixels.
* `padx=5` no `.grid()` significa "adicione 5 pixels de ar vazio nas laterais".



### C. O Caso do `ttk.Progressbar`

O `Progressbar` é um widget gráfico, não textual. Portanto, ele usa pixels.

* **`length`:** É a medida do "comprimento" da barra (o lado longo).
* `length=700` significa **700 pixels** fixos.
* *Por que não width?* Porque se você mudar a orientação para `vertical`, o `length` vira a altura. O `width` no Progressbar (em alguns temas) define a "gordura" da barra.



---

## 8.3. Tabela de Referência Rápida

| Parâmetro | Onde é usado? | Unidade de Medida |
| --- | --- | --- |
| **`width`** | `Entry`, `Label`, `Button`, `Text` | **Caracteres** (aprox. largura do '0') |
| **`width`** | `Frame`, `Canvas`, `rectangles` | **Pixels** |
| **`height`** | `Label`, `Text`, `Button` | **Linhas de Texto** |
| **`height`** | `Frame`, `Canvas` | **Pixels** |
| **`length`** | `ttk.Progressbar`, `ttk.Scale` | **Pixels** (comprimento da barra) |
| **`padx` / `pady**` | `.grid()`, `.pack()`, widgets | **Pixels** (espaço em branco) |
| **`wraplength`** | `Label` (para quebrar texto) | **Pixels** (apesar de ser um widget de texto!) |

### 8.4. Como especificar unidades explicitamente (Avançado)

O Tkinter aceita strings com sufixos para forçar uma unidade (Screen Units), embora seja raro usar isso em `Entry` ou `Text`.

* `"10c"` = 10 Centímetros
* `"10i"` = 10 Polegadas (Inches)
* `"10p"` = 10 Pontos (Tipografia)

**Exemplo:**

```python
# Força um Frame a ter 5 centímetros de largura
frame = tk.Frame(root, width="5c", height="2c")

```
---
### Na Interface do AutoTri

* Os `Entry/Label (width=30)` são **30 caracteres**.
* A  `Progressbar(length=700)` são **700 pixels**.
* Os `padx=5` são **5 pixels**.