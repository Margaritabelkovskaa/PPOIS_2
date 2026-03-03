"""Основной класс умного дома"""

from exceptions import RoomNotFoundError, DeviceNotFoundError, SmartHomeError
from Room import Room

class SmartHome:
    """Основной класс умного дома"""

    def __init__(self, name: str):
        self.name = name
        # Фиксированные комнаты
        self.rooms = {}
        self._init_default_rooms()
        self.security_system = None
        self.automation_rules = {}
        self.owner_device = None

    def _init_default_rooms(self):
        """Инициализация фиксированных комнат"""
        print("Создаю фиксированные комнаты...")
        default_rooms = ["детская", "ванная", "спальня", "кухня", "гостиная", "коридор"]

        for room_name in default_rooms:
            room = Room(room_name)
            self.rooms[room.id] = room
            print(f"  Комната '{room_name}' создана (ID: {room.id})")

        print(f"Всего создано комнат: {len(self.rooms)}")

    def add_owner_device(self, device):
        """Добавление мобильного устройства хозяина"""
        self.owner_device = device
        print("Мобильное устройство хозяина добавлено")

    def get_room(self, room_id: str):
        if room_id not in self.rooms:
            # Поиск по имени комнаты
            for room in self.rooms.values():
                if room.name.lower() == room_id.lower():
                    return room
            raise RoomNotFoundError(f"Комната {room_id} не найдена")
        return self.rooms[room_id]

    def get_device(self, device_id: str):
        # Проверяем устройство хозяина
        if self.owner_device and self.owner_device.id == device_id:
            return self.owner_device

        # Проверяем сигнализацию
        if self.security_system and self.security_system.id == device_id:
            return self.security_system

        # Проверяем комнаты
        for room in self.rooms.values():
            if device_id in room.devices:
                return room.devices[device_id]
        raise DeviceNotFoundError(f"Устройство {device_id} не найдено")

    def add_security_system(self, security) -> None:
        if self.security_system:
            raise SmartHomeError("Сигнализация уже существует")
        self.security_system = security
        print("Сигнализация установлена")

    def add_automation_rule(self, rule) -> None:
        self.automation_rules[rule.id] = rule

    def remove_automation_rule(self, rule_id: str) -> None:
        if rule_id not in self.automation_rules:
            raise ValueError(f"Правило {rule_id} не найдено")
        del self.automation_rules[rule_id]

    def check_automation_rules(self) -> None:
        home_state = self.get_state()
        for rule in self.automation_rules.values():
            if rule.enabled and rule.check_condition(home_state):
                rule.execute_actions(self)

    def get_state(self) -> dict:
        state = {
            'name': self.name,
            'rooms': {},
            'automation_rules': {}
        }

        for rid, room in self.rooms.items():
            room_devices = {}
            for did, device in room.devices.items():
                room_devices[did] = {
                    'id': device.id,
                    'name': device.name,
                    'type': device.get_device_type(),
                    'status': device.status
                }
            state['rooms'][rid] = {
                'id': room.id,
                'name': room.name,
                'devices': room_devices
            }

        if self.security_system:
            state['security_system'] = {
                'id': self.security_system.id,
                'name': self.security_system.name,
                'armed': self.security_system.armed,
                'alarm_triggered': self.security_system.alarm_triggered
            }

        if self.owner_device:
            state['owner_device'] = {
                'id': self.owner_device.id,
                'name': self.owner_device.name,
                'connected': True
            }

        for rid, rule in self.automation_rules.items():
            state['automation_rules'][rid] = {
                'id': rule.id,
                'name': rule.name,
                'condition': rule.condition,
                'actions': rule.actions,
                'enabled': rule.enabled
            }

        return state