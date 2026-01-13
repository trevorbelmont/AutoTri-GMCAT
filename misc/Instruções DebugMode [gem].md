Com base na sua solicitação, a melhor arquitetura para resolver isso **sem alterar as assinaturas das funções existentes** e sem criar importações circulares complexas é utilizar o padrão de projeto **Decorator** aliado a uma variável de configuração global no módulo de utilitários (`logger.py` ou um novo `config.py`).

Isso permite que você "embrulhe" os métodos `executar()` das classes de serviço. O decorator verifica a variável global: se for `True`, ele intercepta os dados, formata como código Python válido (usando `repr()`) e imprime no log antes e depois da execução real.

Aqui está o plano de implementação passo a passo:

### Passo 1: Preparar o `app/utils/logger.py`

Vamos adicionar a flag global e o **Decorator de Inspeção** aqui. Este é o local ideal pois já é importado por todos os sistemas e evita dependências circulares.

**Adicione este código ao final de `app/utils/logger.py`:**

```python
import functools
import pprint

# --- CONFIGURAÇÃO GLOBAL DE DEBUG ---
# Esta variável controla se o modo detalhado está ativo ou não.
# Pode ser alterada pela main.py ou interface.py em tempo de execução.
GLOBAL_DEBUG_MODE = False 

def set_debug_mode(ativar: bool):
    """Setter global para ativar o modo de depuração."""
    global GLOBAL_DEBUG_MODE
    GLOBAL_DEBUG_MODE = ativar
    if ativar:
        logger.setLevel(logging.DEBUG)
        logger.info(">>> MODO DEBUG ATIVADO: Logs detalhados de I/O habilitados. <<<")

def debug_inspector(func):
    """
    Decorator para inspecionar Entradas e Saídas de funções.
    Gera logs formatados prontos para 'Copiar e Colar' (Sequestro de Fluxo).
    Só executa se GLOBAL_DEBUG_MODE for True.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not GLOBAL_DEBUG_MODE:
            return func(*args, **kwargs)

        nome_func = func.__qualname__ # Ex: Siatu.executar
        
        # --- LOG DE ENTRADA (INPUTS) ---
        logger.info(f"\n{'#'*20} DEBUG INPUT: {nome_func} {'#'*20}")
        logger.info(f"# Para reproduzir, instancie a classe e chame {func.__name__} com:")
        
        # Loga argumentos posicionais (ignorando 'self' se for método)
        args_limpos = args[1:] if args and hasattr(args[0], '__class__') else args
        if args_limpos:
            logger.info(f"# ARGUMENTOS POSICIONAIS ({len(args_limpos)}):")
            for i, arg in enumerate(args_limpos):
                # repr(arg) garante que strings tenham aspas, dicts sejam formatados, etc.
                logger.info(f"arg_{i} = {repr(arg)}")
        
        # Loga argumentos nomeados (kwargs)
        if kwargs:
            logger.info(f"# ARGUMENTOS NOMEADOS:")
            for k, v in kwargs.items():
                logger.info(f"{k} = {repr(v)}")
        logger.info(f"{'#'*60}\n")

        # --- EXECUÇÃO REAL ---
        try:
            resultado = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"!!! EXCEÇÃO EM {nome_func}: {e}")
            raise e

        # --- LOG DE SAÍDA (OUTPUTS) ---
        logger.info(f"\n{'='*20} DEBUG OUTPUT: {nome_func} {'='*20}")
        logger.info(f"# Retorno da função (pronto para mock):")
        # pprint deixa dicionários grandes legíveis e copiáveis
        formatted_output = pprint.pformat(resultado, indent=4, width=120)
        logger.info(f"resultado = {formatted_output}")
        logger.info(f"{'='*60}\n")

        return resultado

    return wrapper

```

### Passo 2: Aplicar o Decorator em `app/pipeline/sistemas.py`

Agora, basta colocar o `@debug_inspector` em cima dos métodos `executar` que você quer monitorar. Não precisa mudar nenhuma lógica interna.

**Edite `app/pipeline/sistemas.py`:**

1. Adicione o import no topo:
```python
from utils.logger import debug_inspector # <--- Importe o decorator

```


