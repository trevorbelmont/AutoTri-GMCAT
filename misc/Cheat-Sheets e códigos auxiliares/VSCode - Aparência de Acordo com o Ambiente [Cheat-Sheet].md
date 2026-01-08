# Cheat-Sheet: Customização de Cores por Ambiente (WSL vs. Nativo)

### 1. Como acessar o arquivo `settings.json`

O VS Code possui diferentes camadas de configuração. Para customizar cores baseadas na conexão, siga estes passos:

1. Abra o **VS Code**.
2. Acesse as **Configurações**: Atalho `Ctrl + ,` (Vírgula) ou vá em *File > Preferences > Settings*.
3. No canto superior direito, clique no ícone **Open Settings (JSON)** (ícone de uma folha com uma seta curvada).
4. **Identifique as Abas:**
* **User:** Configurações globais que valem para qualquer instância (Windows nativo).
* **Remote [WSL: Nome]:** Esta aba **só aparece quando você está conectado ao WSL**. As mudanças feitas aqui só ativam quando o túnel WSL estiver aberto.



---

### 2. Sincronização e Persistência

* **Configurações de Usuário (User):** São vinculadas à sua conta GitHub/Microsoft se o "Settings Sync" estiver ativo. Ao formatar ou trocar de PC, elas são restauradas.
* **Configurações Remotas (Remote/WSL):** Ficam salvas dentro do ambiente WSL (geralmente em `~/.vscode-server/data/Machine/settings.json`). Elas **não** são removidas ao desinstalar o VS Code do Windows, pois residem dentro da distro Linux.
* **Configurações de Workspace:** Ficam na pasta `.vscode/` do projeto. São locais e exclusivas daquele projeto.

---

###3. Exemplos Práticos de Configuração (`settings.json`)
### **NOTA** 
    Copie e cole estes blocos dentro da chave principal `{}` do seu arquivo de configurações. Use cores distintas para a aba **User** (ex: Azul) e para a aba **Remote** (ex: Verde).

## Customização Da Janela, Barra e Painéis Laterais
```jsonc
{
  "workbench.colorCustomizations": {

    // =========================================================================
    // TITLE BAR (Título da Janela ) & ACTIVITY BAR (Barra de Ícones à esquerda)
    // =========================================================================
    
    // --- BARRA DE TÍTULO (Title Bar) ---
    // Controla a parte superior da janela
    "titleBar.activeBackground": "#2e7d32",      // Fundo da barra com foco (janela ativa)
    "titleBar.activeForeground": "#ffffff",      // Cor do texto do título/nome do arquivo
    "titleBar.inactiveBackground": "#1b4d1f",    // Fundo quando a janela perde o foco (você clica fora)
    "titleBar.border": "#ffffff22",              // Borda fina/sutil abaixo da barra (hex + opacidade)
    
    // --- ÍCONES DA BARRA LATERAL (Activity Bar) ---
    "activityBar.background": "#1b4d1f",          // Cor de fundo da barra de ícones
    "activityBar.foreground": "#ffffff",          // Cor do ícone selecionado
    "activityBar.inactiveForeground": "#ffffff66", // Cor dos ícones não selecionados
    "activityBar.border": "#2e7d32",              // Linha divisória vertical à direita da barra
    
    // --- Destaques de Seleção nos Ícones ---
    "activityBar.activeBorder": "#ffffff",        // Linha lateral ao ícone ativo (indicador de foco)
    "activityBar.activeBackground": "#2e7d32",    // Fundo do ícone que está clicado no momento
    "activityBar.activeFocusBorder": "#ff0000",   // Borda do ícone quando selecionado via teclado
    
    // --- Badges (Círculos de notificação, ex: número de updates ou commits) ---
    "activityBarBadge.background": "#ffffff",     // Cor do fundo do círculo de notificação
    "activityBarBadge.foreground": "#1b4d1f",     // Cor do número dentro do círculo
    
    // --- Itens de Arrastar e Soltar ---
    "activityBar.dropBorder": "#ffffff",          // Cor da borda quando você arrasta um ícone para reordenar

    //=============================================================================================================

    // --- BARRA DE ATIVIDADE (Activity Bar) ---
    // Menu lateral estreito onde ficam os ícones (Explorer, Search, Git, Extensions)
    "activityBar.background": "#1b4d1f",         // Fundo da barra lateral de ícones
    "activityBar.foreground": "#ffffff",         // Cor do ícone que está selecionado (ativo)
    "activityBar.inactiveForeground": "#ffffff66", // Cor dos ícones não selecionados
    "activityBar.border": "#2e7d32",             // Linha divisória lateral (separando do editor/sidebar)

    // --- BARRA LATERAL / EXPLORER (Side Bar) ---
    // Área onde aparecem a árvore de arquivos e pastas
    "sideBar.background": "#0e120f",             // Fundo da lista de arquivos (Explorer)
    "sideBar.foreground": "#cccccc",             // Cor da fonte dos nomes dos arquivos e pastas
    "sideBar.border": "#1b4d1f",                 // Divisória vertical entre Explorer e Código
    "sideBarSectionHeader.background": "#2e7d3222", // Fundo dos cabeçalhos de seção (ex: "Outline", "Timeline")

    
    // --- EDITOR E NAVEGAÇÃO DE CÓDIGO ---
    "editor.background": "#121212",              // Cor de fundo principal do código
    "editorLineNumber.foreground": "#2e7d32",    // Cor dos números das linhas (estático)
    "editorLineNumber.activeForeground": "#2e7d32", // Cor de destaque do número da linha atual (onde está o cursor)
    "editorCursor.foreground": "#ffffff",        // Cor do cursor de digitação (o "I" que pisca)
    "breadcrumb.foreground": "#cccccc",          // Cor do caminho do arquivo ("breadcrump") no topo do editor
    "tab.activeBorder": "#2e7d32"                // Linha de destaque sob a aba (Tab) do arquivo aberto
  },
```

