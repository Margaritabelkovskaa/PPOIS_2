"""
Класс устройства освещения (лампочки, светильники)
"""

from SmartDevice import SmartDevice
from exceptions import InvalidValueError


class LightDevice(SmartDevice):
    """
    Устройство освещения с регулировкой яркости.

    Attributes:
        brightness (int): Текущая яркость (0-100%)
    """

    def __init__(self, name: str, room_id: str):
        """
        Инициализация лампочки.

        Args:
            name: Название лампочки
            room_id: ID комнаты
        """
        super().__init__(name, room_id)  # Вызов конструктора родителя
        self.brightness = 100  # По умолчанию максимальная яркость

    def get_device_type(self) -> str:
        """
        Реализация абстрактного метода родителя.

        Returns:
            str: Тип устройства - "освещение"
        """
        return "освещение"

    def set_brightness(self, level: int) -> None:
        """
        Установить яркость с проверкой допустимых значений.

        Args:
            level: Уровень яркости (0-100)

        Raises:
            InvalidValueError: Если значение вне диапазона 0-100
        """
        if not 0 <= level <= 100:
            raise InvalidValueError("Яркость должна быть от 0 до 100")
        self.brightness = level
        print(f"Яркость {self.name} установлена на {level}%")

    def get_status(self) -> dict:
        """
        Расширяет родительский метод, добавляя информацию о яркости.

        Returns:
            dict: Статус устройства с яркостью
        """
        status = super().get_status()  # Получаем базовый статус
        status['brightness'] = self.brightness  # Добавляем яркость
        return status