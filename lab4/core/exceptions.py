"""Исключения умного дома"""

class SmartHomeError(Exception):
    """Базовое исключение"""
    pass

class DeviceNotFoundError(SmartHomeError):
    """Устройство не найдено"""
    pass

class RoomNotFoundError(SmartHomeError):
    """Комната не найдена"""
    pass

class InvalidValueError(SmartHomeError):
    """Некорректное значение"""
    pass