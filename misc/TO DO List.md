# TO DO List

* **[URGENTE / PRIORITÁRIO]** **ADD TRIAGEM POR ÍNDICES CADASTRIAS:** Tem que fazer... É Isso...
        **>> FUNDAMENTAL >> :** Índices cadastrais SEMPRE tem formatação padrão? [padrão 123456 123 1234 (Regional, Quadra, Lote).]???
        **>> UX, UI, ROBUSTEZ >>:** Saber se existe realmente um padrão sempre fixo, determina a robustez (e risco da implementação) e a interção dos usuários com o campo de Triagem via Cadastrias

* **[PRIORITÁRIO]** **Checar frequência do status (print) "SEM PROJETO" do URBANO** O print vindo do Urbano tá mostrando sem projeto com frequência - é normal

* **[PRIORITÁRIO]** **SISTEMA DE UPDATE**: Implementar no próprio AutoTRI um meio de comunicação de novas atualizações de updates (notas de versão)
        * **Como isso se dá?** AutoUpdate (com download e substituição automáticos)? Direciona pro site? Atualização lateral (baixa a nova versão e substitui - mas move  mantém a(s) antiga(s) no computador do usuário - para casos de erros de código ou atualizações inconsistentes?)
        * **Comunicação:** Luzes (estilo semáforo), balões de mensagem, Message Box (como já tem), Janela secundária.
        * **Comunicação de Duas Vias?** Indicar (na interface) mandar e-mail pro 4B para notificar problemas/sugestões? Ter um campo de enviar e-mails (padronizados) no próprio AutoTri???

* **[???]** **'SEM PROJETOS' frequente/sempre no Urbano???** Isso é normal

* **[IMPORTANTE]** Entrada de Argumentos na main: Implementar a entrada de argumentos quando roda no terminal para fazer a depuração mais viável e prática (exemplo: rodar headless ou não).
        * Checar se os argumentos da main fiam acessíveis e funcionais no modo --one-file (via painel de propreidades do arquivo)

*  **[IMPORTANTE]** MODO DEBUG:   Em especial para o módulo sistemas.py que orquestra a automação, criar uma entrada de argumentos e/ou checkbox (escondida?) na interface que detalhe o log para depuração. Em sistemas.py uma alteração importante seria: **printar num log separado, logger.DEBUG, por exemplo, o conteúdo de cada dicionário nas saídas (e entrada) das camadas de serviço da automação. Isso possibilita entender exatamente o que cada etapa tá recebendo e retornando e reproduzir falhas mais rapidamente - sem ter que rodar a automação toda.

* **SUMÁRIO DE ERROS MAIS DETALHADO:** Nos logs, ao fim da triagem, além da contagem de protocolos e ICs totais (via triagem de Protocolo + via triagem de ICs), adicionar também um sumário dos erros que aconteceram em cada protocolo/cadastral, para rápida identificação de erros de processamento. **Sumário não verboso, mas informativo.** 

* **[INTERFACE]** **Barra de Progresso:** 
  * Melhorar a granularidade do avanço da barra de progresso - implmentar cálculo inteligente auto ajustável (para cobrir não só avanço de protocolo, mas tb **progresso na traigem dos ICs no protocolo e fase da triagem do IC**)
  * Aplica padrão formatter_by_pattern2(...) nos ICs da Status Message
  * organizar a contagem do "[IC 6/9]" pra refletir os ICs sendo triados na etap no '9' ao invés da contagem total de ICs triados em todas etapas

* Padronizar os argumentos da classe de interface (app/pipeline/interface/base.py) para dar conta de todas as classes de serviço (em app/pipeline/sistemas.py)

* **[DRY - _click(...) bot-core]**Retirar as implementações repetitivas do método _click() em todos os bot-cores (todos os módulos em app/core/) e levar essa implementação para uma única definição porém na classe base ou para um método utilitário - para diminuir repetição de código e adequar melhor ao SOLID.

* **[DRY - _interact(...) bot-core]** Subir a definição dos métodos _interact(...), o _click(...) mais resiliente, definidos duas vezes (em sisctm.py e google.py) para a classe base - pois este é um método universal e agnóstico quanto ao site ou plataformas que estamos (e pode ser usado até em outras aplicações de autmação de navegação)

## Implementados

* **[Feito - AutoTRI 1.3]** APersistência dos Logs de triagem: Após gerar todo o log e salvar A ÚLTIMA TRIAGEM na raíz do projeto/executável copiar o arquivo de log PRA DENTRO DA PASTA DE RESULTADOS - para que os logs não se percam na próxima triagem e tudo relativo à quela triagem fique num lugar só.

* **[FEITO - AutoTRI 1.3]** SISCTM (checagem de pop-up): Garantir que, se a checagem de popup estiver true na triagem do primeiro protocolo, ela auto-desliga nas próximas triagens.
        Isso elimina a perda de eficiência de 3 segundos caso o pop-up já tenha sido retirado na triagem anterior.
        (Protocolos são geralmente triados em séries numa única execução do AutoTri).

* **[FEITO - AutoTRI 1.48]** No status de triagem falar em qual X/N protocolo está e em qual fase. ex: Triando Protocolo 6/9 - SISCTM
* Usar 'separador' (var da main) para separar seções visualmente no Log ( algo tipo -------- <protocolo> - Fase: SISCTM  ------) ou coisa parecida


