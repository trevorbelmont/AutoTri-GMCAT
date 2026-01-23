# **AutoTri \- Versão 1.49b \[Stable\]**

## **🛡️ Solidez, Arquitetura e Logs**

Maior estabilidade do ciclo de vida da aplicação, isolamento de sessões e ferramentas de diagnóstico avançado no log.

* **Rotação de Logs por Execução (Session Reset):** Implementação da função reset\_log\_file() no módulo logger.py. O manipulador de arquivo (FileHandler) é agora fechado e recriado a cada clique no botão "Iniciar", garantindo que o arquivo de log contenha apenas os dados da triagem atual, prevenindo o acúmulo de logs de sessões anteriores (persistência fantasma).  
* **Persistência Automática:** O log da execução é copiado automaticamente para a pasta de Resultados do protocolo ao final do processo, garantindo rastreabilidade.  
* **Refatoração GUI (OOP) \[v1.3\]:** O módulo de interface (gui/interface.py) foi reescrito. Substituição da função monolítica pela classe InterfaceApp, encapsulando estado e métodos. Uso do padrão *Adapter* para manter compatibilidade com o orquestrador main.py.  
* **Performance de Logs \[v1.3\]:** Implementação de QueueHandler e queue.Queue para passar logs do *backend* para a interface via memória, eliminando travamentos visuais (*flickering*).

## **🤖 Resiliência e BotCore (SISCTM & Geral)**

Aprimoramentos críticos na robustez dos robôs, com foco na continuidade da automação mesmo diante de falhas parciais nos sistemas governamentais.

* **Isolamento de Falhas no SISCTM:** Refatoração do método capturar\_areas. A extração de dados foi dividida em blocos independentes (try/except) para "IPTU CTM GEO" e "Lote CP". A falha na localização de uma camada não interrompe mais a captura da outra nem trava a automação.  
* **Interação Robusta (\_interact):** Criação de método universal de interação com lógica de *fallback* em múltiplas estratégias de seletores (XPath, CSS, ID) para elementos instáveis. Dentro de uma mesma estratégia pode haver fallbacks em segunda camada para lidar com a interação.  
* **Tratamento de Pop-ups (Fail Fast):** Implementação de verificação rápida (timeout reduzido) para fechamento automático do pop-up "Notas de Versão" no SISCTM.  
* **Correção Google Maps \[v1.3\]:** Atualização dos seletores dinâmicos do campo de busca para suportar mudanças no DOM do Google Maps.

## **🖥️ Interface (GUI) e Experiência do Usuário (UX)**

Melhorias na entrada de dados e flexibilidade de execução.

* **Sanitização e Mascaramento de Entrada:** Criação do módulo utils/formatters.py e função format\_by\_pattern.  
  * **Correção Crítica:** Índices Cadastrais inseridos sem formatação (ex: 3120160070011) são automaticamente detectados e formatados para o padrão PBH (312016 007 0011) antes do processamento. Isso resolve falhas de busca no SISCTM e Urbano que dependem de espaços exatos na formatação de cada Índice Cadastral.  
* **Normalização de Listas:** O campo de entrada de protocolos agora aceita separadores variados (quebras de linha, espaços, vírgulas) e realiza a limpeza automática (strip) para evitar erros de leitura.  
* **Granularidade da Progress Bar:** A Barra de Progresso agora reage à progressos tanto na triagem de índices cadastrais dentro de um mesmo protocolo e nas etapas de triagem de cada índice cadastral (não só reflete o avanço de quantos protocolos foram triados.  
* **Estimativa Simples de Tempo:** Um campo de estimativa de tempo e tempo utilizado foi criado para refletir uma estimativa simples de tempo de processamento baseado nas médias de tempos de  triagens observadas.  
* **Responsividade \[v1.3\]:** Ajuste nas configurações de grid do TKinter para redimensionamento fluido da janela e da área de logs.

## **📚 Documentação Técnica**

Atualizações na base de conhecimento para desenvolvedores.

* **Estrutura de Utilitários:** Centralização de funções auxiliares em app/utils/formatters.py (formatação) e app/utils/logger.py (logging avançado).  
* **Cheat-Sheets \[v1.3\]:** Adição de guias rápidos na pasta misc/ cobrindo tecnologias utilizadas (TKinter, Selenium, PyInstaller, Venv).  
* **Docstrings:** Atualização da documentação interna dos métodos \_interact, capturar\_areas e reset\_log\_file detalhando comportamentos de borda e tratamento de exceções.  
* 

