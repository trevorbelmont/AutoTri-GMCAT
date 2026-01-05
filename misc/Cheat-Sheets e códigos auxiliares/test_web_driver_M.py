import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

def testar_inicializacao():
    print("--- 🛠️ Iniciando teste funcional do WebDriver... ---")
    
    # 1. Configurações de estabilidade para WSL (Linux)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    
    # Você pode querer rodar em modo headless para testes mais rápidos no WSL:
    # options.add_argument("--headless=new") 

    driver = None
    
    try:
        # 2. Configura o Service usando o WebDriver-Manager
        # Esta linha baixa o driver correto e retorna seu caminho.
        print("1. Tentando localizar e configurar o ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        # 3. Inicializa o WebDriver com as opções e o service
        print("2. Inicializando o navegador Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # 4. Teste de navegação (Hello World)
        print("3. Navegando para https://www.google.com...")
        driver.get("https://www.google.com")
        
        # Aguarda brevemente para ter certeza que a página carregou
        time.sleep(3) 
        
        # 5. Verifica o resultado
        if "Google" in driver.title:
            print(f"\n✅ SUCESSO! WebDriver-Manager e Chrome (v{driver.capabilities.get('browserVersion')}) estão funcionando!")
        else:
            print(f"\n⚠️ SUCESSO PARCIAL! Navegador abriu, mas não conseguiu acessar o Google. Título: {driver.title}")

    except WebDriverException as e:
        print(f"\n❌ FALHA CRÍTICA do WebDriver. Verifique a instalação do seu navegador Chromium (apt install).")
        print(f"Detalhes do Erro: {e}")

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

    finally:
        # 6. Encerra o driver e o navegador
        if driver:
            print("4. Encerrando driver...")
            driver.quit()
        print("--- 🏁 Teste concluído. ---")


if __name__ == "__main__":
    testar_inicializacao()