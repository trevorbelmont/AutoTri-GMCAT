* **[URGENTE / PRIORITÁRIO]** **ADD TRIAGEM POR ÍNDICES CADASTRIAS:** Tem que fazer... É Isso...

* **[PRIORITÁRIO]** **Checar frequência do status (print) "SEM PROJETO" do URBANO** O print vindo do Urbano tá mostrando sem projeto com frequência - é normal

* **[PRIORITÁRIO]** **SISTEMA DE UPDATE**: Implementar no próprio AutoTRI um meio de comunicação de novas atualizações de updates (notas de versão)
        * **Como isso se dá?** AutoUpdate (com download e substituição automáticos)? Direciona pro site? Atualização lateral (baixa a nova versão e substitui - mas move  mantém a(s) antiga(s) no computador do usuário - para casos de erros de código ou atualizações inconsistentes?)
        * **Comunicação:** Luzes (estilo semáforo), balões de mensagem, Message Box (como já tem), Janela secundária.
        * **Comunicação de Duas Vias?** Indicar (na interface) mandar e-mail pro 4B para notificar problemas/sugestões? Ter um campo de enviar e-mails (padronizados) no próprio AutoTri???

* Padronizar os argumentos da classe de interface (app/pipeline/interface/base.py) para dar conta de todas as classes de serviço (em app/pipeline/sistemas.py)

* Retirar as implementações repetitivas do método _click() em todos os bot-cores (todos os módulos em app/core/) e levar essa implementação para a classe base ou para um método utilitário - para diminuir repetição de código e adequar melhor ao SOLID.

* **[Feito - AutoTRI 1.3]** APersistência dos Logs de triagem: Após gerar todo o log e salvar A ÚLTIMA TRIAGEM na raíz do projeto/executável copiar o arquivo de log PRA DENTRO DA PASTA DE RESULTADOS - para que os logs não se percam na próxima triagem e tudo relativo à quela triagem fique num lugar só.

* **[FEITO - AutoTRI 1.3]** SISCTM (checagem de pop-up): Garantir que, se a checagem de popup estiver true na triagem do primeiro protocolo, ela auto-desliga nas próximas triagens.
        Isso elimina a perda de eficiência de 3 segundos caso o pop-up já tenha sido retirado na triagem anterior.
        (Protocolos são geralmente triados em séries numa única execução do AutoTri).

* **[FEITO - AutoTRI 1.48]** No status de triagem falar em qual X/N protocolo está e em qual fase. ex: Triando Protocolo 6/9 - SISCTM
* Usar 'separador' (var da main) para separar seções visualmente no Log ( algo tipo -------- <protocolo> - Fase: SISCTM  ------) ou coisa parecida


