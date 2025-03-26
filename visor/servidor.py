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

BUFFER_SIZE = 10000
image_buffer = deque(maxlen=BUFFER_SIZE)
latest_image = None  # Última imagen en vivo

@app.route('/')
def index():
    global image_buffer
    image_buffer = deque(maxlen=BUFFER_SIZE)  # Reiniciar buffer al volver
    return render_template('index.html')

@app.route('/segundo_visores')
def segundo_visores():
    return render_template('segundo_visores.html')

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
    