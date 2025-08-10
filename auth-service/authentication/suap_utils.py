import requests

def suap_login(username, password):
    """Tenta autenticar no SUAP e retorna o token de acesso."""
    url_token = "https://suap.ifsuldeminas.edu.br/api/token/pair"
    payload = {"username": username, "password": password}
    try:
        response = requests.post(url_token, json=payload, timeout=5) # Adiciona timeout
        if response.status_code == 200:
            return response.json().get("access")
    except requests.exceptions.RequestException as e:
        print(f"[ERRO DE CONEXÃO SUAP]: {e}")
    return None

def get_user_info(token):
    """Busca os dados do usuário no SUAP usando o token de acesso."""
    url_info = "https://suap.ifsuldeminas.edu.br/api/v2/minhas-informacoes/meus-dados/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url_info, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO DE CONEXÃO SUAP]: {e}")
    return None