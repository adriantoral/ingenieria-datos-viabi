from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import eventlet
from collections import deque

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Buffer para almacenar frames recientes (30 segundos a ~20 FPS)
MAX_FPS = 20
MAX_SECONDS = 30
BUFFER_SIZE = MAX_FPS * MAX_SECONDS
frame_buffer = deque(maxlen=BUFFER_SIZE)

rewind_mode = False
rewind_index = 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def start_stream():
    global rewind_mode, rewind_index
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo capturar el frame.")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        frame_buffer.append(frame_bytes)

        if not rewind_mode:
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            emit('image', {'image': frame_base64})
        else:
            if rewind_index < len(frame_buffer):
                rewind_frame = frame_buffer[-rewind_index - 1]
                frame_base64 = base64.b64encode(rewind_frame).decode('utf-8')
                emit('image', {'image': frame_base64})
                rewind_index += 1
                if rewind_index >= len(frame_buffer):
                    rewind_mode = False
                    rewind_index = 0

        socketio.sleep(1.0 / MAX_FPS)

    cap.release()

@socketio.on('rewind')
def handle_rewind(data):
    global rewind_mode, rewind_index
    seconds = data.get('seconds', 5)
    frames_to_rewind = min(seconds * MAX_FPS, len(frame_buffer))
    if frames_to_rewind > 0:
        rewind_mode = True
        rewind_index = frames_to_rewind
    else:
        emit('error', {'message': 'No hay suficientes frames para retroceder.'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
