from minio import Minio
from datetime import timedelta

# 🔹 Configuración de MinIO
MINIO_URL = "172.24.20.152:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "intrusiones"

# 🔹 Crear cliente MinIO
minio_client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

def get_presigned_url(image_name, expiration_seconds=3600):
    """Genera un enlace temporal para visualizar una imagen en el navegador sin descargarla."""
    try:
        url = minio_client.presigned_get_object(
            BUCKET_NAME, 
            image_name, 
            expires=timedelta(seconds=expiration_seconds),
            response_headers={
                "Content-Type": "image/jpeg"
                }  # Forzar que se muestre como imagen
        )
        return url
    except Exception as e:
        print(f"❌ Error al generar URL firmada: {e}")
        return None

# 🔹 Obtener el link para ver la imagen sin descargar
image_name = "ALE29.jpg"
url = get_presigned_url(image_name)

if url:
    print(f"✅ Visualiza la imagen aquí: {url}")
