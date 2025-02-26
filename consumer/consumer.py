import pika
import io
import cv2
import numpy as np
import boto3
import uuid
import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision

# Configuración de conexiones
RABBITMQ_QUEUE = "videos"
MINIO_BUCKET = "videos-procesados"
INFLUXDB_BUCKET = "analisis"
INFLUXDB_ORG = "mi-org"

# Configurar el log para manejar errores
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Conectar a MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

# Conectar a InfluxDB
influx_client = InfluxDBClient(url="http://influxdb:8086", token=" ", org=INFLUXDB_ORG)
write_api = influx_client.write_api()

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE)


def save_video_to_minio(video_bytes):
    """
    Guarda el video en MinIO y devuelve su clave (nombre en el bucket).
    """
    video_id = str(uuid.uuid4()) + ".mp4" 
    try:
        s3_client.put_object(Bucket=MINIO_BUCKET, Key=video_id, Body=video_bytes)
        logger.info(f"Video guardado en MinIO: {video_id}")
        return video_id
    except Exception as e:
        logger.error(f"Error al guardar el video en MinIO: {e}")
        return None


def analyze_video(video_path):
    """
    Analiza un video y devuelve estadísticas como cantidad de frames, FPS, resolución, duración, etc.
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logger.error("Error: No se pudo abrir el video.")
        return None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return {
        "frames": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration": duration
    }


def process_video(body):
    """
    Procesa un video recibido:
    1. Guarda el video en MinIO.
    2. Descarga el video y analiza sus frames, resolución y duración.
    3. Guarda los metadatos en InfluxDB.
    """
    try:
        video_key = save_video_to_minio(body)
        if not video_key:
            return

        # Descargar el video desde MinIO para análisis
        video_path = f"/tmp/{video_key}"
        s3_client.download_file(MINIO_BUCKET, video_key, video_path)

        # Analizar el video
        analysis = analyze_video(video_path)
        if not analysis:
            return

        # Guardar metadata en InfluxDB
        point = Point("analisis_video") \
            .tag("video", video_key) \
            .field("frames", analysis["frames"]) \
            .field("fps", analysis["fps"]) \
            .field("resolucion", f"{analysis['width']}x{analysis['height']}") \
            .field("duracion_segundos", analysis["duration"]) \
            .time(write_precision=WritePrecision.NS)

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        logger.info(f"Video {video_key} analizado y guardado en InfluxDB.")

    except Exception as e:
        logger.error(f"Error al procesar el video: {e}")


def callback(ch, method, properties, body):
    """
    Callback que se ejecuta cuando llega un video en RabbitMQ.
    Procesa el video y confirma el mensaje.
    """
    logger.info("Recibido video, procesando...")
    process_video(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar mensaje procesado


# Configurar RabbitMQ para recibir videos
channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

logger.info("Esperando videos en RabbitMQ...")
channel.start_consuming()