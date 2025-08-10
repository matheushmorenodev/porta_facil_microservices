# -----------------------------------------------------------------------------
# ARQUIVO: main.py
# DESCRIÇÃO: A aplicação FastAPI principal para o Command Service.
# -----------------------------------------------------------------------------
import os
import requests
import paho.mqtt.client as mqtt
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

# --- Configuração dos Endereços dos Serviços ---
# Em um ambiente Docker, usaríamos os nomes dos serviços (ex: 'http://persistence-service:8002')
# Para desenvolvimento local, usamos localhost.
PERSISTENCE_SERVICE_URL = os.environ.get("PERSISTENCE_SERVICE_URL", "http://localhost:8002")
LOG_SERVICE_URL = os.environ.get("LOG_SERVICE_URL", "http://localhost:8003")
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))

app = FastAPI(title="Command Service")

class CommandPayload(BaseModel):
    mac_address: str
    command: str # Ex: "abrir", "status"

def log_action(user_id: int, level: str, message: str):
    """Envia um log para o Log Service."""
    try:
        payload = {
            "service_name": "command-service",
            "user_id": user_id,
            "level": level,
            "message": message
        }
        requests.post(f"{LOG_SERVICE_URL}/log/", json=payload, timeout=2)
    except requests.RequestException as e:
        print(f"ERRO: Não foi possível enviar log para o Log Service: {e}")

def publish_mqtt_command(mac_address: str, command: str):
    """Publica um comando no tópico MQTT apropriado."""
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        topic = f"portas/{mac_address}/command"
        client.publish(topic, command)
        client.disconnect()
        print(f"Comando '{command}' publicado no tópico '{topic}'")
        return True
    except Exception as e:
        print(f"ERRO: Falha ao publicar no MQTT: {e}")
        return False

@app.post("/command/")
async def execute_command(payload: CommandPayload, request: Request):
    """
    Recebe um comando, verifica a permissão e o publica no MQTT.
    """
    # 1. Extrai informações de usuário dos headers (injetados pelo API Gateway)
    try:
        user_id = int(request.headers.get("X-User-ID"))
        user_role = request.headers.get("X-User-Role")
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Headers de autenticação ausentes ou inválidos.")

    # 2. Verifica permissão com o Persistence Service
    # (Vamos precisar adicionar este endpoint no persistence-service depois)
    try:
        # Idealmente, teríamos um endpoint específico para checar permissão
        # Por enquanto, vamos simular essa checagem.
        # Em um cenário real:
        # params = {'user_id': user_id, 'mac_address': payload.mac_address}
        # response = requests.get(f"{PERSISTENCE_SERVICE_URL}/api/internal/check-permission", params=params)
        # if response.status_code != 200:
        #     raise HTTPException(status_code=403, detail="Acesso negado pelo serviço de persistência.")
        
        # Simulação para desenvolvimento:
        print(f"Simulando verificação de permissão para User ID: {user_id} e MAC: {payload.mac_address}")
        has_permission = True # Assumindo que tem permissão para o teste
        
    except requests.RequestException as e:
        log_action(user_id, "ERROR", f"Falha ao conectar com o Persistence Service: {e}")
        raise HTTPException(status_code=503, detail="Não foi possível verificar a permissão.")

    if not has_permission:
        log_action(user_id, "WARNING", f"Tentativa de acesso negado ao MAC {payload.mac_address}")
        raise HTTPException(status_code=403, detail="Você não tem permissão para controlar este dispositivo.")

    # 3. Publica o comando no MQTT
    success = publish_mqtt_command(payload.mac_address, payload.command)

    if not success:
        log_action(user_id, "ERROR", f"Falha ao enviar comando '{payload.command}' para o MAC {payload.mac_address} via MQTT.")
        raise HTTPException(status_code=500, detail="Falha ao enviar comando para o dispositivo.")

    # 4. Registra o log de sucesso
    log_action(user_id, "INFO", f"Comando '{payload.command}' executado com sucesso para o MAC {payload.mac_address}")

    return {"status": "success", "detail": f"Comando '{payload.command}' enviado para {payload.mac_address}."}

@app.get("/")
def read_root():
    return {"service": "Command Service", "status": "online"}
