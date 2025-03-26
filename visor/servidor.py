from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import eventlet
from collections import deque
from datetime import datetime

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

BUFFER_SIZE = 1000
image_buffer = deque(maxlen=BUFFER_SIZE)  # Para almacenar imágenes
time_buffer = deque(maxlen=BUFFER_SIZE)   # Para almacenar las horas

latest_image = None  # Última imagen en vivo
latest_time = None   # Última hora de la imagen en vivo

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

        # Codificar la imagen a base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Obtener la hora actual
        current_time = datetime.now().strftime("%H:%M:%S")

        latest_image = frame_base64  # Guardar la última imagen en vivo
        latest_time = current_time   # Guardar la última hora

        if len(image_buffer) == BUFFER_SIZE:
            image_buffer.popleft()  # Eliminar la imagen más antigua cuando el buffer se llena
            time_buffer.popleft()   # Eliminar la hora más antigua

        # Añadir la imagen y la hora al buffer
        image_buffer.append(frame_base64)
        time_buffer.append(current_time)

        # Emitir la imagen y la hora al cliente en vivo
        emit('image', {'image': frame_base64, 'time': current_time}, broadcast=True)
        socketio.sleep(0.05)  # ~20 FPS

    cap.release()

@socketio.on('get_buffered_image')
def get_buffered_image(data):
    """
    Envía la imagen más reciente o una imagen del buffer con la hora.
    """
    index = int(data.get('index', -1))

    if index == -1:  # Solicitud de la última imagen en vivo
        if latest_image:
            emit('buffered_image', {'image': latest_image, 'time': latest_time})
        else:
            emit('buffered_image', {'error': 'No hay imágenes aún'})
    elif 0 <= index < len(image_buffer):  # Asegurarse de que el índice esté dentro del buffer
        emit('buffered_image', {'image': image_buffer[index], 'time': time_buffer[index]})
    else:
        emit('buffered_image', {'error': 'Índice fuera de rango'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
