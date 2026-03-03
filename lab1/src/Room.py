"""Комната в умном доме"""

import uuid
from exceptions import DeviceNotFoundError

class Room:
    """Комната в умном доме"""

    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.devices = {}

    def add_device(self, device) -> None:
        self.devices[device.id] = device

    def remove_device(self, device_id: str) -> None:
        if device_id not in self.devices:
            raise DeviceNotFoundError(f"Устройство {device_id} не найдено")
        del self.devices[device_id]

    def get_device(self, device_id: str):
        if device_id not in self.devices:
            raise DeviceNotFoundError(f"Устройство {device_id} не найдено")
        return self.devices[device_id]

    def get_devices_by_type(self, device_type: str) -> list:
        return [d for d in self.devices.values() if d.get_device_type() == device_type]