import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import base64
from collections import deque
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

BUFFER_SIZE = 10000
image_buffer = deque(maxlen=BUFFER_SIZE)
latest_image = None  # Última imagen en vivo

# Configuración de InfluxDB
CONFIG_INFLUX = {
	'url'   : os.getenv( 'CONFIG_INFLUX_URL' ),
	'token' : os.getenv( 'CONFIG_INFLUX_TOKEN' ),
	'org'   : os.getenv( 'CONFIG_INFLUX_ORG' ),
	'bucket': os.getenv( 'CONFIG_INFLUX_BUCKET' )
}

# Cliente de InfluxDB
_influx_client = InfluxDBClient(
	url=CONFIG_INFLUX['url'],
	token=CONFIG_INFLUX['token'],
	org=CONFIG_INFLUX['org']
)

query_api = _influx_client.query_api()

@app.route('/')
def index():
    global image_buffer
    image_buffer = deque(maxlen=BUFFER_SIZE)  # Reiniciar buffer al volver
    return render_template('index.html')

@app.route('/segundo_visores')
def segundo_visores():
    return render_template('segundo_visores.html')

def get_recent_intrusions():
    """Devuelve lista de (timestamp, probability) para intrusiones recientes"""
    query = f'''
    from(bucket: "{CONFIG_INFLUX['bucket']}")
      |> range(start: -6h)
      |> filter(fn: (r) => r._measurement == "intrusion_event")
      |> filter(fn: (r) => r._field == "probability" and r._value > 0.9)
      |> keep(columns: ["_time", "_value"])
      |> sort(columns: ["_time"])
      |> limit(n:1)
    '''

    result = query_api.query(org=CONFIG_INFLUX["org"], query=query)
    intrusions = []

    for table in result:
        for record in table.records:
            timestamp = record.get_time()
            prob = record.get_value()
            intrusions.append((timestamp, prob))
    
    return intrusions

def get_clip_images(event_time):
    """Recupera todas las imágenes ±2s desde el timestamp de un evento"""
    t0 = (event_time - timedelta(seconds=2)).isoformat()
    t1 = (event_time + timedelta(seconds=2)).isoformat()

    query = f'''
    from(bucket: "{CONFIG_INFLUX['bucket']}")
      |> range(start: time(v: "{t0}"), stop: time(v: "{t1}"))
      |> filter(fn: (r) => r._measurement == "intrusion_event")
      |> filter(fn: (r) => r._field == "image_url")
      |> keep(columns: ["_time", "_value"])
      |> sort(columns: ["_time"])
    '''

    result = query_api.query(org=CONFIG_INFLUX["org"], query=query)
    images = []

    for table in result:
        for record in table.records:
            url = record.get_value()
            if url:
                images.append(url)
    
    return images

@app.route('/tercer_visores')
def tercer_visores():
    intrusions = get_recent_intrusions()
    if not intrusions:
        return "<h3>No hay intrusiones recientes detectadas</h3>"

    # Seleccionamos la última intrusión
    latest_time, _ = intrusions[-1]
    image_urls = get_clip_images(latest_time)

    return render_template("tercer_visores.html", images=image_urls)

@socketio.on('start_stream')
def start_stream():
    global latest_image
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        latest_image = frame_base64  # Guardar la última imagen en vivo
        image_buffer.append(frame_base64)  # Agregar al buffer

        emit('image', {'image': frame_base64}, broadcast=True)
        socketio.sleep(0.05)

    cap.release()

@socketio.on('get_buffered_image')
def get_buffered_image(data):
    """
    Envía la imagen más reciente o una imagen del buffer.
    """
    index = int(data.get('index', -1))

    if index == -1:  # Solicitud de la última imagen en vivo
        if latest_image:
            emit('buffered_image', {'image': latest_image})
        else:
            emit('buffered_image', {'error': 'No hay imágenes aún'})
    elif 0 <= index < len(image_buffer):
        emit('buffered_image', {'image': image_buffer[index]})
    else:
        emit('buffered_image', {'error': 'Índice fuera de rango'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    