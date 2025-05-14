import socket
import cv2
import numpy as np
import struct

# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5000))  # Conectar al servidor local en el puerto 5000

while True:
    try:
        # Primero, recibir la longitud de los datos
        data_length = struct.unpack("!Q", client_socket.recv(8))[0]

        # Recibir los datos del frame
        frame_data = b""
        while len(frame_data) < data_length:
            frame_data += client_socket.recv(data_length - len(frame_data))

        # Decodificar el frame
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)

        # Mostrar el frame
        cv2.imshow("Visor de Cámara", frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except (ConnectionResetError, BrokenPipeError):
        print("El servidor se ha desconectado.")
        break

client_socket.close()
cv2.destroyAllWindows()
