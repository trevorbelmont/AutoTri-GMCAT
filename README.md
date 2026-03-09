# Links Úteis

## Executável de Distribuição
### [Pasta de Distribuição](https://drive.google.com/drive/folders/1vXxPCR9K_Ow2ADIvdMVsAwrsgmXjRu5z?usp=sharing)

## Documentação
### [Link Documentação](https://drive.google.com/drive/folders/1eS0YmXbdpFn6Romy1wwn3tWkGPOoeIZu?usp=sharing)

## Link deste Repositório
### [Link Repo GitHub - main branch](https://github.com/trevorbelmont/AutoTri-GMCAT)

# **AutoTri \- Introdução**

[**Link do Repositório**](https://github.com/trevorbelmont/AutoTri-GMCAT/tree/cleaning?tab=readme-ov-file)

O **AutoTri** é uma plataforma de automação robótica de processos (RPA) desenvolvida para otimizar a triagem técnica de processos administrativos e imobiliários. O software atua como um orquestrador central que integra diversos bots que acessam múltiplos sistemas governamentais e ferramentas de geoprocessamento em um pipeline único e automatizado.

O programa foi programado com interface gráfica para inserção de credenciais, protocolos e índices cadastrais, facilitando o seu uso. No entanto, desde a versão 1.52a, o software é capaz de receber argumentos via linha de comando que podem ser usados para depuração de bugs ou automação do próprio sistema.

## **1\. Funcionamento do Software**

O AutoTri opera através de um fluxo de trabalho linear e modular, projetado para transformar dados brutos de entrada (Protocolos SIGEDE ou Índices Cadastrais avulsos) em um dossiê técnico completo.

### **Como ele funciona:**

1. **Entrada de Dados:** O usuário insere as credenciais e os identificadores (protocolos ou ICs) via interface gráfica (GUI).  
2. **Orquestração de Pipeline:** O sistema inicia uma thread de processamento que percorre sequencialmente os adaptadores de automação que simulam a interação do usuário com um navegador (navegando, preenchendo campos textuais, fazendo downloads e tirando prints da tela):  
   * **SIGEDE:** Identifica os índices cadastrais vinculados a um protocolo.  
   * **SIATU:** Extrai dados da Planta Básica e realiza o download de anexos documentais.  
   * **URBANO:** Captura dados de licenciamento, alvarás e projetos de edificação.  
   * **SISCTM:** Coleta evidências visuais (prints) e dados de geoprocessamento da malha cadastral.  
   * **EARTH:** Realiza o download direto de arquivos KML para visualização em 3D.  
   * **GOOGLE MAPS:** Captura imagens de satélite e fachada para conferência visual.  
3. **Consolidação:** Após a execução, o software organiza todos os arquivos baixados em pastas estruturadas por protocolo e índice.

### **O que ele devolve:**

* **Relatório de Triagem (PDF):** Um documento consolidado com tabelas de dados comparativos, links para anexos e notas técnicas.  
* **Dossiê Digital:** Uma estrutura de pastas contendo todos os arquivos originais (PDFs, imagens, KMLs) capturados durante o processo.

## 

## **2\. Tecnologias Utilizadas**

A arquitetura do AutoTri baseia-se em tecnologias de ponta para automação web e processamento de dados:

* **Linguagem:** Python 3.x (Núcleo do sistema e orquestração).  
* **Automação Web:** Selenium WebDriver (Interação com interfaces complexas).  
* **Requisições de Rede:** `curl_cffi` (Utilizado para bypass de firewall e captura rápida de polígonos).  
* **Interface Gráfica:** Tkinter (GUI para interação com o usuário).  
* **Geração de Documentos:** ReportLab (Criação de PDFs dinâmicos).  
* **Segurança de Credenciais:** `CredentialManager` (Gerenciamento de sessões e memória segura).

## **3\. Segurança e Proteção de Dados**

A segurança foi implementada como um pilar central da aplicação para proteger informações sensíveis:

* **Sessões Voláteis:** O software utiliza o `CredentialManager` para garantir que as credenciais inseridas existam apenas durante a execução da thread de processamento.  
* **Limpeza de Memória:** Ao final de cada execução ou em caso de encerramento prematuro, o método `limpar_memoria_credenciais()` é invocado para esvaziar os dicionários de memória global do módulo `settings`.  
* **Bypass de Logs:** Senhas e chaves sensíveis são suprimidas dos arquivos de log e do sistema de ajuda da CLI (`argparse.SUPPRESS`).

## **4\. Robustez e Resiliência**

Para enfrentar instabilidades inerentes aos sistemas web governamentais, o AutoTri emprega estratégias de robustez:

* **Lógica de Retry:** O decorador `@retry` permite que falhas momentâneas de carregamento ou rede sejam superadas automaticamente através de novas tentativas configuráveis.  
* **Isolamento de Erros:** O pipeline é projetado para que a falha em um sistema secundário (como a captura do polígono KML) não interrompa a triagem principal ou a geração do relatório.

## **5\. Robôs de Automação (bot-core)**

Esta seção detalha o funcionamento dos motores de automação (os "bots") que compõem o núcleo do **AutoTri**. Todos os robôs foram construídos sobre uma fundação comum chamada **BotBase**, que garante que eles compartilhem a mesma inteligência para clicar em botões, esperar o carregamento de páginas e nomear arquivos de forma segura.

Podemos dividir os 7 bots em três grupos principais, de acordo com a forma como interagem com a tecnologia:

### **5.1. Exploradores de Sistemas (SIGEDE, SIATU e URBANO)**

Estes robôs são os responsáveis por navegar nos sistemas governamentais. Eles funcionam através de uma simulação de comportamento humano via navegador (*WebDriver*).

* **Lógica de Trabalho:** Eles realizam o login, percorrem menus complexos e localizam processos ou índices específicos.  
* **Extração Documental:** São programados para identificar links de download e aguardar a conclusão de cada arquivo de forma paciente, garantindo que nenhum documento (como o Inteiro Teor ou a Planta Básica) seja perdido por lentidão dos servidores externos.  
* **Persistência:** Em caso de erros de carregamento, eles utilizam uma lógica de "tentativa e erro" (fallback) para tentar localizar o elemento desejado por diferentes caminhos antes de desistir.

### **5.2. Capturadores Visuais (SISCTM e Google Maps)**

Este grupo foca na geração de evidências visuais e dados geográficos. Eles também utilizam o navegador para "enxergar" o que um analista veria na tela.

* **Mapeamento e Prints:** O robô do **SISCTM** navega por mapas digitais, ativa camadas de informação (como lotes ativos e tributação) e captura "fotos" aéreas e ortofotos.  
* **Contexto Urbano:** O bot do **Google Maps** utiliza os endereços encontrados para capturar imagens de satélite e a fachada dos imóveis (Street View), enriquecendo a triagem com o contexto real do terreno.

### **5.3. Especialistas em Dados e Documentos (Polígono KML e Relatórios)**

Estes dois componentes operam de forma distinta dos anteriores, pois não dependem de navegação visual ou cliques em sites.

* **Robô de Polígono (WFS):** Diferente dos demais, este bot não abre um navegador. Ele se comunica diretamente com os servidores de dados geográficos da prefeitura por meio de requisições de rede invisíveis, o que o torna extremamente rápido e imune a mudanças visuais em sites. Ele entrega o arquivo `.kml` pronto para ser aberto no Google Earth. Este robô foi desenvolvido baseado no código pega\_poligono.py, escrito pelo servidor Daniel Viana.  
* **Robô de Consolidação (Relatórios):** Este é o motor final que não interage com a internet. Sua função é ler todos os dados e imagens coletados pelos outros 6 robôs e "escrever" o relatório PDF final, organizando as informações de forma clara e profissional para o analista.

