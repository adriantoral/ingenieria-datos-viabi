import pika

PIKA_PARAMS = {
    "host": '192.168.49.2',  # IP del servicio RabbitMQ del loadbalancer
    "port": 30743,  # Puerto del servicio RabbitMQ del loadbalancer
    "credentials": pika.PlainCredentials('admin', 'admin')
}
