
# Python Workflow: Venv, Pip & PyInstaller

**Sumário:**

1. **VENV (Ambientes Virtuais):** Criação, Ativação, Verificação, Desativação e Exclusão.
2. **PIP (Gerenciamento de Pacotes):** Instalação, Freeze, Diagnóstico e Manutenção.
3. **PYINSTALLER (Distribuição):** Compilação, Breakdown de Argumentos, Dados Extras e Limpeza.


---

## 1. VENV (Ambientes Virtuais)

*O isolamento do projeto. Garante que bibliotecas de um projeto não interfiram em outro.*

### Criação

Cria uma pasta (geralmente chamada `venv` ou `.venv`) contendo uma cópia isolada do Python.

```powershell
python -m venv nome_da_venv

```

### Ativação

Faz o terminal passar a usar o Python e o Pip de dentro da pasta criada.

* **Windows (Powershell):**
```powershell
.\venv\Scripts\activate

```


* **Linux/Mac:**
```bash
source venv/bin/activate

```



### Verificação (Rastreio)

*Fundamental.* Confirma se a ativação funcionou e se você não está instalando coisas no Python global do sistema.

* **Windows:** `where python` (Deve retornar o caminho dentro da pasta `venv`).
* **Linux:** `which python`

### Desativação

Sai do ambiente virtual e volta para o Python do sistema.

```powershell
deactivate

```

### Exclusão (Destruir a Venv)

Não existe comando de "desinstalar". Como a venv é apenas uma pasta, basta deletá-la.

* **Windows:** `rm -r venv` (ou delete pelo Explorer).
* **Linux:** `rm -rf venv`

---

## 2. PIP (Gerenciamento de Dependências)

*O instalador de pacotes. Baixa, remove e lista bibliotecas.*

### Instalação e Atualização

* **Instalar pacote:**
```powershell
pip install nome-do-pacote

```


* **Instalar lista de requisitos (Deploy):**
Lê o arquivo e instala as versões exatas. Usado ao baixar um projeto novo.
```powershell
pip install -r requirements.txt

```


* **Atualizar o próprio PIP:**
Resolve avisos de versão antiga do gerenciador.
```powershell
python -m pip install --upgrade pip

```



### Congelamento (Gerar Requirements)

* **Visualizar na tela:**
Mostra o que está instalado no formato de requirements.
```powershell
pip freeze

```


* **Salvar em arquivo:**
O operador `>` pega a saída do comando e escreve no arquivo.
```powershell
pip freeze > requirements.txt

```



### Diagnóstico e Remoção

* **Listagem Humana:**
Mostra pacotes instalados em formato de tabela (mais limpo que o freeze).
```powershell
pip list

```


* **Detalhes do Pacote (Show):**
Mostra onde o pacote está salvo, autor e versão. Útil para debugar se o Python está "enxergando" a lib correta.
```powershell
pip show nome-do-pacote

```


* **Checagem de Conflitos (Check):**
Verifica se alguma biblioteca está quebrada ou exigindo versões conflitantes.
```powershell
pip check

```


* **Desinstalar:**
Remove um pacote específico.
```powershell
pip uninstall nome-do-pacote

```



---

## 3. PYINSTALLER (Distribuição)

*Transforma scripts `.py` em executáveis `.exe` (Windows) ou binários (Linux).*

### Instalação

```powershell
pip install pyinstaller

```

### Comando Completo (Exemplo Real) - o que uso no AutoTri

Rodando,com a venv ativada, o comando abaixo a partir do diretório que contém a pasta app (e contem a venv), geramos um executável com ícone e num arquivo só.
```powershell
pyinstaller --noconfirm --onefile --windowed --name "AutoTriagem-PBH 1_X" --icon "app/PBH-Iconizado.ico" --paths "app" --add-data "app/PBH-Iconizado.ico;." --clean app/main.py

```

*(O executável será gerado na pasta `dist` e assume-se que o íncone (PBH-Iconizado.ico) está dentro da pasta app)*

### Breakdown dos Argumentos (O que cada um faz)

