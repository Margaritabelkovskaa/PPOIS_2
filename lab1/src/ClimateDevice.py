"""
Класс устройства климат-контроля (кондиционер, климат-система)
Управление температурой и влажностью
"""

from SmartDevice import SmartDevice
from exceptions import InvalidValueError


class ClimateDevice(SmartDevice):
    """
    Устройство климат-контроля с контролем температуры и влажности.

    Attributes:
        temperature (float): Текущая температура
        target_temperature (float): Целевая температура
        humidity (float): Текущая влажность
        target_humidity (float): Целевая влажность
        mode (str): Режим работы (auto, cool, heat, dry, fan_only)
        fan_speed (str): Скорость вентилятора (auto, low, medium, high)
    """

    def __init__(self, name: str, room_id: str):
        """
        Инициализация климат-устройства с параметрами по умолчанию.

        Args:
            name: Название устройства
            room_id: ID комнаты
        """
        super().__init__(name, room_id)

        # Температура: текущая и целевая
        self.temperature = 22.0  # Комфортная температура
        self.target_temperature = 22.0

        # Влажность: текущая и целевая
        self.humidity = 50.0  # Комфортная влажность
        self.target_humidity = 50.0

        # Режимы работы
        self.mode = "auto"  # auto, cool, heat, dry, fan_only
        self.fan_speed = "auto"  # auto, low, medium, high

    def get_device_type(self) -> str:
        """Возвращает тип устройства."""
        return "климат"

    # ========== УПРАВЛЕНИЕ ТЕМПЕРАТУРОЙ ==========

    def set_temperature(self, temp: float) -> None:
        """
        Установить целевую температуру с валидацией.

        Args:
            temp: Желаемая температура (16-30°C)

        Raises:
            InvalidValueError: Если температура вне допустимого диапазона
        """
        if not 16 <= temp <= 30:
            raise InvalidValueError("Температура должна быть от 16 до 30°C")
        self.target_temperature = temp
        print(f"Температура {self.name} установлена на {temp}°C")

    def set_temperature_range(self, min_temp: float, max_temp: float) -> None:
        """
        Установить диапазон температуры для автоматического режима.

        Args:
            min_temp: Минимальная температура (16-30°C)
            max_temp: Максимальная температура (16-30°C)

        Raises:
            InvalidValueError: При некорректных значениях
        """
        # Проверка границ
        if not 16 <= min_temp <= 30 or not 16 <= max_temp <= 30:
            raise InvalidValueError("Температура должна быть от 16 до 30°C")

        # Проверка логики (мин не может быть больше макс)
        if min_temp > max_temp:
            raise InvalidValueError("Минимальная температура не может быть больше максимальной")

        # Сохраняем диапазон
        self.min_temperature = min_temp
        self.max_temperature = max_temp
        print(f"Диапазон температуры установлен: {min_temp}°C - {max_temp}°C")

    # ========== УПРАВЛЕНИЕ ВЛАЖНОСТЬЮ ==========

    def set_humidity(self, humidity: float) -> None:
        """
        Установить целевую влажность с валидацией.

        Args:
            humidity: Желаемая влажность (30-80%)

        Raises:
            InvalidValueError: Если влажность вне допустимого диапазона
        """
        if not 30 <= humidity <= 80:
            raise InvalidValueError("Влажность должна быть от 30 до 80%")
        self.target_humidity = humidity
        print(f"Влажность {self.name} установлена на {humidity}%")

    def set_humidity_range(self, min_humidity: float, max_humidity: float) -> None:
        """
        Установить диапазон влажности для автоматического режима.

        Args:
            min_humidity: Минимальная влажность (30-80%)
            max_humidity: Максимальная влажность (30-80%)

        Raises:
            InvalidValueError: При некорректных значениях
        """
        # Проверка границ
        if not 30 <= min_humidity <= 80 or not 30 <= max_humidity <= 80:
            raise InvalidValueError("Влажность должна быть от 30 до 80%")

        # Проверка логики
        if min_humidity > max_humidity:
            raise InvalidValueError("Минимальная влажность не может быть больше максимальной")

        # Сохраняем диапазон
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        print(f"Диапазон влажности установлен: {min_humidity}% - {max_humidity}%")

    def increase_humidity(self) -> None:
        """
        Увеличить текущую влажность на 5% (включить увлажнитель).
        Не может превысить 80%.
        """
        if self.humidity < 80:
            self.humidity = min(80, self.humidity + 5)
            print(f"Влажность увеличена до {self.humidity}%")
        else:
            print("Влажность уже максимальная")

    def decrease_humidity(self) -> None:
        """
        Уменьшить текущую влажность на 5% (включить осушитель).
        Не может стать меньше 30%.
        """
        if self.humidity > 30:
            self.humidity = max(30, self.humidity - 5)
            print(f"Влажность уменьшена до {self.humidity}%")
        else:
            print("Влажность уже минимальная")

    # ========== УПРАВЛЕНИЕ РЕЖИМАМИ ==========

    def set_mode(self, mode: str) -> None:
        """
        Установить режим работы с валидацией.

        Args:
            mode: Режим (auto, cool, heat, dry, fan_only)

        Raises:
            InvalidValueError: Если режим не поддерживается
        """
        valid_modes = ["auto", "cool", "heat", "dry", "fan_only"]
        if mode not in valid_modes:
            raise InvalidValueError(f"Режим должен быть одним из: {', '.join(valid_modes)}")
        self.mode = mode
        print(f"Режим {self.name} установлен: {mode}")

    def set_fan_speed(self, speed: str) -> None:
        """
        Установить скорость вентилятора с валидацией.

        Args:
            speed: Скорость (auto, low, medium, high)

        Raises:
            InvalidValueError: Если скорость не поддерживается
        """
        valid_speeds = ["auto", "low", "medium", "high"]
        if speed not in valid_speeds:
            raise InvalidValueError(f"Скорость вентилятора должна быть одной из: {', '.join(valid_speeds)}")
        self.fan_speed = speed
        print(f"Скорость вентилятора {self.name} установлена: {speed}")

    # ========== АВТОМАТИЧЕСКОЕ УПРАВЛЕНИЕ ==========

    def auto_adjust(self) -> None:
        """
        Автоматическая подстройка под целевые параметры.
        Вызывается периодически для плавного изменения температуры и влажности.
        Работает только если устройство включено.
        """
        if not self.status:  # Если устройство выключено - ничего не делаем
            return

        changes = []  # Список изменений для вывода

        # Регулировка температуры
        if self.temperature < self.target_temperature - 1:
            # Если текущая температура сильно ниже целевой - повышаем
            self.temperature += 0.5
            changes.append(f"температура +0.5°C")
        elif self.temperature > self.target_temperature + 1:
            # Если текущая температура сильно выше целевой - понижаем
            self.temperature -= 0.5
            changes.append(f"температура -0.5°C")

        # Регулировка влажности
        if self.humidity < self.target_humidity - 3:
            # Если влажность ниже целевой - повышаем
            self.humidity = min(self.target_humidity, self.humidity + 2)
            changes.append(f"влажность +2%")
        elif self.humidity > self.target_humidity + 3:
            # Если влажность выше целевой - понижаем
            self.humidity = max(self.target_humidity, self.humidity - 2)
            changes.append(f"влажность -2%")

        # Выводим информацию об изменениях
        if changes:
            print(f"{self.name}: " + ", ".join(changes))

    # ========== ПОЛУЧЕНИЕ СТАТУСА ==========

    def get_status(self) -> dict:
        """
        Расширенный метод получения статуса.
        Добавляет все параметры климат-контроля.

        Returns:
            dict: Полный статус устройства
        """
        status = super().get_status()  # Базовый статус (id, name, и т.д.)

        # Добавляем параметры климат-контроля
        status.update({
            'temperature': round(self.temperature, 1),
            'target_temperature': round(self.target_temperature, 1),
            'humidity': round(self.humidity, 1),
            'target_humidity': round(self.target_humidity, 1),
            'mode': self.mode,
            'fan_speed': self.fan_speed
        })

        # Добавляем диапазоны, если они были установлены
        if hasattr(self, 'min_temperature'):
            status['min_temperature'] = self.min_temperature
            status['max_temperature'] = self.max_temperature
        if hasattr(self, 'min_humidity'):
            status['min_humidity'] = self.min_humidity
            status['max_humidity'] = self.max_humidity

        return status