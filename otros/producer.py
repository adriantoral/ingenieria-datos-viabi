import pika


# Configuración de conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(**{
    "host": '192.168.56.1',  # IP del servicio RabbitMQ del loadbalancer
    "port": 30976,  # Puerto del servicio RabbitMQ del loadbalancer
    "credentials": pika.PlainCredentials('admin', 'admin')
}))
channel = connection.channel()

# Declarar una cola llamada 'queueBasica'
channel.queue_declare(queue='queueBasica')

# Leer imagen de un fichero local
image_path = 'ensaimada_01.jpg'  # Ruta de la imagen a enviar
with open(image_path, 'rb') as image_file:
    image_bytes = image_file.read()

# Enviar la imagen como mensaje a la cola 'queueBasica'
channel.basic_publish(
    exchange='',
    routing_key='queueBasica',
    body=image_bytes
)

# Cerrar la conexión
print(f"Imagen enviada desde {image_path}")
connection.close()