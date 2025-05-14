import cv2
import base64
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

# Inicializar Flask y SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Capturar video desde la cámara
cap = cv2.VideoCapture(0)

# Función para capturar frames
def capture_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Codificar el frame en JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_base64 = base64.b64encode(buffer).decode('utf-8')

        # Emitir el frame codificado a través de WebSocket
        socketio.emit('video_frame', {'data': jpg_as_base64})
        print("Frame enviado...")  # Agregar mensaje de depuración
        time.sleep(0.03)  # Para no sobrecargar el servidor (aproximadamente 30 fps)

# Ruta principal que sirve el HTML
@app.route('/')
def index():
    return render_template('index.html')

# Iniciar el servidor Flask en un hilo separado para no bloquear la captura de video
def start_server():
    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Ejecutar la captura de video en un hilo separado
    video_thread = threading.Thread(target=capture_frames)
    video_thread.daemon = True
    video_thread.start()

    # Iniciar el servidor Flask
    start_server()