| Argumento | Função | Quando usar |
| --- | --- | --- |
| `--onefile` | Empacota tudo em um único arquivo `.exe` em vez de uma pasta cheia de arquivos. | Quase sempre, para facilitar o envio. |
| `--onedir` | (Padrão) Cria uma pasta com o `.exe` e várias DLLs soltas. | Apenas se o `--onefile` estiver muito lento para abrir. |
| `--console` | Mantém a janela preta (CMD) aberta ao rodar. | **Desenvolvimento/Debug.** Essencial para ver `print()` e erros. |
| `--noconsole` | Esconde a janela preta (ou `--windowed`). | **Produção.** Para apps com interface gráfica (GUI) ou rodando em background. |
| `--name="X"` | Define o nome do arquivo final (ex: `X.exe`). | Para não ficar com o nome padrão do script (`main.exe`). |
| `--clean` | Limpa o cache de builds anteriores antes de começar. | Sempre que alterar muitas bibliotecas ou se a build falhar. |
| `--icon="icon.ico"` | Adiciona um ícone personalizado ao executável. | Para dar acabamento profissional. O arquivo deve ser `.ico`. |
| `--add-data` | Inclui arquivos não-Python (imagens, drivers, configs) dentro do executável. | Quando seu script depende de arquivos externos. |

### Sintaxe do `--add-data`

A sintaxe muda entre Windows e Linux (separador `;` vs `:`).

* **Formato:** `<arquivo_origem><separador><pasta_destino_dentro_do_exe>`
* **Windows (Exemplo):** Incluir uma imagem `logo.png` na raiz do exe.
```powershell
--add-data "logo.png;."

```


* **Linux:**
```bash
--add-data "logo.png:."

```


### Sintaxe do `--add-data` (Profundo)

**Sintaxe Básica:**
`--add-data "<origem><separador><destino>"`

* **Origem:** Onde o arquivo/pasta está no seu PC *agora*.
* **Separador:** `;` (Ponto e vírgula) no Windows. `:` (Dois pontos) no Linux/Mac.
* **Destino:** Onde o arquivo/pasta vai ficar *dentro* do executável.
* `.` (Ponto) = Raiz do executável (junto com o main.py).
* `pasta` = Cria uma subpasta dentro do executável.



#### 1. Como adicionar Pastas Inteiras

Se você tem uma pasta chamada `assets` cheia de imagens, não adicione uma por uma.

* **Comando:** `--add-data "assets;assets"`
* **O que faz:** Pega a pasta `assets` do seu PC e coloca ela dentro do executável mantendo o nome `assets`.

#### 2. Exemplos de Separadores e Destinos (Windows)

| Comando | O que acontece |
| --- | --- |
| `"foto.png;."` | Copia `foto.png` para a **raiz** do app. |
| `"foto.png;imagens"` | Copia `foto.png` para dentro de uma pasta `imagens/` no app. |
| `"minha_pasta;."` | Copia o **conteúdo** de `minha_pasta` e joga solto na raiz do app (Bagunçado!). |
| `"minha_pasta;assets"` | Copia a pasta inteira e ela continua se chamando `assets` lá dentro (Recomendado). |

---

#### 3. O Comando "Mega" (Exemplo Fictício Completo)

Imagine um bot complexo que precisa de:

1. Um driver do Chrome (`chromedriver.exe`).
2. Uma pasta inteira de ícones (`icones/`).
3. Um arquivo de configuração (`config.json`).
4. Um arquivo de banco de dados (`dados.db`).

Você usa o `--add-data` várias vezes na mesma linha.

**No Windows (Separador `;`):**

```powershell
pyinstaller --noconsole --onefile --name="SuperBot_v1" ^
 --add-data "chromedriver.exe;." ^
 --add-data "icones;midia/icones" ^
 --add-data "config.json;." ^
 --add-data "dados/base.db;database" ^
 main.py

```

*(Nota: O caractere `^` no Powershell/CMD serve apenas para quebrar a linha visualmente e facilitar a leitura. Você pode digitar tudo numa linha só sem ele).*

**Tradução dos comandos acima acima (em prosa):**

1. O `chromedriver.exe` vai para a raiz (`.`).
2. A pasta `icones` do seu PC vai virar uma pasta chamada `midia/icones` dentro do app.
3. O `config.json` vai para a raiz (`.`).
4. O arquivo `base.db` (que estava na pasta `dados` do PC) vai para uma pasta chamada `database` dentro do app.

---

### ⚠ Nota Crítica 

Adicionar os arquivos é só metade da batalha. O seu código Python precisa saber encontrá-los. Quando você usa `--onefile`, os arquivos são descompactados numa pasta temporária (`sys._MEIPASS`).

Se você usa `open('config.json')`, vai falhar no executável. Você precisa de uma funçãozinha para corrigir o caminho:

```python
import sys
import os

def recurso_path(relative_path):
    """ Retorna o caminho absoluto, funcione via .exe ou via script """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Uso:
# driver_path = recurso_path("chromedriver.exe")

```


