"""
Класс умного пылесоса
"""

from SmartDevice import SmartDevice


class SmartCleaner(SmartDevice):
    """
    Умный пылесос с разными режимами уборки.

    Attributes:
        mode (str): Режим уборки ("обычный", "влажная")
    """

    def __init__(self, name: str, room_id: str):
        """
        Инициализация пылесоса.

        Args:
            name: Название пылесоса
            room_id: ID комнаты
        """
        super().__init__(name, room_id)
        self.mode = "обычный"  # По умолчанию обычная уборка

    def get_device_type(self) -> str:
        """Возвращает тип устройства."""
        return "пылесос"

    def clean(self) -> None:
        """
        Запуск уборки.
        Включает устройство и сообщает о начале уборки.
        """
        self.status = True  # Включаем пылесос

        if self.mode == "влажная":
            print(f"{self.name} начал влажную уборку")
        else:
            print(f"{self.name} начал обычную уборку")

    def stop(self) -> None:
        """Остановка уборки."""
        self.status = False
        print(f"{self.name} остановлен")

    def set_mode(self, mode: str) -> None:
        """
        Установка режима уборки с валидацией.

        Args:
            mode: Режим ("обычный" или "влажная")
        """
        if mode in ["обычный", "влажная"]:
            self.mode = mode
            print(f"Режим установлен: {'влажная уборка' if mode == 'влажная' else 'обычная уборка'}")
        else:
            print("Ошибка: доступные режимы: обычный, влажная")
            # Здесь можно было бы выбросить исключение, но автор выбрал просто вывод ошибки

    def get_status(self) -> dict:
        """
        Расширенный метод получения статуса.

        Returns:
            dict: Статус с информацией о режиме уборки
        """
        status = super().get_status()
        status['mode'] = "влажная уборка" if self.mode == "влажная" else "обычная уборка"
        return status