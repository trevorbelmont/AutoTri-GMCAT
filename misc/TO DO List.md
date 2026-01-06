* Padronizar os argumentos da classe de interface (app/pipeline/interface/base.py) para dar conta de todas as classes de serviço (em app/pipeline/sistemas.py)

* Retirar as implementações repetitivas do método _click() em todos os bot-cores (todos os módulos em app/core/) e levar essa implementação para a classe base ou para um método utilitário - para diminuir repetição de código e adequar melhor ao SOLID.

* SISCTM (checagem de pop-up): Garantir que, se a checagem de popup estiver true na triagem do primeiro protocolo, ela auto-desliga nas próximas triagens.
         Isso elimina a perda de eficiência de 3 segundos caso o pop-up já tenha sido retirado na triagem anterior.
         (Protocolos são geralmente triados em séries numa única execução do AutoTri).