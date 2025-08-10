# -----------------------------------------------------------------------------
# ARQUIVO: event_consumer.py (NOVO! Crie na raiz do persistence-service)
# DESCRIÇÃO: Ouve eventos do RabbitMQ e atualiza o banco de dados.
# -----------------------------------------------------------------------------
import pika
import json
import os
import django
import time

# Configura o ambiente do Django para que possamos usar os modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'persistence_project.settings')
django.setup()

from profiles.models import ActorUser, Common, Service, Admin, Coordinator, Security

def process_user_event(ch, method, properties, body):
    """
    Função callback que processa mensagens da fila 'user_events'.
    """
    print(f" [x] Recebido evento: {body.decode()}")
    try:
        data = json.loads(body)
        event_type = data.get('event_type')
        user_id = data.get('user_id')
        username = data.get('username')
        role = data.get('role')

        if not all([event_type, user_id, username, role]):
            print(" [!] Mensagem de evento malformada. Descartando.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if event_type in ['user_created', 'user_updated']:
            # Atualiza ou cria o ActorUser
            ActorUser.objects.update_or_create(
                user_id=user_id,
                defaults={'username': username, 'role': role}
            )

            # Mapeia o 'role' para o modelo de perfil correspondente
            role_to_model = {
                'padrao': Common,
                'servidor': Service,
                'administrador': Admin,
                'coordenador': Coordinator,
                'seguranca': Security,
            }
            
            # Garante que o perfil correto existe
            TargetModel = role_to_model.get(role)
            if TargetModel:
                TargetModel.objects.get_or_create(user_id=user_id)
                print(f" [✔] Perfil '{role}' garantido para o usuário {user_id}.")

            # Aqui você pode adicionar lógica para remover perfis antigos se o papel do usuário mudar
        
        # Confirma que a mensagem foi processada com sucesso
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        print(" [!] Erro ao decodificar JSON. Mensagem descartada.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Erro ao processar evento: {e}")
        # Em um sistema de produção, você poderia reenfileirar a mensagem (ch.basic_nack)
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue='user_events', durable=True)
            
            # Consome mensagens da fila
            channel.basic_consume(queue='user_events', on_message_callback=process_user_event)

            print(' [*] Aguardando por eventos de usuário. Para sair, pressione CTRL+C')
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Erro de conexão com RabbitMQ: {e}. Tentando reconectar em 5 segundos...")
            time.sleep(5)
        except KeyboardInterrupt:
            print('Interrompido')
            break

if __name__ == '__main__':
    main()