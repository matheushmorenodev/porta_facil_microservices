import requests

class SuapError(Exception):
    """Erro genérico do SUAP."""
    pass

class SuapInvalidCredentials(SuapError):
    """Usuário ou senha inválidos."""
    pass

class SuapForbidden(SuapError):
    """Usuário sem permissão."""
    pass

class SuapNotFound(SuapError):
    """Endpoint não encontrado."""
    pass

class SuapServerError(SuapError):
    """Erro interno no SUAP."""
    pass

class SuapUnauthorized(SuapError):
    """Token inválido ou expirado."""
    pass


def suap_login(username, password):
    """Tenta autenticar no SUAP e retorna o token de acesso ou lança exceções."""
    url_token = "https://suap.ifsuldeminas.edu.br/api/token/pair"
    payload = {"username": username, "password": password}

    try:
        response = requests.post(url_token, json=payload, timeout=5)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 400:
            raise SuapError("Requisição inválida. Verifique os dados enviados.")

        elif response.status_code == 401:
            raise SuapInvalidCredentials("Usuário ou senha incorretos.")

        elif response.status_code == 403:
            raise SuapForbidden("Acesso negado. Você não tem permissão para usar este recurso.")

        elif response.status_code == 404:
            raise SuapNotFound("Endpoint do SUAP não encontrado.")

        elif response.status_code >= 500:
            raise SuapServerError("Erro interno no SUAP. Tente novamente mais tarde.")

        else:
            raise SuapError(f"Erro inesperado (código {response.status_code}).")

    except requests.exceptions.Timeout:
        raise SuapError("Tempo de conexão esgotado (timeout).")

    except requests.exceptions.ConnectionError:
        raise SuapError("Erro de conexão com o SUAP.")

    except requests.exceptions.RequestException as e:
        raise SuapError(f"Erro na requisição: {e}")


def get_user_info(token):
    """Busca os dados do usuário no SUAP usando o token de acesso.
       Lança exceções em caso de erro."""
    url_info = "https://suap.ifsuldeminas.edu.br/api/v2/minhas-informacoes/meus-dados/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url_info, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Filtrando apenas os campos desejados
            return {
                "id": data.get("id"),
                "nome_usual": data.get("nome_usual"),
                "tipo_vinculo": data.get("tipo_vinculo"),
                "url_foto_150x200": data.get("url_foto_150x200"),
                "url_foto_75x100": data.get("url_foto_75x100"),
            }

        elif response.status_code == 401:
            raise SuapUnauthorized("Token inválido ou expirado.")

        elif response.status_code == 403:
            raise SuapForbidden("Acesso negado ao recurso de informações do usuário.")

        elif response.status_code == 404:
            raise SuapNotFound("Endpoint de informações do usuário não encontrado.")

        elif response.status_code >= 500:
            raise SuapServerError("Erro interno no SUAP ao buscar informações do usuário.")

        else:
            raise SuapError(f"Erro inesperado ao consultar usuário (código {response.status_code}).")

    except requests.exceptions.Timeout:
        raise SuapError("Tempo de conexão esgotado (timeout).")

    except requests.exceptions.ConnectionError:
        raise SuapError("Erro de conexão com o SUAP.")

    except requests.exceptions.RequestException as e:
        raise SuapError(f"Erro na requisição: {e}")