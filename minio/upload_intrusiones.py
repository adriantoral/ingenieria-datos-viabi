from minio import Minio
from influxdb_client import InfluxDBClient, Point
import datetime
import os
import sys
from datetime import timedelta  # Para generar URLs temporales

# 🔹 Configuración de MinIO
MINIO_URL = "172.24.20.152:9000"  # Cambia a tu IP de WSL si accedes desde Windows
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "intrusiones"

# 🔹 Configuración de InfluxDB
INFLUX_URL = "172.24.20.152:8086"  # Cambia si usas WSL
INFLUX_TOKEN = "_EhQWPn5hzlOCqQ5klBt7IkmdM8lnIdet-nvVkDMOwmI-lMA3wkF8VQaBd0WC7HAe_SAJ_9pyZCktFnjl_qd-Q=="  # Copia el token generado en la Web UI
ORG = "VIABI"
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

def upload_image(image_path, probability):
    """Sube una imagen a MinIO y guarda la referencia en InfluxDB."""
    
    # 📌 1️⃣ Verificar si la imagen existe
    if not os.path.exists(image_path):
        print(f"❌ Error: La imagen '{image_path}' no existe.")
        return
    
    # 📌 2️⃣ Obtener el timestamp actual en UTC
    timestamp = datetime.datetime.utcnow().isoformat()

    # 📌 3️⃣ Obtener el nombre del archivo
    image_name = os.path.basename(image_path)

    # 📌 4️⃣ Subir la imagen a MinIO
    try:
        minio_client.fput_object(BUCKET_NAME, image_name, image_path)
        print(f"✅ Imagen '{image_name}' subida a MinIO.")
    except Exception as e:
        print(f"❌ Error al subir la imagen a MinIO: {e}")
        return

    # 📌 5️⃣ Generar el link temporal para visualizar la imagen
    image_url = get_presigned_url(image_name, expiration_seconds=3600)  # 1 hora de validez

    # 📌 6️⃣ Conectar con InfluxDB y registrar la imagen
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
    if len(sys.argv) != 3:
        print("❌ Uso: python3 upload_intrusion.py <ruta_imagen> <probabilidad>")
        sys.exit(1)

    image_path = sys.argv[1]
    probability = float(sys.argv[2])  

    upload_image(image_path, probability)
