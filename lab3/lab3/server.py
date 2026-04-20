import socket
import pickle
import threading


class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = []  # [(socket, color), ...]
        self.colors = ['white', 'black']
        self.waiting_for_connection = True
        print(f"Сервер запущен на {host}:{port}")
        print("Ожидание подключения игроков...")

    def broadcast_to_other(self, data, sender_socket):
        """Отправляет данные другому игроку (не отправителю)"""
        for client_socket, color in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(pickle.dumps(data))
                    print(f"Пересылаю ход игроку {color}")
                except:
                    pass

    def handle_client(self, client_socket, color):
        """Обрабатывает одного клиента"""
        print(f"Игрок {color} подключился")

        # Отправляем клиенту его цвет
        client_socket.send(pickle.dumps({'type': 'init', 'color': color}))

        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                move_data = pickle.loads(data)
                print(f"Получен ход от {color}: {move_data}")
                # Пересылаем другому игроку
                self.broadcast_to_other(move_data, client_socket)
            except:
                break

        print(f"Игрок {color} отключился")
        # Удаляем клиента из списка
        for i, (sock, col) in enumerate(self.clients):
            if sock == client_socket:
                self.clients.pop(i)
                break
        client_socket.close()

    def start(self):
        """Запускает сервер"""
        # Принимаем двух игроков
        for i in range(2):
            client_socket, addr = self.server.accept()
            color = self.colors[i]
            self.clients.append((client_socket, color))
            thread = threading.Thread(target=self.handle_client, args=(client_socket, color))
            thread.daemon = True
            thread.start()
            print(f"Игрок {color} подключился с адреса {addr}")

        print("Оба игрока подключены! Игра начинается!")
        print("Белые ходят первыми!")

        # Ждём завершения
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Сервер остановлен")
            self.server.close()


if __name__ == "__main__":
    server = GameServer()
    server.start()