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

# Configuración de buffers
BUFFER_SIZE = 3000  # 5 minutos a ~10fps (10*60*5)
MIN_BUFFER_TO_START = 100  # Buffer mínimo para comenzar

# Buffers para cada cámara
buffer_cam1 = deque(maxlen=BUFFER_SIZE)
buffer_cam2 = deque(maxlen=BUFFER_SIZE)
buffer_timestamps = deque(maxlen=BUFFER_SIZE)

stream_active = False

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
    return render_template('index.html')

@socketio.on('init_stream')
def handle_init_stream():
    global stream_active
    if not stream_active:
        stream_active = True
        socketio.start_background_task(start_stream)

def start_stream():
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(1)
    
    try:
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            if not ret1 or not ret2:
                print("Error leyendo frames de las cámaras")
                break

            # Procesar frames
            _, buffer1 = cv2.imencode('.jpg', frame1)
            _, buffer2 = cv2.imencode('.jpg', frame2)

            frame_base64_1 = base64.b64encode(buffer1).decode('utf-8')
            frame_base64_2 = base64.b64encode(buffer2).decode('utf-8')
            current_time = datetime.now().strftime("%H:%M:%S")

            # Almacenar en buffers
            buffer_cam1.append(frame_base64_1)
            buffer_cam2.append(frame_base64_2)
            buffer_timestamps.append(current_time)

            # Calcular porcentaje de carga
            buffer_percent = min(100, (len(buffer_cam1) / MIN_BUFFER_TO_START) * 100)
            
            # Enviar actualización del buffer
            socketio.emit('buffer_update', {
                'size': len(buffer_cam1),
                'percent': buffer_percent,
                'total': MIN_BUFFER_TO_START
            })

            # Enviar imágenes en tiempo real
            if len(buffer_cam1) >= MIN_BUFFER_TO_START:
                socketio.emit('image_cam1', {'image': frame_base64_1, 'time': current_time})
                socketio.emit('image_cam2', {'image': frame_base64_2, 'time': current_time})

            eventlet.sleep(0.1)  # Controlar la tasa de frames (~10fps)
    except Exception as e:
        print(f"Error en el stream: {str(e)}")
    finally:
        cap1.release()
        cap2.release()
        global stream_active
        stream_active = False
        print("Stream detenido")

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


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    
