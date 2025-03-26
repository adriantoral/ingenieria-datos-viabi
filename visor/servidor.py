from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import eventlet

eventlet.monkey_patch()  # Permite que SocketIO funcione con Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/segundo_visores')
def segundo_visores():
    return render_template('segundo_visores.html')

@socketio.on('start_stream')
def start_stream():
    # Cambiamos a la cámara IVCam, generalmente es "1" en lugar de "0".
    cap = cv2.VideoCapture(1)  # Cambia el número si no funciona, prueba con 0, 1, 2, etc.

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        emit('image', {'image': frame_base64})

        socketio.sleep(0.05)  # Para evitar saturar la red

    cap.release()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
