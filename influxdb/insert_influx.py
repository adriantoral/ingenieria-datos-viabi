from influxdb_client import InfluxDBClient, Point
import datetime

# 🔹 Configuración de InfluxDB
INFLUX_URL = "http://172.24.20.152:8086"  # Cambia si usas WSL
INFLUX_TOKEN = "_EhQWPn5hzlOCqQ5klBt7IkmdM8lnIdet-nvVkDMOwmI-lMA3wkF8VQaBd0WC7HAe_SAJ_9pyZCktFnjl_qd-Q=="  # Copia el token generado en la Web UI
ORG = "VIABI"  # Nombre de la organización
BUCKET = "sensores"  # Nombre del bucket

# 🔹 Conectar con InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
write_api = client.write_api()
try:
    # 🔹 Crear un punto de datos
    point = (
        Point("temperatura")  # Nombre de la medición
        .tag("ubicacion", "cocina")  # Etiqueta opcional
        .field("valor", 27.5)  # Valor a almacenar
        .time(datetime.datetime.utcnow())  # Hora actual en UTC
    )

    # 🔹 Insertar en la base de datos
    write_api.write(bucket=BUCKET, org=ORG, record=point)

    print("✅ Datos insertados en InfluxDB.")

finally:
    # 🔹 Cerrar correctamente la conexión
    write_api.close()
    client.close()