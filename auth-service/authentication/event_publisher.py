import pika
import json
import os

# Pega a URL do RabbitMQ das variáveis de ambiente, com um fallback para localhost
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

def publish_event(queue_name, event_data):
    """
    Publica um evento genérico em uma fila específica do RabbitMQ.
    """
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Garante que a fila existe
        channel.queue_declare(queue=queue_name, durable=True)

        # Publica a mensagem
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(event_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente
            ))
        print(f" [x] Evento publicado na fila '{queue_name}': {event_data}")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"ERRO: Não foi possível conectar ao RabbitMQ. {e}")
        # Em um sistema real, aqui você poderia ter um fallback (ex: salvar em banco local para reenviar depois)
    except Exception as e:
        print(f"ERRO ao publicar evento: {e}")
