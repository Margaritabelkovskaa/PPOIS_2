"""
Абстрактный базовый класс для всех умных устройств
Определяет общий интерфейс и базовую функциональность
"""

import uuid
from abc import ABC, abstractmethod


class SmartDevice(ABC):
    """
    Абстрактный базовый класс для всех умных устройств.

    Attributes:
        id (str): Уникальный идентификатор устройства (генерируется автоматически)
        name (str): Название устройства, задается пользователем
        room_id (str): ID комнаты, где находится устройство
        status (bool): Состояние устройства (включено/выключено)
    """

    def __init__(self, name: str, room_id: str):
        """
        Инициализация базового устройства.

        Args:
            name: Название устройства
            room_id: ID комнаты размещения
        """
        self.id = str(uuid.uuid4())  # Генерируем уникальный ID
        self.name = name
        self.room_id = room_id
        self.status = False  # По умолчанию устройство выключено

    @abstractmethod
    def get_device_type(self) -> str:
        """
        Абстрактный метод - должен быть реализован в каждом дочернем классе.
        Возвращает строку с типом устройства для идентификации.

        Returns:
            str: Тип устройства (например, "освещение", "климат")
        """
        pass

    def turn_on(self) -> None:
        """Включить устройство. Изменяет статус на True."""
        self.status = True

    def turn_off(self) -> None:
        """Выключить устройство. Изменяет статус на False."""
        self.status = False

    def get_status(self) -> dict:
        """
        Получить базовый статус устройства.
        Дочерние классы могут расширять этот метод, добавляя свои параметры.

        Returns:
            dict: Словарь с основными параметрами устройства
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.get_device_type(),
            'status': 'включено' if self.status else 'выключено',
            'room_id': self.room_id
        }