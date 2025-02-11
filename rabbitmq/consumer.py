import pika

from config import PIKA_PARAMS

# Configuración de conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(**PIKA_PARAMS))
channel = connection.channel()

# Declarar la cola 'queueBasica' para asegurarse de que existe
channel.queue_declare(queue='queueBasica')


# Función de callback para procesar el mensaje
def callback(ch, method, properties, body): print(f"Mensaje recibido: {body.decode()}")


# Consumir mensajes de la cola 'queueBasica'
channel.basic_consume(queue='queueBasica', on_message_callback=callback, auto_ack=True)
print('Esperando mensajes. Para salir presiona Ctrl+C')

# Iniciar el consumo de mensajes
channel.start_consuming()
