"""Основной класс умного дома"""

"""Основной класс умного дома с поддержкой сохранения состояния"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from exceptions import RoomNotFoundError, DeviceNotFoundError, SmartHomeError
from Room import Room
from SmartDevice import SmartDevice
from LightDevice import LightDevice
from ClimateDevice import ClimateDevice
from SecuritySystem import SecuritySystem
from SmartCleaner import SmartCleaner
from SmartKettle import SmartKettle
from OwnerDevice import OwnerDevice
from Automation import AutomationRule


class SmartHome:
    """Основной класс умного дома"""

    def __init__(self, name: str):
        self.name = name
        # Фиксированные комнаты
        self.rooms: Dict[str, Room] = {}
        self._init_default_rooms()
        self.security_system: Optional[SecuritySystem] = None
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.owner_device: Optional[OwnerDevice] = None

    def _init_default_rooms(self) -> None:
        """Инициализация фиксированных комнат"""
        print("Создаю фиксированные комнаты...")
        default_rooms = ["детская", "ванная", "спальня", "кухня", "гостиная", "коридор"]

        for room_name in default_rooms:
            room = Room(room_name)
            self.rooms[room.id] = room
            print(f"  Комната '{room_name}' создана (ID: {room.id})")

        print(f"Всего создано комнат: {len(self.rooms)}")

    def add_owner_device(self, device: OwnerDevice) -> None:
        """Добавление мобильного устройства хозяина"""
        self.owner_device = device
        print("Мобильное устройство хозяина добавлено")

    def get_room(self, room_id: str) -> Room:
        """Получить комнату по ID или имени"""
        if room_id in self.rooms:
            return self.rooms[room_id]

        # Поиск по имени комнаты
        for room in self.rooms.values():
            if room.name.lower() == room_id.lower():
                return room

        raise RoomNotFoundError(f"Комната {room_id} не найдена")

    def get_device(self, device_id: str) -> SmartDevice:
        """Получить устройство по ID"""
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

    def add_security_system(self, security: SecuritySystem) -> None:
        """Добавить систему безопасности"""
        if self.security_system:
            raise SmartHomeError("Сигнализация уже существует")
        self.security_system = security
        print("Сигнализация установлена")

    def add_automation_rule(self, rule: AutomationRule) -> None:
        """Добавить правило автоматизации"""
        self.automation_rules[rule.id] = rule

    def remove_automation_rule(self, rule_id: str) -> None:
        """Удалить правило автоматизации"""
        if rule_id not in self.automation_rules:
            raise ValueError(f"Правило {rule_id} не найдено")
        del self.automation_rules[rule_id]

    def check_automation_rules(self) -> None:
        """Проверить все правила автоматизации"""
        home_state = self.get_state()
        for rule in self.automation_rules.values():
            if rule.enabled and rule.check_condition(home_state):
                rule.execute_actions(self)

    def get_state(self) -> dict:
        """Получить текущее состояние дома"""
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
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat()
            }

        return state

    # ==================== МЕТОДЫ СОХРАНЕНИЯ/ЗАГРУЗКИ ====================

    def _serialize_device(self, device: SmartDevice) -> dict:
        """Преобразует устройство в словарь для JSON"""
        base = {
            'id': device.id,
            'name': device.name,
            'room_id': device.room_id,
            'status': device.status,
            'device_type': device.get_device_type(),
        }

        if isinstance(device, LightDevice):
            base['brightness'] = device.brightness

        elif isinstance(device, ClimateDevice):
            base.update({
                'temperature': device.temperature,
                'target_temperature': device.target_temperature,
                'humidity': device.humidity,
                'target_humidity': device.target_humidity,
                'mode': device.mode,
                'fan_speed': device.fan_speed,
            })
            if hasattr(device, 'min_temperature'):
                base['min_temperature'] = device.min_temperature
                base['max_temperature'] = device.max_temperature
            if hasattr(device, 'min_humidity'):
                base['min_humidity'] = device.min_humidity
                base['max_humidity'] = device.max_humidity

        elif isinstance(device, SmartCleaner):
            base['mode'] = device.mode

        elif isinstance(device, SmartKettle):
            base.update({
                'water_level': device.water_level,
                'temperature': device.temperature,
                'boiling': device.boiling
            })

        elif isinstance(device, SecuritySystem):
            base.update({
                'armed': device.armed,
                'alarm_triggered': device.alarm_triggered
            })

        elif isinstance(device, OwnerDevice):
            base.update({
                'connected': device.connected,
                'last_access': device.last_access.isoformat() if device.last_access else None
            })

        return base

    def _deserialize_device(self, data: dict, room_id: str) -> Optional[SmartDevice]:
        """Воссоздает устройство из словаря"""
        device_type = data.get('device_type')
        name = data.get('name')
        device = None

        if device_type == "освещение":
            device = LightDevice(name, room_id)
            if 'brightness' in data:
                device.brightness = data['brightness']

        elif device_type == "климат":
            device = ClimateDevice(name, room_id)
            device.temperature = data.get('temperature', 22.0)
            device.target_temperature = data.get('target_temperature', 22.0)
            device.humidity = data.get('humidity', 50.0)
            device.target_humidity = data.get('target_humidity', 50.0)
            device.mode = data.get('mode', 'auto')
            device.fan_speed = data.get('fan_speed', 'auto')
            if 'min_temperature' in data:
                device.min_temperature = data['min_temperature']
                device.max_temperature = data['max_temperature']
            if 'min_humidity' in data:
                device.min_humidity = data['min_humidity']
                device.max_humidity = data['max_humidity']

        elif device_type == "пылесос":
            device = SmartCleaner(name, room_id)
            device.mode = data.get('mode', 'обычный')

        elif device_type == "чайник":
            device = SmartKettle(name, room_id)
            device.water_level = data.get('water_level', 100)
            device.temperature = data.get('temperature', 20)
            device.boiling = data.get('boiling', False)

        elif device_type == "безопасность":
            device = SecuritySystem(name)
            device.armed = data.get('armed', False)
            device.alarm_triggered = data.get('alarm_triggered', False)

        elif device_type == "мобильное устройство":
            device = OwnerDevice(name)
            device.connected = data.get('connected', True)
            if data.get('last_access'):
                try:
                    device.last_access = datetime.fromisoformat(data['last_access'])
                except (ValueError, TypeError):
                    device.last_access = None

        if device:
            device.id = data.get('id', device.id)
            device.status = data.get('status', False)

        return device

    def save_state(self, filepath: str = "smarthome_state.json") -> None:
        """Сохраняет состояние дома в файл"""
        state_data = {
            'name': self.name,
            'rooms': {},
            'security_system': None,
            'owner_device': None,
            'automation_rules': {}
        }

        # Сохраняем комнаты и устройства в них
        for room_id, room in self.rooms.items():
            room_data = {
                'id': room.id,
                'name': room.name,
                'devices': {}
            }
            for device_id, device in room.devices.items():
                room_data['devices'][device_id] = self._serialize_device(device)
            state_data['rooms'][room_id] = room_data

        # Сохраняем сигнализацию
        if self.security_system:
            state_data['security_system'] = self._serialize_device(self.security_system)

        # Сохраняем устройство хозяина
        if self.owner_device:
            state_data['owner_device'] = self._serialize_device(self.owner_device)

        # Сохраняем правила автоматизации
        for rule_id, rule in self.automation_rules.items():
            state_data['automation_rules'][rule_id] = {
                'id': rule.id,
                'name': rule.name,
                'condition': rule.condition,
                'actions': rule.actions,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat()
            }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            print(f"✓ Состояние сохранено в {filepath}")
        except Exception as e:
            raise SmartHomeError(f"Не удалось сохранить состояние: {e}")

    def load_state(self, filepath: str = "smarthome_state.json") -> None:
        """Загружает состояние дома из файла"""
        if not os.path.exists(filepath):
            print(f"Файл {filepath} не найден. Запуск с состоянием по умолчанию.")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SmartHomeError(f"Ошибка формата JSON: {e}")
        except Exception as e:
            raise SmartHomeError(f"Не удалось загрузить состояние: {e}")

        # Очищаем текущее состояние перед загрузкой
        self.rooms.clear()
        self.automation_rules.clear()
        self.security_system = None
        self.owner_device = None

        # Восстанавливаем имя
        self.name = data.get('name', self.name)

        # Загружаем комнаты
        from Room import Room
        for room_id, room_data in data.get('rooms', {}).items():
            room = Room(room_data.get('name', 'Неизвестно'))
            room.id = room_id
            self.rooms[room_id] = room

            # Загружаем устройства в комнате
            for device_id, device_data in room_data.get('devices', {}).items():
                device = self._deserialize_device(device_data, room_id)
                if device:
                    device.id = device_id
                    room.add_device(device)

        # Загружаем сигнализацию
        sec_data = data.get('security_system')
        if sec_data:
            self.security_system = self._deserialize_device(sec_data, "house")
            if self.security_system:
                self.security_system.id = sec_data.get('id', self.security_system.id)

        # Загружаем устройство хозяина
        owner_data = data.get('owner_device')
        if owner_data:
            self.owner_device = self._deserialize_device(owner_data, "")
            if self.owner_device:
                self.owner_device.id = owner_data.get('id', self.owner_device.id)

        # Загружаем правила автоматизации
        from Automation import AutomationRule
        for rule_id, rule_data in data.get('automation_rules', {}).items():
            rule = AutomationRule(
                rule_data['name'],
                rule_data['condition'],
                rule_data['actions']
            )
            rule.id = rule_id
            rule.enabled = rule_data.get('enabled', True)
            if rule_data.get('created_at'):
                try:
                    rule.created_at = datetime.fromisoformat(rule_data['created_at'])
                except (ValueError, TypeError):
                    pass  # Оставляем текущее время
            self.automation_rules[rule_id] = rule

        print(f"✓ Состояние загружено из {filepath}")
        print(f"  Загружено комнат: {len(self.rooms)}")
        print(f"  Загружено правил: {len(self.automation_rules)}")