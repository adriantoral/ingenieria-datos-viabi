import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone, timedelta
import random

# Parámetros de conexión
bucket = "mibucket"
org = "miorganizacion"
token = "ohypHupASVyeVyPeEcnuvruggxoC4lIX9hqaqzOmPN8tzB7Ew0vE1TAN2GB3gSY0VUETfZzbbGyPFd_F7P-Qcg=="
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Directorio con los frames
frame_dir = "./Frames"
base_url = "http://localhost:8000"

# Leer archivos de la carpeta
frame_files = sorted(os.listdir(frame_dir))

# Insertar cada frame
for i, filename in enumerate(frame_files):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        full_url = f"{base_url}/{filename}"
        probability = round(random.uniform(0.8, 1.0), 2)
        timestamp = datetime.now(timezone.utc) + timedelta(seconds=i)

        point = (
            Point("intrusion_event")
            .tag("image_name", filename)
            .field("probability", probability)
            .field("image_url", f"http://localhost:8000/{filename}")  # URL servida por HTTP
            .time(timestamp)
        )

        write_api.write(bucket=bucket, org=org, record=point)

print("Frames locales cargados en InfluxDB con URLs.")