## Customização da Região Inferior (onde fica o Terminal)
```jsonc
{
  "workbench.colorCustomizations": {
    // =========================================================================
    // PANEL (Área do Terminal, Output, Problems, Debug Console)
    // =========================================================================

    // --- Cores Gerais do Painel ---
    "panel.background": "#0e120f",             // Cor de fundo do painel inferior
    "panel.border": "#2e7d32",                 // Borda que separa o painel do editor de código
    "panel.dropBorder": "#ffffff",             // Cor da borda ao arrastar painéis para reordenar

    // --- FUNDO E BORDAS ---
    "panel.background": "#0e120f",               // Cor de fundo de todo o painel (incluindo a barra)
    "panel.border": "#2e7d32",                   // Linha que separa o editor do painel

    // =========================================================================
    // STATUS BAR - CAMPOS ESPECÍFICOS (WSL e GIT)
    // =========================================================================

    // --- 1. INDICADOR DE CONEXÃO REMOTA (Canto inferior esquerdo - WSL) ---
    // Este é o campo que mostra "WSL: Ubuntu"
    "statusBarItem.remoteBackground": "#2e7d32",   // Fundo do campo de conexão (Verde vibrante)
    "statusBarItem.remoteForeground": "#ffffff",   // Cor do ícone e do texto "< >"
    
    // --- 2. INDICADOR DE GIT (Branch atual) ---
    // Nota: O VS Code não tem uma chave "statusBarItem.gitBackground".
    // Para destacar o Git, mudamos a cor de hover ou as cores de itens prioritários.
    "statusBarItem.activeBackground": "#ffffff33", // Cor ao clicar em um item da barra
    "statusBarItem.hoverBackground": "#2e7d32aa",  // Cor ao passar o mouse (vibrante)

    // --- 3. CORES GERAIS DE ITENS DA BARRA (Afeta Branch, Erros, Warnings) ---
    "statusBarItem.prominentBackground": "#2e7d32", // Fundo de itens que ganham destaque
    "statusBarItem.prominentForeground": "#ffffff", // Texto de itens que ganham destaque
    "statusBarItem.errorBackground": "#ff0000",     // Fundo quando há erros críticos
    "statusBarItem.warningBackground": "#ffa500",   // Fundo quando há avisos

    // --- REVISÃO DA BARRA INTEIRA (Para contraste) ---
    "statusBar.background": "#1b4d1f",              // Fundo da barra inteira
    "statusBar.foreground": "#ffffffcc",             // Texto padrão (menos vibrante que o WSL)

    "statusBar.noFolderBackground": "#222222",   // Cor de fundo quando não há nenhuma pasta/projeto aberto
    "statusBar.debuggingBackground": "#cc6600",  // Muda a cor automaticamente ao iniciar o Debug (F5)

    
    // --- BOTÕES DE AÇÃO (Maximizar, Fechar o painel no canto direito) ---
    "panel.dropBorder": "#2e7d32",               // Cor ao arrastar uma aba dentro do painel
    "panelSection.border": "#1b4d1f",            // Borda entre seções do painel se ele for dividido
    "panelSectionHeader.background": "#1b4d1f"   // Fundo do cabeçalho de seções divididas

    // --- Títulos das Abas (TERMINAL, OUTPUT, etc.) ---
    "panelTitle.activeForeground": "#ffffff",   // Cor do texto da aba selecionada (ex: TERMINAL)
    "panelTitle.inactiveForeground": "#ffffff66", // Cor das abas não selecionadas
    "panelTitle.activeBorder": "#2e7d32",       // Linha de destaque abaixo da aba ativa

    // --- Seção de Input/Filtro (Problems/Output) ---
    "panelInput.border": "#1b4d1f",            // Borda do campo de busca/filtro dentro do painel

    // --- Cores Específicas do TERMINAL Interno ---
    "terminal.background": "#0e120f",          // Fundo do console
    "terminal.foreground": "#cccccc",          // Cor padrão das letras do terminal
    "terminal.cursorBackground": "#2e7d32",    // Cor do bloco do cursor
    "terminal.cursorForeground": "#ffffff",    // Cor da letra sobre a qual o cursor está
    "terminal.selectionBackground": "#2e7d3255", // Cor do destaque ao selecionar texto com o mouse
    
    // --- Cores de ANSI (Cores que o terminal usa para erros, sucessos, etc) ---
    "terminal.ansiGreen": "#2e7d32",           // Customiza o verde que aparece no terminal (ex: comandos Git)
    "terminal.ansiRed": "#ff0000"              // Customiza o vermelho (ex: erros de compilação)
  }
}

  // --- CUSTOMIZAÇÕES DE FONTE E INTERFACE (Configurações Globais) ---
  
  // Necessário para que algumas customizações de cores da TitleBar funcionem corretamente
  "window.titleBarStyle": "custom",

  // Peso da fonte no editor. Opções comuns: "normal", "bold", "100" a "900"
  "editor.fontWeight": "normal",

  /**
   * DICA DE TÍTULO DINÂMICO:
   * No Windows, não há comando direto para 'bold' no texto da TitleBar via JSON.
   * Mas você pode customizar as informações exibidas no topo da janela:
   * ${dirty}: Indicador de arquivo não salvo
   * ${activeEditorShort}: Nome do arquivo atual
   * ${rootName}: Nome da pasta raiz do projeto
   * ${appName}: Nome do aplicativo (Visual Studio Code)
   */
  "window.title": "${dirty}${activeEditorShort}${separator}${rootName}${separator}${appName}"
}
```

---

### 4. Dicas de Produtividade

* **IntelliSense:** Dentro de `colorCustomizations`, pressione `Ctrl + Space` para ver a lista completa de centenas de elementos editáveis.
* **Color Picker:** Ao pairar o mouse sobre um código hexadecimal (ex: `#2e7d32`), o VS Code abrirá um seletor visual de cores.
* **Opacidade:** Adicione dois dígitos extras ao final do Hexadecimal (00 a FF) para controlar a transparência. Ex: `#00000088` (Preto 50% transparente).

