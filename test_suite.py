import requests
import time
import jwt

# URL base do nosso sistema, apontando para o API Gateway
BASE_URL = "http://localhost:8000"
# URL direta para o persistence-service para a limpeza (mais simples para o teste)
PERSISTENCE_URL = "http://localhost:8002"

# Chave secreta para depuração do token (deve ser a mesma do kong.yml e settings.py)
SECRET_KEY = 'my-super-secret-key-that-must-match'

# Usaremos uma sessão para que os cookies de login sejam mantidos
session = requests.Session()

def print_status(message, success):
    """Função auxiliar para imprimir os resultados do teste."""
    status = "✅ SUCESSO" if success else "❌ FALHA"
    print(f"{status}: {message}")

def debug_token(response):
    """
    Função para extrair, decodificar e imprimir o conteúdo do token JWT.
    """
    print("\n--- 🔍 INSPECIONANDO TOKEN JWT 🔍 ---")
    access_token = response.cookies.get('access_token')
    if not access_token:
        print("Token 'access_token' não encontrado nos cookies da resposta.")
        return

    print(f"Token (encurtado): {access_token[:30]}...")
    try:
        decoded_payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        print("Token decodificado com SUCESSO!")
        print("Conteúdo (Payload):")
        for key, value in decoded_payload.items():
            print(f"  - {key}: {value}")
    except jwt.InvalidSignatureError:
        print("ERRO CRÍTICO: A assinatura do token é INVÁLIDA.")
    except Exception as e:
        print(f"ERRO ao decodificar o token: {e}")
    print("-------------------------------------\n")

def cleanup_before_test():
    """
    Limpa os dados de testes anteriores para garantir um ambiente limpo.
    """
    print("\n--- 🧹 FASE DE LIMPEZA 🧹 ---")
    
    # Em um ambiente de produção, este endpoint não existiria ou seria protegido.
    users_to_clean = ["_test_admin_", "_test_aluno_"]
    for user in users_to_clean:
        # Acessamos o endpoint de limpeza diretamente no persistence-service
        url = f"{PERSISTENCE_URL}/internal/cleanup/user/{user}/"
        try:
            response = requests.delete(url, timeout=5)
            # 204 (No Content) ou 404 (Not Found) são considerados sucesso na limpeza
            if response.status_code in [204, 404]:
                print_status(f"Limpeza do usuário '{user}'", True)
            else:
                print_status(f"Limpeza do usuário '{user}'", False)
                print(f"  -> Resposta do servidor de limpeza: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_status(f"Falha ao conectar ao serviço de persistência para limpeza do usuário '{user}'", False)


def run_test_suite():
    """Executa a suíte de testes completa."""
    # 1. Limpa o ambiente antes de começar
    cleanup_before_test()
    
    print("\n🚀 INICIANDO SUÍTE DE TESTES AUTOMATIZADOS 🚀")
    print("-" * 50)

    # --- Cenário 1: Administrador cria os recursos ---
    print("\n--- CENÁRIO 1: SETUP COMO ADMINISTRADOR ---")
    
    # 1.1 Login como Administrador
    payload = {"username": "_test_admin_", "role": "administrador"}
    response = session.post(f"{BASE_URL}/api/auth/mock-login/", json=payload)
    is_success = response.status_code == 200
    print_status("Login como Administrador", is_success)
    debug_token(response)
    if not is_success:
        print(f"Erro no login: {response.status_code} - {response.text}")
        return
    
    # Espera 2 segundos para o evento ser consumido pelo persistence-service
    time.sleep(2)

    # 1.2 Criar um Departamento
    payload = {"name": "Teste de Automação", "code": "TESTE"}
    response = session.post(f"{BASE_URL}/api/resources/departments/", json=payload)
    is_success = response.status_code == 201
    print_status("Criar Departamento", is_success)
    if not is_success:
        print(f"Resposta do servidor: {response.status_code} - {response.text}")
        return
    department_id = response.json().get('id')

    # 1.3 Criar uma Sala
    payload = {"code": "AUTOTEST01", "name": "Sala de Teste", "department": department_id}
    response = session.post(f"{BASE_URL}/api/resources/rooms/", json=payload)
    is_success = response.status_code == 201
    print_status("Criar Sala", is_success)
    if not is_success:
        print(f"Resposta do servidor: {response.status_code} - {response.text}")
        return
    
    print("-" * 50)

    # --- Cenário 2: Aluno tenta acessar recursos ---
    print("\n--- CENÁRIO 2: TESTES COMO ALUNO ---")

    # 2.1 Login como Aluno
    payload = {"username": "_test_aluno_", "role": "padrao"}
    response = session.post(f"{BASE_URL}/api/auth/mock-login/", json=payload)
    is_success = response.status_code == 200
    print_status("Login como Aluno", is_success)
    if not is_success: return
    
    time.sleep(2)

    # 2.2 Tentar criar uma sala (deve falhar)
    payload = {"code": "FAIL01", "name": "Sala de Falha", "department": department_id}
    response = session.post(f"{BASE_URL}/api/resources/rooms/", json=payload)
    is_success = response.status_code == 403 # 403 Forbidden é o sucesso aqui
    print_status("Aluno tentar criar sala (esperado falhar com 403)", is_success)
    if not is_success:
        print(f"Resposta do servidor: {response.status_code} - {response.text}")
        return

    # ... Adicionar mais testes aqui ...

    print("-" * 50)
    print("🎉 SUÍTE DE TESTES CONCLUÍDA COM SUCESSO! 🎉")

if __name__ == "__main__":
    run_test_suite()
