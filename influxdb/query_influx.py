from influxdb_client import InfluxDBClient

# 🔹 Configuración de InfluxDB
INFLUX_URL = "http://172.24.20.152:8086"  # IP de WSL
INFLUX_TOKEN = "_EhQWPn5hzlOCqQ5klBt7IkmdM8lnIdet-nvVkDMOwmI-lMA3wkF8VQaBd0WC7HAe_SAJ_9pyZCktFnjl_qd-Q=="
ORG = "VIABI"
BUCKET = "sensores"

# 🔹 Conectar con InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
query_api = client.query_api()

# 🔹 Consulta de los últimos datos (última hora)
query = f'''
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "temperatura")
  |> sort(columns: ["_time"], desc: true)  // Ordenar por tiempo
'''

# 🔹 Ejecutar la consulta
tables = query_api.query(query)

# 🔹 Mostrar resultados
print("\n📊 **Resultados de la consulta:**\n")
for table in tables:
    for record in table.records:
        print(f"📌 {record.get_time()} - {record.get_measurement()} - {record.get_value()} {record.get_field()}")
