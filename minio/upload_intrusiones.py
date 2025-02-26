from minio import Minio
from influxdb_client import InfluxDBClient, Point
import datetime
import os
import sys
from datetime import timedelta  # Para generar URLs temporales
import pika


# 🔹 Configuración de MinIO
MINIO_URL = "192.168.56.1:30779"  # Cambia a tu IP de WSL si accedes desde Windows
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "intrusiones"

# 🔹 Configuración de InfluxDB
INFLUX_URL = "192.168.56.1:30710"  # Cambia si usas WSL
INFLUX_TOKEN = "0XrHKGL2Gjx4wI7ArkTax5uW8CSzKZlb5fs6-U4nnnpfDHVo4Zh1kFn4tZg92trJs_mFo-Nni7MWy7PGWWh_rQ=="  # Copia el token generado en la Web UI
ORG = "miorganizacion"
BUCKET = "intrusiones"


# 🔹 Crear clientes para MinIO e InfluxDB
minio_client = Minio(MINIO_URL.replace("http://", ""), access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

def get_presigned_url(image_name, expiration_seconds=3600):
    """Genera un enlace temporal para visualizar la imagen en el navegador sin descargarla."""
    try:
        url = minio_client.presigned_get_object(
            BUCKET_NAME, 
            image_name, 
            expires=timedelta(seconds=expiration_seconds),
            response_headers={
                "Content-Type": "image/jpeg",  
                "Content-Disposition": "inline"
            }
        )
        return url
    except Exception as e:
        print(f"❌ Error al generar URL firmada: {e}")
        return None

def upload_image(image_bytes, probability=1.0):
    """Sube una imagen a MinIO y guarda la referencia en InfluxDB, consumiendo la imagen en formato bytes."""
    # 📌 1️⃣ Obtener el timestamp actual en UTC
    timestamp = datetime.datetime.utcnow().isoformat()

    # 📌 2️⃣ Generar un nombre único para la imagen (por ejemplo, usando la fecha y hora actual)
    image_name = f"intrusion_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.jpg"

    # 📌 3️⃣ Subir la imagen a MinIO utilizando put_object con un stream de bytes
    try:
        from io import BytesIO
        stream = BytesIO(image_bytes)
        image_length = len(image_bytes)
        minio_client.put_object(
            BUCKET_NAME,
            image_name,
            stream,
            image_length,
            content_type="image/jpeg"
        )
        print(f"✅ Imagen '{image_name}' subida a MinIO.")
    except Exception as e:
        print(f"❌ Error al subir la imagen a MinIO: {e}")
        return

    # 📌 4️⃣ Generar el link temporal para visualizar la imagen
    image_url = get_presigned_url(image_name, expiration_seconds=3600)  # 1 hora de validez

    # 📌 5️⃣ Conectar con InfluxDB y registrar el evento de intrusión
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = influx_client.write_api()
    try:
        point = (
            Point("intrusion_event")
            .tag("image_name", image_name)
            .field("probability", probability)
            .field("image_url", image_url)  # Guardamos el link de visualización
            .time(timestamp)
        )
        write_api.write(bucket=BUCKET, org=ORG, record=point)
        print(f"✅ Registro insertado en InfluxDB: {image_name}, Probabilidad: {probability}")
        print(f"🔗 Link de visualización: {image_url}")
    except Exception as e:
        print(f"❌ Error al escribir en InfluxDB: {e}")
    finally:
        write_api.close()
        influx_client.close()


# 📌 7️⃣ Leer parámetros desde la línea de comandos
if __name__ == "__main__":


    # Configuración de conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(**{
    "host": '192.168.56.1',  # IP del servicio RabbitMQ del loadbalancer
    "port": 30976,  # Puerto del servicio RabbitMQ del loadbalancer
    "credentials": pika.PlainCredentials('admin', 'admin')
}
))
    channel = connection.channel()

    # Declarar la cola 'queueBasica' para asegurarse de que existe
    channel.queue_declare(queue='queueBasica')


    # Función de callback para procesar el mensaje
    def callback(ch, method, properties, body):
        # Si deseas extraer la probabilidad desde las propiedades (por ejemplo, en headers)
        probability = 1.0  # Valor por defecto
        if properties.headers and 'probability' in properties.headers:
            probability = properties.headers['probability']
        upload_image(body, probability)


    # Consumir mensajes de la cola 'queueBasica'
    channel.basic_consume(queue='queueBasica', on_message_callback=callback, auto_ack=True)
    print('Esperando mensajes. Para salir presiona Ctrl+C')

    # Iniciar el consumo de mensajes
    channel.start_consuming()

