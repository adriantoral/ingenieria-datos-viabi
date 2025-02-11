import pika

from config import PIKA_PARAMS

# Configuración de conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(**PIKA_PARAMS))
channel = connection.channel()

# Declarar una cola llamada 'queueBasica'
channel.queue_declare(queue='queueBasica')

# Enviar un mensaje a la cola 'queueBasica'
message = '¡Hola desde Python!'
channel.basic_publish(
    exchange='',
    routing_key='queueBasica',
    body=message
)

# Cerrar la conexión
print(f"Mensaje enviado: {message}")
connection.close()
