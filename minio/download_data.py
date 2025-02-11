from minio import Minio
import os

# Configuración de MinIO
MINIO_URL = "172.24.20.152:9000"  # Cambia a tu IP de WSL si accedes desde Windows
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "datos"
DOWNLOAD_FOLDER = "descargas"

# Crear cliente MinIO
client = Minio(
    MINIO_URL,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False  # Cambiar a True si usas HTTPS
)

# Verificar si el bucket existe
if not client.bucket_exists(BUCKET_NAME):
    print(f"El bucket '{BUCKET_NAME}' no existe.")
    exit()

# Crear carpeta local para descargas si no existe
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Listar y descargar archivos del bucket
objects = client.list_objects(BUCKET_NAME)
for obj in objects:
    file_path = os.path.join(DOWNLOAD_FOLDER, obj.object_name)
    client.fget_object(BUCKET_NAME, obj.object_name, file_path)
    print(f"Archivo descargado: {file_path}")

print("✅ Descarga completada.")
