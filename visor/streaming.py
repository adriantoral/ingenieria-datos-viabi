import cv2
import base64
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# IP y puerto de EpocCam (ajusta si es necesario)
VIDEO_SOURCE = "http://192.168.21.28:4747/video"
cap = cv2.VideoCapture(VIDEO_SOURCE)

frame_buffer = []  # Buffer de frames (timestamp, frame)
BUFFER_SECONDS = 30  # Segundos a mantener en buffer
FPS = 10  # Estimado de frames por segundo
MAX_FRAMES = BUFFER_SECONDS * FPS

lock = threading.Lock()


def stream_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = base64.b64encode(buffer).decode('utf-8')

        with lock:
            timestamp = time.time()
            frame_buffer.append((timestamp, frame_bytes))
            if len(frame_buffer) > MAX_FRAMES:
                frame_buffer.pop(0)

        socketio.emit('image', {'image': frame_bytes})
        time.sleep(1 / FPS)


@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado")


@socketio.on('rewind')
def handle_rewind(data):
    seconds = data.get('seconds', 5)
    now = time.time()
    frames_to_send = []

    with lock:
        for ts, frame in reversed(frame_buffer):
            if now - ts <= seconds:
                frames_to_send.insert(0, frame)
            else:
                break

    for frame in frames_to_send:
        socketio.emit('image', {'image': frame})
        time.sleep(1 / FPS)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    t = threading.Thread(target=stream_frames)
    t.daemon = True
    t.start()

    socketio.run(app, host='0.0.0.0', port=5000)
