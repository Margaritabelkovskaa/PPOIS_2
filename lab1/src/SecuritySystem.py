"""
Класс системы безопасности (сигнализация для всего дома)
"""

from SmartDevice import SmartDevice


class SecuritySystem(SmartDevice):
    """
    Система безопасности для всего дома.

    Attributes:
        armed (bool): Находится ли на охране
        alarm_triggered (bool): Сработала ли тревога
    """

    def __init__(self, name: str):
        """
        Инициализация системы безопасности.

        Args:
            name: Название системы
        """
        # Сигнализация всегда находится в доме, а не в конкретной комнате
        super().__init__(name, "house")
        self.armed = False  # Не на охране
        self.alarm_triggered = False  # Тревога не сработала

    def get_device_type(self) -> str:
        """Возвращает тип устройства."""
        return "безопасность"

    def arm(self) -> None:
        """Поставить систему на охрану."""
        self.armed = True
        print(f"Сигнализация {self.name} поставлена на охрану")

    def disarm(self) -> None:
        """Снять систему с охраны (сбрасывает тревогу)."""
        self.armed = False
        self.alarm_triggered = False
        print(f"Сигнализация {self.name} снята с охраны")

    def trigger_alarm(self) -> None:
        """
        Запустить тревогу.
        Срабатывает только если система на охране.
        """
        if self.armed:  # Только если на охране
            self.alarm_triggered = True
            print(f"ТРЕВОГА! Сработала сигнализация {self.name}!")

    def get_status(self) -> dict:
        """
        Расширенный метод получения статуса.

        Returns:
            dict: Статус с информацией о состоянии охраны
        """
        status = super().get_status()
        status['armed'] = 'да' if self.armed else 'нет'
        status['alarm_triggered'] = 'да' if self.alarm_triggered else 'нет'
        return status