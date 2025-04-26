import eventlet
eventlet.monkey_patch()  # Primero, antes de cualquier import

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
BUFFER_SIZE = 1000  # Buffer de 1000 imágenes
MIN_BUFFER_TO_START = 100  # Mostrar contenido al 10% para pruebas

# Buffers principales
image_buffer = deque(maxlen=BUFFER_SIZE)
time_buffer = deque(maxlen=BUFFER_SIZE)

# Buffers adicionales
additional_buffer_1 = deque(maxlen=BUFFER_SIZE)
additional_buffer_2 = deque(maxlen=BUFFER_SIZE)
additional_buffer_3 = deque(maxlen=BUFFER_SIZE)

latest_image = None
latest_time = None
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
                break

            _, buffer1 = cv2.imencode('.jpg', frame1)
            _, buffer2 = cv2.imencode('.jpg', frame2)

            frame_base64_1 = base64.b64encode(buffer1).decode('utf-8')
            frame_base64_2 = base64.b64encode(buffer2).decode('utf-8')
            current_time = datetime.now().strftime("%H:%M:%S")

            # Actualizar buffers
            global latest_image, latest_time
            latest_image = frame_base64_1
            latest_time = current_time
            image_buffer.append(frame_base64_1)
            time_buffer.append(current_time)
            additional_buffer_1.append(frame_base64_1)
            additional_buffer_2.append(frame_base64_2)
            additional_buffer_3.append((frame_base64_1, frame_base64_2))

            # Calcular porcentaje de carga
            buffer_percent = min(100, (len(image_buffer) / BUFFER_SIZE) * 100)
            socketio.emit('buffer_update', {
                'size': len(image_buffer),
                'percent': buffer_percent,
                'total': BUFFER_SIZE
            })

            # Mostrar imágenes cuando alcancemos el mínimo
            if len(image_buffer) >= MIN_BUFFER_TO_START:
                socketio.emit('image_cam1', {'image': frame_base64_1, 'time': current_time})
                socketio.emit('image_cam2', {'image': frame_base64_2, 'time': current_time})

            eventlet.sleep(0.05)
    finally:
        cap1.release()
        cap2.release()
        global stream_active
        stream_active = False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)