import eventlet
eventlet.monkey_patch()

import base64
from collections import deque
from datetime import datetime
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)