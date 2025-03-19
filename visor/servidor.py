from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import eventlet
from collections import deque  # 🆕 Para buffer circular

eventlet.monkey_patch()  # Permite que SocketIO funcione con Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 🆕 Buffer de los últimos frames (~10 segundos a 20 fps)
frame_buffer = deque(maxlen=200)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def start_stream():
    cap = cv2.VideoCapture(1)  # ⚠️ Cámara IVCam (ajustar si no funciona)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        frame_buffer.append(frame_base64)  # 🆕 Guardamos frame en buffer

        emit('image', {'image': frame_base64})

        socketio.sleep(0.05)  # Evita saturar red

    cap.release()

# 🆕 Retroceder segundos (máx 10s por buffer)
@socketio.on('rewind')
def handle_rewind(seconds):
    fps = 20
    frames_to_send = int(fps * seconds)
    frames = list(frame_buffer)[-frames_to_send:]

    for frame_base64 in frames:
        emit('image', {'image': frame_base64})
        socketio.sleep(0.05)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
