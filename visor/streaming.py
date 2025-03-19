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

# Buffer circular para almacenar los últimos frames (10 segundos a 20 fps = 200 frames)
frame_buffer = deque(maxlen=200)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def start_stream():
    cap = cv2.VideoCapture(1)  # Cámara. Cambia el índice si no funciona.

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Guardamos el frame en el buffer
            frame_buffer.append(frame_base64)

            # Enviamos el frame en vivo
            emit('image', {'image': frame_base64})

            socketio.sleep(0.05)
    finally:
        cap.release()

@socketio.on('rewind')
def handle_rewind(seconds):
    # Calculamos cuántos frames equivale ese tiempo (asumimos 20 fps)
    fps = 20
    frames_to_send = int(fps * seconds)
    frames = list(frame_buffer)[-frames_to_send:]

    for frame_base64 in frames:
        emit('image', {'image': frame_base64})
        socketio.sleep(0.05)  # Imitamos tiempo real

    # Vuelve al tiempo real automáticamente

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
