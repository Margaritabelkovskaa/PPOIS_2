import uuid
from abc import ABC, abstractmethod
from exceptions import InvalidValueError


# ==================== БАЗОВЫЙ КЛАСС ====================

class SmartDevice(ABC):
    """Абстрактный базовый класс для всех умных устройств"""

    def __init__(self, name: str, room_id: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.room_id = room_id
        self.status = False

    @abstractmethod
    def get_device_type(self) -> str:
        """Возвращает тип устройства"""
        pass

    def turn_on(self) -> None:
        """Включить устройство"""
        self.status = True

    def turn_off(self) -> None:
        """Выключить устройство"""
        self.status = False

    def get_status(self) -> dict:
        """Получить статус устройства"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.get_device_type(),
            'status': 'включено' if self.status else 'выключено',
            'room_id': self.room_id
        }


# ==================== ОСВЕЩЕНИЕ ====================

class LightDevice(SmartDevice):
    """Устройство освещения"""

    def __init__(self, name: str, room_id: str):
        super().__init__(name, room_id)
        self.brightness = 100

    def get_device_type(self) -> str:
        return "освещение"

    def set_brightness(self, level: int) -> None:
        """Установить яркость (0-100)"""
        if not 0 <= level <= 100:
            raise InvalidValueError("Яркость должна быть от 0 до 100")
        self.brightness = level
        print(f"Яркость {self.name} установлена на {level}%")

    def get_status(self) -> dict:
        status = super().get_status()
        status['brightness'] = self.brightness
        return status


# ==================== КЛИМАТ (с контролем влажности) ====================

class ClimateDevice(SmartDevice):
    """Устройство климат-контроля с контролем температуры и влажности"""

    def __init__(self, name: str, room_id: str):
        super().__init__(name, room_id)
        self.temperature = 22.0
        self.target_temperature = 22.0
        self.humidity = 50.0
        self.target_humidity = 50.0
        self.mode = "auto"  # auto, cool, heat, dry, fan_only
        self.fan_speed = "auto"  # auto, low, medium, high

    def get_device_type(self) -> str:
        return "климат"

    # ===== МЕТОДЫ УПРАВЛЕНИЯ ТЕМПЕРАТУРОЙ =====

    def set_temperature(self, temp: float) -> None:
        """Установить целевую температуру (16-30°C)"""
        if not 16 <= temp <= 30:
            raise InvalidValueError("Температура должна быть от 16 до 30°C")
        self.target_temperature = temp
        print(f"Температура {self.name} установлена на {temp}°C")

    def set_temperature_range(self, min_temp: float, max_temp: float) -> None:
        """Установить диапазон температуры (для автоматического режима)"""
        if not 16 <= min_temp <= 30 or not 16 <= max_temp <= 30:
            raise InvalidValueError("Температура должна быть от 16 до 30°C")
        if min_temp > max_temp:
            raise InvalidValueError("Минимальная температура не может быть больше максимальной")
        self.min_temperature = min_temp
        self.max_temperature = max_temp
        print(f"Диапазон температуры установлен: {min_temp}°C - {max_temp}°C")

    # ===== МЕТОДЫ УПРАВЛЕНИЯ ВЛАЖНОСТЬЮ =====

    def set_humidity(self, humidity: float) -> None:
        """Установить целевую влажность (30-80%)"""
        if not 30 <= humidity <= 80:
            raise InvalidValueError("Влажность должна быть от 30 до 80%")
        self.target_humidity = humidity
        print(f"Влажность {self.name} установлена на {humidity}%")

    def set_humidity_range(self, min_humidity: float, max_humidity: float) -> None:
        """Установить диапазон влажности (для автоматического режима)"""
        if not 30 <= min_humidity <= 80 or not 30 <= max_humidity <= 80:
            raise InvalidValueError("Влажность должна быть от 30 до 80%")
        if min_humidity > max_humidity:
            raise InvalidValueError("Минимальная влажность не может быть больше максимальной")
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        print(f"Диапазон влажности установлен: {min_humidity}% - {max_humidity}%")

    def increase_humidity(self) -> None:
        """Увеличить влажность (включить увлажнитель)"""
        if self.humidity < 80:
            self.humidity = min(80, self.humidity + 5)
            print(f"Влажность увеличена до {self.humidity}%")
        else:
            print("Влажность уже максимальная")

    def decrease_humidity(self) -> None:
        """Уменьшить влажность (включить осушитель)"""
        if self.humidity > 30:
            self.humidity = max(30, self.humidity - 5)
            print(f"Влажность уменьшена до {self.humidity}%")
        else:
            print("Влажность уже минимальная")

    # ===== МЕТОДЫ УПРАВЛЕНИЯ РЕЖИМАМИ =====

    def set_mode(self, mode: str) -> None:
        """Установить режим работы: auto, cool, heat, dry, fan_only"""
        valid_modes = ["auto", "cool", "heat", "dry", "fan_only"]
        if mode not in valid_modes:
            raise InvalidValueError(f"Режим должен быть одним из: {', '.join(valid_modes)}")
        self.mode = mode
        print(f"Режим {self.name} установлен: {mode}")

    def set_fan_speed(self, speed: str) -> None:
        """Установить скорость вентилятора: auto, low, medium, high"""
        valid_speeds = ["auto", "low", "medium", "high"]
        if speed not in valid_speeds:
            raise InvalidValueError(f"Скорость вентилятора должна быть одной из: {', '.join(valid_speeds)}")
        self.fan_speed = speed
        print(f"Скорость вентилятора {self.name} установлена: {speed}")

    # ===== АВТОМАТИЧЕСКОЕ УПРАВЛЕНИЕ =====

    def auto_adjust(self) -> None:
        """Автоматическая подстройка под целевые параметры"""
        if not self.status:
            return

        changes = []

        # Регулировка температуры
        if self.temperature < self.target_temperature - 1:
            self.temperature += 0.5
            changes.append(f"температура +0.5°C")
        elif self.temperature > self.target_temperature + 1:
            self.temperature -= 0.5
            changes.append(f"температура -0.5°C")

        # Регулировка влажности
        if self.humidity < self.target_humidity - 3:
            self.humidity = min(self.target_humidity, self.humidity + 2)
            changes.append(f"влажность +2%")
        elif self.humidity > self.target_humidity + 3:
            self.humidity = max(self.target_humidity, self.humidity - 2)
            changes.append(f"влажность -2%")

        if changes:
            print(f"{self.name}: " + ", ".join(changes))

    # ===== ПОЛУЧЕНИЕ СТАТУСА =====

    def get_status(self) -> dict:
        """Получить полный статус устройства"""
        status = super().get_status()
        status.update({
            'temperature': round(self.temperature, 1),
            'target_temperature': round(self.target_temperature, 1),
            'humidity': round(self.humidity, 1),
            'target_humidity': round(self.target_humidity, 1),
            'mode': self.mode,
            'fan_speed': self.fan_speed
        })

        # Добавляем диапазоны если они есть
        if hasattr(self, 'min_temperature'):
            status['min_temperature'] = self.min_temperature
            status['max_temperature'] = self.max_temperature
        if hasattr(self, 'min_humidity'):
            status['min_humidity'] = self.min_humidity
            status['max_humidity'] = self.max_humidity

        return status


# ==================== СИГНАЛИЗАЦИЯ ====================

class SecuritySystem(SmartDevice):
    """Система безопасности для всего дома"""

    def __init__(self, name: str):
        super().__init__(name, "house")
        self.armed = False
        self.alarm_triggered = False

    def get_device_type(self) -> str:
        return "безопасность"

    def arm(self) -> None:
        """Поставить на охрану"""
        self.armed = True
        print(f"Сигнализация {self.name} поставлена на охрану")

    def disarm(self) -> None:
        """Снять с охраны"""
        self.armed = False
        self.alarm_triggered = False
        print(f"Сигнализация {self.name} снята с охраны")

    def trigger_alarm(self) -> None:
        """Запустить тревогу (только если на охране)"""
        if self.armed:
            self.alarm_triggered = True
            print(f"ТРЕВОГА! Сработала сигнализация {self.name}!")

    def get_status(self) -> dict:
        status = super().get_status()
        status['armed'] = 'да' if self.armed else 'нет'
        status['alarm_triggered'] = 'да' if self.alarm_triggered else 'нет'
        return status


# ==================== ПЫЛЕСОС ====================

class SmartCleaner(SmartDevice):
    """Умный пылесос"""

    def __init__(self, name: str, room_id: str):
        super().__init__(name, room_id)
        self.mode = "обычный"  # обычный, влажная

    def get_device_type(self) -> str:
        return "пылесос"

    def clean(self):
        """Запуск уборки"""
        self.status = True

        if self.mode == "влажная":
            print(f"{self.name} начал влажную уборку")
        else:
            print(f"{self.name} начал обычную уборку")

    def stop(self):
        """Остановка уборки"""
        self.status = False
        print(f"{self.name} остановлен")

    def set_mode(self, mode: str):
        """Установка режима уборки"""
        if mode in ["обычный", "влажная"]:
            self.mode = mode
            if mode == "влажная":
                print(f"Режим установлен: влажная уборка")
            else:
                print(f"Режим установлен: обычная уборка")
        else:
            print("Ошибка: доступные режимы: обычный, влажная")

    def get_status(self) -> dict:
        status = super().get_status()
        status['mode'] = "влажная уборка" if self.mode == "влажная" else "обычная уборка"
        return status


# ==================== ЧАЙНИК ====================

class SmartKettle(SmartDevice):
    """Умный чайник"""

    def __init__(self, name: str, room_id: str):
        super().__init__(name, room_id)
        self.water_level = 100
        self.temperature = 20
        self.boiling = False

    def get_device_type(self) -> str:
        return "чайник"

    def boil(self):
        """Вскипятить воду"""
        if self.water_level < 10:
            print("Ошибка: нет воды!")
            return

        self.boiling = True
        self.status = True
        print(f"{self.name} кипятит...")
        self.temperature = 100
        self.boiling = False
        print(f"Вода вскипела!")

    def set_temperature(self, temp: int):
        """Нагреть воду до температуры (40-100°C)"""
        if temp < 40 or temp > 100:
            print("Ошибка: температура должна быть от 40 до 100°C")
            return
        self.temperature = temp
        self.status = True
        print(f"Вода нагрета до {temp}°C")
        self.status = False

    def get_status(self) -> dict:
        status = super().get_status()
        status['water'] = f"{self.water_level}%"
        status['temperature'] = f"{self.temperature}°C"
        return status