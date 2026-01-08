# 📚 Comandos de Referência Rápida (Git, Python, WSL/Linux)

Este arquivo contém comandos essenciais para o fluxo de desenvolvimento, instalação de ferramentas e gerenciamento de ambiente.

---

## 💻 Gerenciamento de Código (Git)

### 1. Branches e Fluxo de Trabalho
| Comando | Descrição |
| :--- | :--- |
| `git checkout -b <nome da branch>` | Cria uma nova branch e migra para ela. (Foi substituído por `git switch -c`)[cite_start]. [cite: 1] |
| `git switch <nome da branch>` | [cite_start]Migra para uma branch existente. [cite: 2] |
| `git branch` | Checa a lista de branches locais e mostra a atual. |
| `git push -u origin <branch_name>` | [cite_start]Liga o branch local (`-u` ou `--set-upstream`) a um branch homônimo no repositório remoto (`origin`) e faz o push. [cite: 1] |

### 2. Inicialização e Conexão de Repositório (Primeiro Setup)
| Comando | Descrição |
| :--- | :--- |
| `git init` | Inicializa um repositório Git local. |
| `git add -A` | Adiciona todos os arquivos novos, modificados e deletados ao staging area. |
| `git commit -m "Mensagem"` | Registra as alterações staged no histórico local. |
| `git remote add origin <url>` | Liga o repositório local a um repositório remoto (ex: GitHub). |
| `git remote -v` | Verifica as URLs remotas configuradas. |
| `git push --set-upstream origin main` | Faz o primeiro push, criando o branch `main` no remoto e o configurando para rastreamento. |

### 3. Configuração de Editor
| Comando | Descrição |
| :--- | :--- |
| `git config --global core.editor "code --wait"` | Define o VS Code como o editor padrão do Git (para comandos como `git commit` sem a flag `-m`). |

---

## 🐍 Ambiente Python (Virtual Environment)

| Comando | Descrição |
| :--- | :--- |
| `python3 -m venv venv` | Cria um ambiente virtual Python isolado chamado `venv` na pasta atual. |
| `source venv/bin/activate` | Ativa o ambiente virtual (Necessário em Linux/WSL). |
| `deactivate` | Sai do ambiente virtual. |
| `pip install <nome>` | Instala uma biblioteca, módulo ou dependência no ambiente Python ativo. |

---

## ⚙️ Atalhos de Shell (Aliases)

Os *aliases* criam comandos curtos para comandos longos no terminal.

| Tipo de Alias | Sintaxe | Como Tornar Persistente (WSL/Ubuntu) |
| :--- | :--- | :--- |
| **Temporário** | `alias gs='git status -sb'` | Defina diretamente no terminal. Expira ao fechar a sessão. |
| **Persistente** | `alias venv-on='source venv/bin/activate'` | Adicione a definição no final do arquivo `~/.bashrc` e execute `source ~/.bashrc` para aplicar imediatamente. |

---

## 🐧 Instalação de Ferramentas (WSL/Ubuntu)

### 1. Instalação Básica do VS Code
| Comando | Descrição |
| :--- | :--- |
| `sudo apt update -y` | [cite_start]Atualiza a lista de pacotes disponíveis. [cite: 3] |
| `sudo apt install gnupg2 software-properties-common apt-transport-https curl -y` | [cite_start]Instala pacotes necessários para gerenciar chaves e repositórios. [cite: 3] |
| `curl -sSL ... | sudo apt-key add -` | [cite_start]Importa a chave pública da Microsoft para autenticar o repositório do VS Code. [cite: 4] |
| `sudo add-apt-repository "..." -y` | Adiciona o repositório oficial do VS Code. |
| `sudo apt install code -y` | Instala o VS Code. |
| `sudo apt-get install g++` | Instala o compilador G++ (necessário para certas dependências Python ou C/C++). |

