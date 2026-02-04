# Links Úteis

## Executável de Distribuição
### [Pasta de Distribuição](https://drive.google.com/drive/folders/1vXxPCR9K_Ow2ADIvdMVsAwrsgmXjRu5z?usp=sharing)

## Documentação Parcial
### [Link Doc Parcial](https://drive.google.com/drive/folders/1eS0YmXbdpFn6Romy1wwn3tWkGPOoeIZu?usp=sharing)

## Link deste Repositório
### [Link Repo GitHub - main branch](https://github.com/trevorbelmont/AutoTri-GMCAT)


# **AutoTri \- Versão 1.52a \[Alpha\]  - ChangeLog**

**04/02/2026**

## **Resumo** 

Atualiza usabilidade, segurança e refatora sistemas de automação da navegação automatizada e o sistema de credenciais. Também melhora a depuração e centraliza manutenção do bot-core através de hierarquia de classes.   
	O foco principal foi eliminar riscos no manuseio de dados sensíveis e padronizar o comportamento dos robôs para facilitar manutenções futuras e escalabilidade. Também implementa auto-complete de campos via CredentialManager (e passagem de argumentos) e implementa um maior controle de variáveis comuns na automação da navegação de forma simples, possibilitando automatização do próprio AutoTri e maior independência da Interface Gráfica.

* **🔐 Segurança de Dados (Novo Módulo de Credenciais):** Implementação de uma blindagem no fluxo de autenticação. O sistema agora recebe de forma centralizada credenciais de forma automatizada e segura \- e também garante que senhas sejam removidas ("limpas") da memória do computador imediatamente após o uso. Elevando o nível de compliance e segurança da ferramenta.  
* **🏗️ Padronização dos Robôs (BotBase):** Realizamos uma reestruturaçãono núcleo de automação. Todos os robôs (SIGEDE, SIATU, Urbano, etc.) agora obedecem a uma "Inteligência Central" (Classe Mãe), que gerencia tempos de espera e estratégias de clique e variáveis comuns à todos os bots. Isso capacita a aplicação a adequar-se mais facilmente (via linha de comando) à condições de conexão e pode reduzir erros intermitentes causados por lentidão na rede \- ou funcionar mais eficientemente em conexões melhores ou testes. O principal benefício é, no entanto, centralizar os ajustes de comportamentos comuns dos robôs (comportamentos específicos de cada bot continuam específicos).  
* **🐞 Diagnóstico Avançado (Debug Dinâmico):** Aprimoramento do sistema de registros (Logs). Agora é possível alterar o nível de detalhe do robô via configuração simples de inicialização, agilizando o diagnóstico de problemas em ambientes de produção.

## ---

**Changelog Técnico**

### **🔐 Segurança & Gerenciamento de Credenciais \[Novo\]**

Implementação do módulo **utils/credentials.py** para gestão segura do ciclo de vida de dados sensíveis.

* **CredentialManager (Static Class):** Atua como *Single Source of Truth* para credenciais, desacoplando a origem dos dados da interface de consumo.  
* **CredentialManager.session\_manager():** Implementação de um *Context Manager* (gerenciado de contexto via  ***with***). As credenciais são alocadas na memória estritamente durante a inicialização do **InterfaceApp**.  
* **Security Wipe (Limpeza de Memória):** Ao sair do contexto de inicialização, o sistema invoca **settings.limpar\_memoria\_credenciais()** e executa **clear(**) no dicionário injetado. Isso garante que não restem variáveis contendo senhas na memória Python durante o tempo de execução (*runtime*).  
* **Argumentos Ocultos (CLI):** Adição de suporte a argumentos de linha de comando suprimidos (--setSigedeCred, \--setSiatuCred) para injeção de credenciais em ambientes de desenvolvimento e automação, sem exposição no menu de ajuda público.

### **🤖 Arquitetura & BotCore (Refatoração)**

Centralização de lógica repetitiva na nova classe pai **app/core/base.py**, seguindo princípios SOLID/DRY.

