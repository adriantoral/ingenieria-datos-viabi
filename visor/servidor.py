import base64
from collections import deque
from datetime import datetime

import cv2
import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

eventlet.monkey_patch( )

app = Flask( __name__ )
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO( app, cors_allowed_origins="*", async_mode='eventlet' )

BUFFER_SIZE = 2400  # 20 FPS * 120 segundos = 2400 imágenes para 2 minutos
image_buffer = deque( maxlen=BUFFER_SIZE )
time_buffer = deque( maxlen=BUFFER_SIZE )

latest_image = None
latest_time = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/segundo_visores')
def segundo_visores():
    return render_template('segundo_visores.html')

@socketio.on('start_stream')
def start_stream():
    global latest_image, latest_time
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        current_time = datetime.now().strftime("%H:%M:%S")

        latest_image = frame_base64
        latest_time = current_time

        image_buffer.append(frame_base64)
        time_buffer.append(current_time)

        emit('image', {'image': frame_base64, 'time': current_time}, broadcast=True)
        socketio.sleep(0.05)

    cap.release()

@socketio.on('get_buffered_image')
def get_buffered_image(data):
    index = int(data.get('index', -1))
    
    if index == -1 and latest_image:
        emit('buffered_image', {'image': latest_image, 'time': latest_time})
    elif 0 <= index < len(image_buffer):
        emit('buffered_image', {'image': image_buffer[index], 'time': time_buffer[index]})
    else:
        emit('buffered_image', {'error': 'Índice fuera de rango'})

@socketio.on('get_buffer_size')
def get_buffer_size():
    buffer_length = len(image_buffer)
    emit('buffer_size', {'size': buffer_length})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
