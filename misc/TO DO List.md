* **[URGENTE / PRIORITÁRIO]** **ADD TRIAGEM POR ÍNDICES CADASTRIAS:** Tem que fazer... É Isso...

* Padronizar os argumentos da classe de interface (app/pipeline/interface/base.py) para dar conta de todas as classes de serviço (em app/pipeline/sistemas.py)

* Retirar as implementações repetitivas do método _click() em todos os bot-cores (todos os módulos em app/core/) e levar essa implementação para a classe base ou para um método utilitário - para diminuir repetição de código e adequar melhor ao SOLID.

* Persistência dos Logs de triagem: Após gerar todo o log e salvar A ÚLTIMA TRIAGEM na raíz do projeto/executável copiar o arquivo de log PRA DENTRO DA PASTA DE RESULTADOS - para que os logs não se percam na próxima triagem e tudo relativo à quela triagem fique num lugar só.

* **[FEITO - AutoTRI 1.3]** SISCTM (checagem de pop-up): Garantir que, se a checagem de popup estiver true na triagem do primeiro protocolo, ela auto-desliga nas próximas triagens.
        Isso elimina a perda de eficiência de 3 segundos caso o pop-up já tenha sido retirado na triagem anterior.
        (Protocolos são geralmente triados em séries numa única execução do AutoTri).

* No status de triagem falar em qual X/N protocolo está e em qual fase. ex: Triando Protocolo 6/9 - SISCTM
* Usar 'separador' (var da main) para separar seções visualmente no Log ( algo tipo -------- <protocolo> - Fase: SISCTM  ------) ou coisa parecida