2. Decore os métodos `executar` das classes (Sigede, Siatu, Urbano, Sisctm, GoogleMaps). Exemplo com o `Sisctm`:

```python
class Sisctm(SistemaAutomacao):
    """Adapter para o sistema de Mapa (SISCTM)."""

    # ADICIONE O DECORATOR AQUI
    @debug_inspector 
    def executar(self, indice: str, credenciais: Dict[str, str], pasta_indice: str) -> Dict[str, Any]:
        """Executa a automação do mapa SISCTM..."""
        # ... (O resto do código permanece IDÊNTICO) ...

```

*Repita isso para `Sigede.executar`, `Siatu.executar`, `Urbano.executar` e `GoogleMaps.executar`.*

### Passo 3: Ativar na Interface (`app/gui/interface.py`)

Você queria uma forma de ativar isso. Uma solução elegante "escondida" (sem poluir a UI principal) ou via argumento é simples.

Como você ainda não tem CLI arguments implementados na `main.py`, vamos adicionar um **Checkbox de Debug** na interface, mas para não poluir, podemos colocá-lo pequeno ou ativá-lo via código temporariamente.

**Sugestão de implementação rápida na `interface.py`:**

No método `_configurar_widgets`, adicione um checkbox "Modo Debug" (pode ser na linha do botão Iniciar):

```python
# Em interface.py, dentro de __init__:
self.var_debug = tk.BooleanVar(value=False) # Começa desligado

# Em interface.py, dentro de _configurar_widgets (perto dos botões):
chk_debug = tk.Checkbutton(self.root, text="Modo Debug (Logs I/O)", variable=self.var_debug)
chk_debug.grid(row=7, column=1, sticky="w", padx=5) # Ajuste o grid conforme seu layout atual

```

**E no método `_acao_confirmar` (antes de iniciar a thread):**

```python
# Em interface.py, dentro de _acao_confirmar:
from utils.logger import set_debug_mode

# ... validações ...

# Define o modo global baseado no checkbox
set_debug_mode(self.var_debug.get())

# ... inicia thread ...

```

### O Resultado Prático

Quando você rodar a automação com o checkbox marcado, o seu log (`Detalhes da Última Triagem.txt`) vai conter blocos assim:

```text
#################### DEBUG INPUT: Sisctm.executar ####################
# Para reproduzir, instancie a classe e chame executar com:
# ARGUMENTOS POSICIONAIS (3):
arg_0 = '9471400120011'
arg_1 = {'usuario': 'teste', 'senha': '123'}
arg_2 = 'C:\\Resultados\\Triagem por ICs\\9471400120011'
############################################################

... logs normais da automação ...

==================== DEBUG OUTPUT: Sisctm.executar ====================
# Retorno da função (pronto para mock):
resultado = {   'endereco_ctmgeo': 'Rua Exemplo, 123 - BH',
    'iptu_ctm_geo_area': '360,00',
    'iptu_ctm_geo_area_terreno': '360,00',
    'lote_cp_ativo_area_informada': '360,00'}
============================================================

```

### Como usar isso para "Sequestro de Fluxo" (Mocking)

Agora, se der erro no `GoogleMaps`, você vai no log, copia a saída do `SISCTM` e do `SIATU` (que são inputs do GoogleMaps) e cria um script `teste_google.py`:

```python
from app.core.google import GoogleMapsAuto
from app.utils import driver_context

# DADOS COPIADOS DO LOG DE DEBUG
indice = '9471400120011'
pasta = 'C:\\Resultados\\...'
dados_sisctm = {   
    'endereco_ctmgeo': 'Rua Exemplo, 123 - BH',
    'iptu_ctm_geo_area': '360,00',
    # ... resto copiado ...
}
dados_pb = {} # Copiado do log do Siatu

# Execução direta (Sequestro de fluxo)
print("Rodando apenas Google Maps com dados mockados...")
with driver_context(pasta) as driver:
    bot = GoogleMapsAuto(driver, "url...", endereco=dados_sisctm['endereco_ctmgeo'], pasta_download=pasta)
    bot.acessar_google_maps()
    bot.navegar()

```

Isso atende 100% à sua necessidade de reprodução rápida sem alterar a estrutura do código principal.