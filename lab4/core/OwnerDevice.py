"""Мобильное устройство хозяина умного дома"""
import uuid
from datetime import datetime
from .SmartDevice import SmartDevice


class OwnerDevice(SmartDevice):
    """Мобильное устройство для управления умным домом"""

    def __init__(self, name: str = "Мобильное устройство хозяина"):
        # Передаем room_id = "owner" так как устройство хозяина не в комнате
        super().__init__(name, "owner")
        self.connected = True
        self.last_access = None

    def get_device_type(self) -> str:
        return "мобильное устройство"

    def connect(self):
        """Подключение к системе"""
        self.connected = True
        self.status = True
        self.last_access = datetime.now()
        print(f"{self.name} подключен к системе")

    def disconnect(self):
        """Отключение от системы"""
        self.connected = False
        self.status = False
        print(f"{self.name} отключен от системы")

    def get_status(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.get_device_type(),
            'connected': 'да' if self.connected else 'нет',
            'status': 'активно' if self.connected else 'отключено',
            'last_access': self.last_access.strftime('%Y-%m-%d %H:%M:%S') if self.last_access else 'никогда'
        }

    def send_notification(self, message: str):
        """Отправка уведомления на устройство"""
        if self.connected:
            print(f"Уведомление на {self.name}: {message}")
            self.last_access = datetime.now()
        else:
            print(f"Устройство {self.name} отключено, уведомление не доставлено")