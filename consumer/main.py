import os
import random
import signal
import sys
from datetime import datetime, timezone
from io import BytesIO

from PIL import Image, ImageDraw
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import WriteOptions
from minio import Minio
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

# Configuraciones
CONFIG_MINIO = {
    'url': os.getenv('CONFIG_MINIO_URL'),
    'access_key': os.getenv('CONFIG_MINIO_ACCESS_KEY'),
    'secret_key': os.getenv('CONFIG_MINIO_SECRET_KEY'),
    'bucket': os.getenv('CONFIG_MINIO_BUCKET')
}

CONFIG_INFLUX = {
    'url': os.getenv('CONFIG_INFLUX_URL'),
    'token': os.getenv('CONFIG_INFLUX_TOKEN'),
    'org': os.getenv('CONFIG_INFLUX_ORG'),
    'bucket': os.getenv('CONFIG_INFLUX_BUCKET')
}

CONFIG_RABBITMQ = {
    'url': os.getenv('CONFIG_RABBITMQ_URL'),
    'username': os.getenv('CONFIG_RABBITMQ_USERNAME'),
    'password': os.getenv('CONFIG_RABBITMQ_PASSWORD'),
    'queue': os.getenv('CONFIG_RABBITMQ_QUEUE')
}


def try_catch_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return None
    return wrapper


def create_instances():
    minio_client = Minio(
        CONFIG_MINIO['url'],
        access_key=CONFIG_MINIO['access_key'],
        secret_key=CONFIG_MINIO['secret_key'],
        secure=False
    )

    influx_client = InfluxDBClient(
        url=CONFIG_INFLUX['url'],
        token=CONFIG_INFLUX['token'],
        org=CONFIG_INFLUX['org']
    )
    write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

    rabbitmq_client = BlockingConnection(
        ConnectionParameters(
            host=CONFIG_RABBITMQ['url'].split(':')[0],
            port=int(CONFIG_RABBITMQ['url'].split(':')[1]),
            credentials=PlainCredentials(CONFIG_RABBITMQ['username'], CONFIG_RABBITMQ['password'])
        )
    )

    return minio_client, influx_client, write_api, rabbitmq_client


@try_catch_decorator
def process_image(image_bytes):
    """ Procesa la imagen usando PIL, agregando un recuadro aleatorio si la probabilidad es mayor al 80% """
    image = Image.open(BytesIO(image_bytes))
    probability = random.uniform(0, 1)  # Simula detección de intrusión
    flagged = False

    if probability >= 0.8:
        flagged = True
        width, height = image.size
        x1, y1 = random.randint(0, width // 2), random.randint(0, height // 2)
        x2, y2 = random.randint(width // 2, width), random.randint(height // 2, height)
        draw = ImageDraw.Draw(image)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue(), probability, flagged


@try_catch_decorator
def upload_image_to_minio(minio_client, image_bytes):
    """ Sube la imagen a Minio y genera una URL firmada """
    image_name = f"intrusion_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.jpg"
    minio_client.put_object(
        CONFIG_MINIO['bucket'],
        image_name,
        BytesIO(image_bytes),
        len(image_bytes)
    )
    image_url = minio_client.presigned_get_object(
        CONFIG_MINIO['bucket'],
        image_name,
        response_headers={"Content-Type": "image/jpeg", "Content-Disposition": "inline"}
    )
    return image_name, image_url


@try_catch_decorator
def upload_image_to_influx(write_api, image_name, image_url, probability, flagged):
    """ Guarda los metadatos en InfluxDB incluyendo la probabilidad de intrusión """
    point = (
        Point("intrusion_event")
        .tag("image_name", image_name)
        .field("probability", probability)
        .field("image_url", image_url)
        .field("flagged", int(flagged))  # 1 si hay intrusión, 0 si no
        .time(datetime.now(timezone.utc).isoformat())
    )
    write_api.write(bucket=CONFIG_INFLUX['bucket'], record=point)


def callback(minio_client, write_api, ch, method, properties, body):
    """ Callback de RabbitMQ, procesa la imagen y la almacena en Minio/InfluxDB """
    try:
        print('Procesando frame...')
        processed_image, probability, flagged = process_image(body)
        image_name, image_url = upload_image_to_minio(minio_client, processed_image)
        if image_url:
            upload_image_to_influx(write_api, image_name, image_url, probability, flagged)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error en callback: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def signal_handler(influx_client, rabbit, sig, frame):
    if influx_client:
        influx_client.close()
    if rabbit:
        rabbit.close()
    sys.exit(0)


if __name__ == '__main__':
    minio_client, influx_client, write_api, rabbitmq_client = create_instances()

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(influx_client, rabbitmq_client, sig, frame))
    signal.signal(signal.SIGTSTP, lambda sig, frame: signal_handler(influx_client, rabbitmq_client, sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(influx_client, rabbitmq_client, sig, frame))

    channel = rabbitmq_client.channel()
    channel.queue_declare(queue=CONFIG_RABBITMQ['queue'], durable=True)

    channel.basic_consume(
        queue=CONFIG_RABBITMQ['queue'],
        auto_ack=False,
        on_message_callback=lambda ch, method, properties, body: callback(
            minio_client,
            write_api,
            ch,
            method,
            properties,
            body
        )
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        signal_handler(influx_client, rabbitmq_client, None, None)
