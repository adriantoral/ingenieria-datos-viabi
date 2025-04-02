import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import base64
from collections import deque
import os

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

@app.route('/tercer_visores')
def tercer_visores():
    frames_folder = os.path.join(os.getcwd(), 'Frames')
    print("Directorio Frames encontrado en:", frames_folder)  # Depuración
    print("Contenido del directorio Frames:", os.listdir(frames_folder))  # Depuración

    images = []
    for filename in os.listdir(frames_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(filename)
    
    images.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    images_urls = [url_for('get_frame', filename=img) for img in images]

    print("URLs generadas:", images_urls)  # Depuración
    return render_template('tercer_visores.html', images=images_urls)

@app.route('/frames/<path:filename>')
def get_frame(filename):
    # Envía el archivo desde la carpeta "frames"
    return send_from_directory("Frames", filename)

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
    