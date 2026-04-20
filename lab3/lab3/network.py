import socket
import pickle
import threading


class Network:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.connected = False
        self.player_color = None

    def connect(self):
        """Подключение к серверу"""
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            # Получаем цвет игрока от сервера
            data = self.receive()
            if data and data.get('type') == 'init':
                self.player_color = data.get('color')
                print(f"Подключен к серверу! Твой цвет: {self.player_color}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def send(self, data):
        """Отправка данных"""
        try:
            self.client.send(pickle.dumps(data))
            return True
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return False

    def receive(self):
        """Получение данных"""
        try:
            data = self.client.recv(4096)
            return pickle.loads(data)
        except Exception as e:
            print(f"Ошибка получения: {e}")
            return None

    def close(self):
        """Закрытие соединения"""
        self.client.close()