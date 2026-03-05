"""
Класс умного чайника
"""

from SmartDevice import SmartDevice


class SmartKettle(SmartDevice):
    """
    Умный чайник с контролем температуры и уровня воды.

    Attributes:
        water_level (int): Уровень воды в процентах (0-100)
        temperature (int): Текущая температура воды
        boiling (bool): Идет ли процесс кипячения
    """

    def __init__(self, name: str, room_id: str):
        """
        Инициализация чайника.

        Args:
            name: Название чайника
            room_id: ID комнаты
        """
        super().__init__(name, room_id)
        self.water_level = 100  # Полный чайник
        self.temperature = 20  # Комнатная температура
        self.boiling = False  # Не кипятит

    def get_device_type(self) -> str:
        """Возвращает тип устройства."""
        return "чайник"

    def boil(self) -> None:
        """
        Вскипятить воду.
        Проверяет наличие воды и имитирует процесс кипячения.
        """
        if self.water_level < 10:
            print("Ошибка: нет воды!")
            return

        self.boiling = True
        self.status = True
        print(f"{self.name} кипятит...")

        # Имитация кипячения
        self.temperature = 100
        self.boiling = False

        print(f"Вода вскипела!")

    def set_temperature(self, temp: int) -> None:
        """
        Нагреть воду до заданной температуры.

        Args:
            temp: Желаемая температура (40-100°C)
        """
        if temp < 40 or temp > 100:
            print("Ошибка: температура должна быть от 40 до 100°C")
            return

        self.temperature = temp
        self.status = True
        print(f"Вода нагрета до {temp}°C")
        self.status = False  # Автоматически выключается после нагрева

    def get_status(self) -> dict:
        """
        Расширенный метод получения статуса.

        Returns:
            dict: Статус с информацией о воде и температуре
        """
        status = super().get_status()
        status['water'] = f"{self.water_level}%"
        status['temperature'] = f"{self.temperature}°C"
        return status