### 2. Gerenciamento de Pacotes e Buscas
| Comando | Descrição |
| :--- | :--- |
| `installar .deb` | Use `dpkg -i <nome_do_arquivo.deb>`. |
| `flatpak` | Subsistema para instalar e gerenciar aplicativos no Debian (ex: Firefox). |
| `grep -Rn "texto"` | Procura a string de forma recursiva (`R`) e mostra o número da linha (`n`) em subpastas. |
| `grep "string" *` | Procura a string apenas nos arquivos da pasta atual. |
| `vmc stop arcvm` | Comando específico para parar o container Android (arcvm). |

(...)

---
---

# 🧹 Manipulação de Metadados e Arquivos de Sistema (Windows / Python)

### 💻 Comandos de Remoção Recursiva

#### Bash (Linux / WSL)

```bash
# REMOÇÃO RECURSIVA: :Zone.Identifier & __pycache__

# Remove arquivos de metadados do Windows (:Zone.Identifier)
find . -name "*:Zone.Identifier" -type f -delete

# Remove diretórios de cache do Python (__pycache__)
# O uso de -exec rm -rf é necessário para garantir a remoção de pastas não vazias
find . -name "__pycache__" -type d -exec rm -rf {} +

```

#### PowerShell (Windows)

```powershell
# REMOÇÃO RECURSIVA: :Zone.Identifier & __pycache__

# Remove arquivos de metadados do Windows (:Zone.Identifier)
Get-ChildItem -Path . -Recurse -Filter "*?Zone.Identifier" -File | Remove-Item -Force

# Remove diretórios de cache do Python (__pycache__)
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force

# PREVENÇÃO: Remove o bloqueio de zona antes da transferência para o WSL
Get-ChildItem -Recurse | Unblock-File

```

---

### 🔍 Detalhamento Técnico dos Argumentos (Breakdown)

A execução dos comandos baseia-se nos seguintes parâmetros de filtragem e ação:

**No Bash (Linux):**

* `-name`: Define o padrão de busca (utiliza coringas como `*` para capturar sufixos).
* `-type f`: Filtra exclusivamente **arquivos** (files). Utilizado para metadados.
* `-type d`: Filtra exclusivamente **diretórios** (directories). Utilizado para caches.
* `-delete`: Remove os itens encontrados de forma direta.
* `-exec rm -rf {} +`: Executa a remoção forçada e recursiva. O símbolo `{}` representa o caminho encontrado e o `+` otimiza a execução para múltiplos itens.

**No PowerShell (Windows):**

* `-Recurse`: Varre todos os subdiretórios a partir da origem.
* `-Filter`: Aplica a busca pelo nome específico (processamento mais rápido que `-Include`).
* `-File`: Restringe a seleção a arquivos.
* `-Directory`: Restringe a seleção a pastas.
* `-Force`: Ignora restrições de leitura ou confirmações de segurança do sistema.

---

### 🛡️ Desativação Global de Metadados de Zona (Windows)

A configuração abaixo impede que o Windows anexe metadados de transferência aos arquivos baixados, eliminando a criação futura de arquivos `:Zone.Identifier`.

#### Opção 1: Editor de Política de Grupo Local (GPEDIT)

*Compatível com Windows Pro/Enterprise*

1. Executar (`Win + R`) **gpedit.msc**.
2. Caminho: **Configuração do Usuário** > **Modelos Administrativos** > **Componentes do Windows** > **Gerenciador de Anexos**.
3. Política: **Não preservar informações de zona em anexos de arquivos**.
4. Configuração: **Habilitado**.

#### Opção 2: Registro do Windows (PowerShell Admin)

*Compatível com todas as versões (Home/Pro)*

```powershell
# Define a política de anexos para não salvar informações de zona
$path = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\Attachments"
if (-not (Test-Path $path)) { New-Item -Path $path -Force }
Set-ItemProperty -Path $path -Name "SaveZoneInformation" -Value 1

```

**Nota de Segurança:** A desativação desta funcionalidade remove o alerta de segurança do Windows ao executar arquivos desconhecidos baixados da internet.

---
