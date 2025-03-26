from minio import Minio
import json
import os

# Configuración de MinIO
MINIO_URL = "172.24.20.152:9000"  # Cambia a tu IP de WSL si accedes desde Windows
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "datos"

# Crear cliente MinIO
client = Minio(
    MINIO_URL,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False  # Cambiar a True si usas HTTPS
)

# Crear bucket si no existe
if not client.bucket_exists(BUCKET_NAME):
    client.make_bucket(BUCKET_NAME)

# Datos a almacenar
data = [
    {"id": 1, "nombre": "Juan", "edad": 30},
    {"id": 2, "nombre": "Maria", "edad": 25},
]

# Guardar en JSON y subir a MinIO
json_filename = "datos.json"
with open(json_filename, "w") as f:
    json.dump(data, f)

client.fput_object(BUCKET_NAME, json_filename, json_filename)
print(f"Archivo '{json_filename}' subido a MinIO.")

# Limpiar archivo local
os.remove(json_filename)
