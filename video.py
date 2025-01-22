import cv2
import socket
import struct

server_ip = '192.168.1.112'
server_port = 12345

# Открываем захват с камеры
cap = cv2.VideoCapture(0)

# Настройка сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Server listening on {server_ip}:{server_port}")

while True:
    try:
        # Ожидаем подключения клиента
        client_socket, _ = server_socket.accept()
        print("Client connected")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            # Кодируем кадр в формат JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()

            # Отправляем длину данных (4 байта)
            length = len(data)
            client_socket.send(struct.pack('I', length))

            # Отправляем данные кадра
            client_socket.send(data)

    except (socket.error, cv2.error) as e:
        print(f"Connection error or video capture error: {e}")
        if client_socket:
            client_socket.close()
        print("Waiting for new client connection...")

cap.release()
server_socket.close()