* **Classe BotBase:** Implementada como superclasse para todos os módulos de automação (SigedeAuto, SiatuAuto, etc.).  
  * **Variáveis Comuns:** Centralização de self.timeout (com *fallback* automático para settings.py), self.driver e a instância persistente de **self.wait** (WebDriverWait), eliminando instanciações redundantes nos robôs filhos.  
  * **Método BotBase.\_click(...):** Migração da lógica híbrida de clique (Tentativa nativa \+ Fallback via JavaScript injection) para a classe base.  
  * **Método BotBase.\_interact(...):** Centralização da lógica de interação robusta com *fallback* de seletores. O método itera sobre estratégias (ID, XPath, CSS, etc.) sequencialmente até localizar o elemento ou esgotar as tentativas.  
  * **Método BotBase.\_esperar\_download\_concluir(...):** Lógica de monitoramento do sistema de arquivos (*File System Polling*) movida para a base, padronizando a verificação de integridade de downloads e a sanitização de nomes de arquivos em todos os sistemas.

### **🛠️ Logging, Debugging & Configuração**

Refatoração do sistema de logs para suportar níveis dinâmicos e novos argumentos de linha de comando no módulo settings.py.

* **Nível de Log Dinâmico:** O logger agora responde ao argumento \--**debug**. A lógica condicional manual foi removida em favor de **logger.setLevel(logging.DEBUG)**, permitindo o controle granular da verbosidade.  
* **Novos Argumentos CLI (Públicos):**  
  * \--**timeout (float)**: Define o tempo padrão de espera global (TIMEOUT\_ESPERA).  
  * **\--timeout-download (float):** Define o tempo limite para operações longas e downloads.  
  * **\--show-browser** ou **\--not-headless (**alias **\-sb, \-nhdls):** Força a exibição do navegador para debug visual durante a execução.  
* **Depuração/ Reprodutibilidade de Erros:** Depuração de dicionários e variáveis usadas na automação (camada de serviço) no [process.py](http://process.py) (do **executar()** de todos bots que se relacionam com plataformas governamentais).

### **🎨 Interface & UX**

Ajustes na InterfaceApp e no orquestrador main.py para suportar a nova arquitetura.

* **Auto-Preenchimento Seguro:** A InterfaceApp detecta e consome o dicionário de credenciais injetado pelo **CredentialManager**, preenchendo os campos visuais (**tk.Entry**) sem persistir os dados sensíveis na lógica interna da classe.  
* **Orquestração Híbrida (main.py):** Refinamento do fluxo de processamento para distinguir **Protocolos Reais** (que executam a etapa SIGEDE) de **Protocolos Virtuais** (Lotes de Índices Avulsos), ajustando dinamicamente a Barra de Progresso e a criação de pastas.  
* **Validação de Logs:** Ajuste na lógica de logs de injeção para evitar falsos positivos quando o dicionário de credenciais é inicializado vazio.

### **🔄 Resiliência**

* **Isolamento de Falhas no SISCTM (v. 1.49b):** Refatoração do método capturar\_areas. A extração de dados foi dividida em blocos independentes (try/except) para "IPTU CTM GEO" e "Lote CP". A falha na localização de uma camada não interrompe mais a captura da outra nem trava a automação.

### ---

**Próximos Passos (TO DO)**

* **\[Repositório\]** Limpeza do código da branch main (*merged* com o estado atual da branch de documentação) para adequar-se a filosofia clean code e migrar o conteúdo da pasta misc para guia Wiki ou pro drive de documentação.  
* **\[Documentação\]** Continuar documentando os pacotes que ainda não foram documentados.  
* **\[Segurança\]** Considerar implementar leitura de credenciais a partir de arquivos criptografados (.ini / .dat) utilizando criptografia simétrica, visando substituir a injeção via *plain text*.  
* **\[Configuração\]** Parametrizar as variáveis do decorador @retry (número de tentativas e delay) via settings.py.  
* **\[Logging\]** Implementar VisualFormatter para hierarquizar visualmente os logs de DEBUG com indentação, facilitando o rastreio de fluxos aninhados e leitura.

