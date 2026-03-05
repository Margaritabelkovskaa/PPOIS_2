"""Юнит-тесты для всех классов умного дома (максимальное покрытие)"""

import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch, MagicMock
import json
import os

from exceptions import SmartHomeError, DeviceNotFoundError, RoomNotFoundError, InvalidValueError
from Room import Room
from SmartDevice import SmartDevice
from LightDevice import LightDevice
from ClimateDevice import ClimateDevice
from SecuritySystem import SecuritySystem
from SmartCleaner import SmartCleaner
from SmartKettle import SmartKettle
from OwnerDevice import OwnerDevice
from Automation import AutomationRule
from SmartHome import SmartHome
from SmartHomeCLI import SmartHomeCLI


# ==================== ТЕСТЫ ИСКЛЮЧЕНИЙ ====================

class TestExceptions:
    def test_exceptions(self):
        e1 = SmartHomeError("Ошибка")
        assert str(e1) == "Ошибка"
        assert isinstance(e1, Exception)

        e2 = DeviceNotFoundError("Устройство не найдено")
        assert isinstance(e2, SmartHomeError)

        e3 = RoomNotFoundError("Комната не найдена")
        assert isinstance(e3, SmartHomeError)

        e4 = InvalidValueError("Неверное значение")
        assert isinstance(e4, SmartHomeError)


# ==================== ТЕСТЫ КОМНАТЫ ====================

class TestRoom:
    def setup_method(self):
        self.room = Room("спальня")
        self.device = LightDevice("лампа", self.room.id)

    def test_room_operations(self):
        assert self.room.name == "спальня"
        assert self.room.id is not None
        assert len(self.room.devices) == 0

        self.room.add_device(self.device)
        assert len(self.room.devices) == 1
        assert self.device.id in self.room.devices

        found = self.room.get_device(self.device.id)
        assert found == self.device

        self.room.remove_device(self.device.id)
        assert len(self.room.devices) == 0

        with pytest.raises(DeviceNotFoundError):
            self.room.get_device("несущ")

        with pytest.raises(DeviceNotFoundError):
            self.room.remove_device("несущ")

    def test_get_devices_by_type(self):
        light = LightDevice("лампа", self.room.id)
        climate = ClimateDevice("кондей", self.room.id)
        self.room.add_device(light)
        self.room.add_device(climate)

        lights = self.room.get_devices_by_type("освещение")
        assert len(lights) == 1
        assert light in lights
        assert climate not in lights


# ==================== ТЕСТЫ УСТРОЙСТВ ====================

class TestSmartDevice:
    def setup_method(self):
        class TestDevice(SmartDevice):
            def get_device_type(self):
                return "тест"
        self.device = TestDevice("тест", "room_123")

    def test_device_operations(self):
        assert self.device.name == "тест"
        assert self.device.room_id == "room_123"
        assert self.device.status is False

        self.device.turn_on()
        assert self.device.status is True

        self.device.turn_off()
        assert self.device.status is False

        status = self.device.get_status()
        assert status['name'] == "тест"
        assert status['type'] == "тест"
        assert status['status'] == "выключено"


class TestLightDevice:
    def setup_method(self):
        self.device = LightDevice("лампа", "room_123")

    def test_light_operations(self):
        assert self.device.get_device_type() == "освещение"
        assert self.device.brightness == 100

        self.device.set_brightness(50)
        assert self.device.brightness == 50

        with pytest.raises(InvalidValueError):
            self.device.set_brightness(-10)

        with pytest.raises(InvalidValueError):
            self.device.set_brightness(150)

        status = self.device.get_status()
        assert status['brightness'] == 50


class TestClimateDevice:
    def setup_method(self):
        self.device = ClimateDevice("кондей", "room_123")

    def test_initialization(self):
        assert self.device.get_device_type() == "климат"
        assert self.device.temperature == 22.0
        assert self.device.target_temperature == 22.0
        assert self.device.humidity == 50.0
        assert self.device.target_humidity == 50.0
        assert self.device.mode == "auto"
        assert self.device.fan_speed == "auto"

    def test_temperature(self):
        self.device.set_temperature(24)
        assert self.device.target_temperature == 24

        self.device.set_temperature(16)
        assert self.device.target_temperature == 16

        self.device.set_temperature(30)
        assert self.device.target_temperature == 30

        with pytest.raises(InvalidValueError):
            self.device.set_temperature(15)

        with pytest.raises(InvalidValueError):
            self.device.set_temperature(31)

    def test_temperature_range(self):
        self.device.set_temperature_range(20, 25)
        assert hasattr(self.device, 'min_temperature')
        assert self.device.min_temperature == 20
        assert self.device.max_temperature == 25

        with pytest.raises(InvalidValueError):
            self.device.set_temperature_range(15, 25)

        with pytest.raises(InvalidValueError):
            self.device.set_temperature_range(25, 20)

    def test_humidity(self):
        self.device.set_humidity(55)
        assert self.device.target_humidity == 55

        self.device.set_humidity(30)
        assert self.device.target_humidity == 30

        self.device.set_humidity(80)
        assert self.device.target_humidity == 80

        with pytest.raises(InvalidValueError):
            self.device.set_humidity(20)

        with pytest.raises(InvalidValueError):
            self.device.set_humidity(90)

    def test_humidity_range(self):
        self.device.set_humidity_range(40, 60)
        assert hasattr(self.device, 'min_humidity')
        assert self.device.min_humidity == 40
        assert self.device.max_humidity == 60

        with pytest.raises(InvalidValueError):
            self.device.set_humidity_range(20, 60)

        with pytest.raises(InvalidValueError):
            self.device.set_humidity_range(40, 90)

        with pytest.raises(InvalidValueError):
            self.device.set_humidity_range(50, 40)

    def test_humidity_adjust(self):
        self.device.humidity = 45
        self.device.increase_humidity()
        assert self.device.humidity == 50

        self.device.humidity = 78
        self.device.increase_humidity()
        assert self.device.humidity == 80
        self.device.increase_humidity()
        assert self.device.humidity == 80

        self.device.humidity = 55
        self.device.decrease_humidity()
        assert self.device.humidity == 50

        self.device.humidity = 32
        self.device.decrease_humidity()
        assert self.device.humidity == 30
        self.device.decrease_humidity()
        assert self.device.humidity == 30

    def test_modes(self):
        self.device.set_mode("cool")
        assert self.device.mode == "cool"

        self.device.set_mode("heat")
        assert self.device.mode == "heat"

        self.device.set_mode("dry")
        assert self.device.mode == "dry"

        self.device.set_mode("fan_only")
        assert self.device.mode == "fan_only"

        with pytest.raises(InvalidValueError):
            self.device.set_mode("invalid")

    def test_fan_speed(self):
        self.device.set_fan_speed("low")
        assert self.device.fan_speed == "low"

        self.device.set_fan_speed("medium")
        assert self.device.fan_speed == "medium"

        self.device.set_fan_speed("high")
        assert self.device.fan_speed == "high"

        with pytest.raises(InvalidValueError):
            self.device.set_fan_speed("invalid")

    def test_auto_adjust(self):
        self.device.turn_on()
        self.device.temperature = 20
        self.device.target_temperature = 22
        self.device.humidity = 45
        self.device.target_humidity = 50

        self.device.auto_adjust()
        assert self.device.temperature == 20.5
        assert self.device.humidity == 47

        self.device.turn_off()
        self.device.auto_adjust()
        assert self.device.temperature == 20.5

    def test_get_status(self):
        self.device.set_temperature(24)
        self.device.set_humidity(55)
        self.device.set_mode("cool")
        self.device.set_fan_speed("medium")

        status = self.device.get_status()
        assert status['target_temperature'] == 24
        assert status['target_humidity'] == 55
        assert status['mode'] == "cool"
        assert status['fan_speed'] == "medium"

        self.device.set_temperature_range(20, 25)
        self.device.set_humidity_range(40, 60)
        status = self.device.get_status()
        assert 'min_temperature' in status
        assert 'max_temperature' in status
        assert 'min_humidity' in status
        assert 'max_humidity' in status


class TestSecuritySystem:
    def setup_method(self):
        self.device = SecuritySystem("сигнал")

    def test_security_operations(self):
        assert self.device.get_device_type() == "безопасность"
        assert self.device.room_id == "house"
        assert self.device.armed is False
        assert self.device.alarm_triggered is False

        self.device.arm()
        assert self.device.armed is True

        self.device.trigger_alarm()
        assert self.device.alarm_triggered is True

        self.device.disarm()
        assert self.device.armed is False
        assert self.device.alarm_triggered is False

        status = self.device.get_status()
        assert 'armed' in status
        assert 'alarm_triggered' in status


class TestSmartCleaner:
    def setup_method(self):
        self.device = SmartCleaner("пылесос", "room_123")

    def test_cleaner_operations(self):
        assert self.device.get_device_type() == "пылесос"
        assert self.device.mode == "обычный"

        self.device.set_mode("влажная")
        assert self.device.mode == "влажная"

        self.device.set_mode("обычный")
        assert self.device.mode == "обычный"

        self.device.set_mode("несуществующий")
        assert self.device.mode == "обычный"

        self.device.clean()
        assert self.device.status is True

        self.device.stop()
        assert self.device.status is False

        status = self.device.get_status()
        assert 'mode' in status


class TestSmartKettle:
    def setup_method(self):
        self.device = SmartKettle("чайник", "room_123")

    def test_kettle_operations(self):
        assert self.device.get_device_type() == "чайник"
        assert self.device.water_level == 100
        assert self.device.temperature == 20

        self.device.boil()
        assert self.device.temperature == 100
        assert self.device.status is True

        self.device.water_level = 5
        self.device.boil()
        assert self.device.temperature == 100

        self.device.set_temperature(80)
        assert self.device.temperature == 80

        self.device.set_temperature(40)
        assert self.device.temperature == 40

        self.device.set_temperature(100)
        assert self.device.temperature == 100

        self.device.set_temperature(30)
        assert self.device.temperature == 100

        status = self.device.get_status()
        assert 'water' in status
        assert 'temperature' in status


# ==================== ТЕСТЫ УСТРОЙСТВА ХОЗЯИНА ====================

class TestOwnerDevice:
    def setup_method(self):
        self.device = OwnerDevice("iPhone")

    def test_owner_operations(self):
        assert self.device.get_device_type() == "мобильное устройство"
        assert self.device.connected is True
        assert self.device.id is not None

        self.device.disconnect()
        assert self.device.connected is False

        self.device.connect()
        assert self.device.connected is True
        assert self.device.last_access is not None

        status = self.device.get_status()
        assert status['name'] == "iPhone"
        assert status['connected'] == 'да'

        self.device.send_notification("Тест")

        self.device.disconnect()
        self.device.send_notification("Тест")


# ==================== ТЕСТЫ АВТОМАТИЗАЦИИ ====================

class TestAutomationRule:
    def setup_method(self):
        self.rule = AutomationRule(
            "тест",
            {'type': 'time', 'time': '12:00'},
            [{'device_id': '123', 'type': 'turn_on'}]
        )

    @patch('Automation.datetime')
    def test_time_condition_true(self, mock_datetime):
        mock_now = Mock()
        mock_now.time.return_value = time(12, 30)
        mock_datetime.now.return_value = mock_now
        mock_target = Mock()
        mock_target.time.return_value = time(12, 0)
        mock_datetime.strptime.return_value = mock_target
        assert self.rule.check_condition({}) is True

    @patch('Automation.datetime')
    def test_time_condition_false(self, mock_datetime):
        mock_now = Mock()
        mock_now.time.return_value = time(11, 30)
        mock_datetime.now.return_value = mock_now
        mock_target = Mock()
        mock_target.time.return_value = time(12, 0)
        mock_datetime.strptime.return_value = mock_target
        assert self.rule.check_condition({}) is False

    def test_device_status_condition_true(self):
        rule = AutomationRule(
            "тест",
            {'type': 'device_status', 'device_id': 'dev1', 'status': 'включено'},
            []
        )
        state = {
            'rooms': {
                'room1': {
                    'devices': {
                        'dev1': {'status': True}
                    }
                }
            }
        }
        assert rule.check_condition(state) is True

    def test_device_status_condition_false(self):
        rule = AutomationRule(
            "тест",
            {'type': 'device_status', 'device_id': 'dev1', 'status': 'включено'},
            []
        )
        state = {
            'rooms': {
                'room1': {
                    'devices': {
                        'dev1': {'status': False}
                    }
                }
            }
        }
        assert rule.check_condition(state) is False

    def test_device_not_found(self):
        rule = AutomationRule(
            "тест",
            {'type': 'device_status', 'device_id': 'dev1', 'status': 'включено'},
            []
        )
        state = {'rooms': {'room1': {'devices': {}}}}
        assert rule.check_condition(state) is False

    def test_unknown_condition(self):
        rule = AutomationRule("тест", {'type': 'unknown'}, [])
        assert rule.check_condition({}) is False

    def test_condition_descriptions(self):
        mock_home = Mock()
        desc1 = self.rule.get_condition_description(mock_home)
        assert "Время: 12:00" in desc1

        rule2 = AutomationRule("тест",
                               {'type': 'device_status', 'device_id': 'dev1', 'status': 'включено'}, [])
        mock_device = Mock()
        mock_device.name = "Тестовое устройство"
        mock_device.get_device_type.return_value = "тест"
        mock_home.get_device.return_value = mock_device
        desc2 = rule2.get_condition_description(mock_home)
        assert "Устройство: Тестовое устройство (тест)" in desc2

        mock_home.get_device.side_effect = Exception("Not found")
        desc3 = rule2.get_condition_description(mock_home)
        assert "Устройство ID: dev1" in desc3

    def test_action_descriptions(self):
        actions = [
            {'device_id': '1', 'type': 'turn_on'},
            {'device_id': '2', 'type': 'turn_off'},
            {'device_id': '3', 'type': 'set_temperature', 'temperature': 25},
            {'device_id': '4', 'type': 'set_humidity', 'humidity': 55},
            {'device_id': '5', 'type': 'set_brightness', 'brightness': 50},
            {'device_id': '6', 'type': 'start_cleaning'},
            {'device_id': '7', 'type': 'boil'},
            {'device_id': '8', 'type': 'arm_alarm'},
            {'device_id': '9', 'type': 'disarm_alarm'},
            {'device_id': '10', 'type': 'unknown'}
        ]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        def mock_get(id):
            d = Mock()
            d.name = f"Устройство {id}"
            d.get_device_type.return_value = "тест"
            return d
        mock_home.get_device.side_effect = mock_get

        descs = rule.get_actions_description(mock_home)
        assert len(descs) == 10

        mock_home.get_device.side_effect = Exception("Not found")
        descs = rule.get_actions_description(mock_home)
        assert len(descs) == 10

    def test_execute_actions(self):
        mock_home = Mock()
        mock_device = Mock()
        mock_home.get_device.return_value = mock_device

        self.rule.execute_actions(mock_home)
        mock_device.turn_on.assert_called_once()

    def test_execute_actions_disabled(self):
        self.rule.enabled = False
        mock_home = Mock()
        self.rule.execute_actions(mock_home)
        mock_home.get_device.assert_not_called()

    def test_execute_actions_error(self):
        mock_home = Mock()
        mock_home.get_device.side_effect = Exception("Ошибка")
        self.rule.execute_actions(mock_home)

    def test_execute_actions_all_types(self):
        actions = [
            {'device_id': '1', 'type': 'turn_on'},
            {'device_id': '2', 'type': 'turn_off'},
            {'device_id': '3', 'type': 'set_temperature', 'temperature': 25},
            {'device_id': '4', 'type': 'set_humidity', 'humidity': 55},
            {'device_id': '5', 'type': 'set_brightness', 'brightness': 50},
            {'device_id': '6', 'type': 'start_cleaning'},
            {'device_id': '7', 'type': 'boil'},
            {'device_id': '8', 'type': 'arm_alarm'},
            {'device_id': '9', 'type': 'disarm_alarm'},
        ]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        devices = {}
        for i in range(1, 10):
            device = Mock()
            device.name = f"Устройство {i}"
            device.turn_on = Mock()
            device.turn_off = Mock()
            device.set_temperature = Mock()
            device.set_humidity = Mock()
            device.set_brightness = Mock()
            device.clean = Mock()
            device.boil = Mock()
            device.arm = Mock()
            device.disarm = Mock()
            devices[str(i)] = device

        mock_home.get_device.side_effect = lambda x: devices[x]
        rule.execute_actions(mock_home)

        devices['1'].turn_on.assert_called_once()
        devices['2'].turn_off.assert_called_once()
        devices['3'].set_temperature.assert_called_with(25)
        devices['4'].set_humidity.assert_called_with(55)
        devices['5'].set_brightness.assert_called_with(50)
        devices['6'].clean.assert_called_once()
        devices['7'].boil.assert_called_once()
        devices['8'].arm.assert_called_once()
        devices['9'].disarm.assert_called_once()


# ==================== ТЕСТЫ УМНОГО ДОМА ====================

class TestSmartHome:
    def setup_method(self):
        self.home = SmartHome("Мой умный дом")

    def test_default_rooms(self):
        names = [r.name for r in self.home.rooms.values()]
        assert "спальня" in names
        assert "кухня" in names
        assert "гостиная" in names
        assert "коридор" in names
        assert len(self.home.rooms) == 6

    def test_add_owner(self):
        device = OwnerDevice("iPhone")
        self.home.add_owner_device(device)
        assert self.home.owner_device == device

    def test_get_room(self):
        room_id = list(self.home.rooms.keys())[0]
        room = self.home.get_room(room_id)
        assert room.id == room_id

        room = self.home.get_room("спальня")
        assert room.name == "спальня"

        with pytest.raises(RoomNotFoundError):
            self.home.get_room("несущ")

    def test_get_device(self):
        owner = OwnerDevice("iPhone")
        self.home.add_owner_device(owner)
        assert self.home.get_device(owner.id) == owner

        security = SecuritySystem("сигнал")
        self.home.add_security_system(security)
        assert self.home.get_device(security.id) == security

        room = list(self.home.rooms.values())[0]
        light = LightDevice("лампа", room.id)
        room.add_device(light)
        assert self.home.get_device(light.id) == light

        with pytest.raises(DeviceNotFoundError):
            self.home.get_device("несущ")

    def test_security_system(self):
        sec = SecuritySystem("сигнал")
        self.home.add_security_system(sec)
        assert self.home.security_system == sec

        with pytest.raises(SmartHomeError):
            self.home.add_security_system(SecuritySystem("еще"))

    def test_automation_rules(self):
        rule = AutomationRule("тест", {}, [])
        self.home.add_automation_rule(rule)
        assert rule.id in self.home.automation_rules

        self.home.remove_automation_rule(rule.id)
        assert rule.id not in self.home.automation_rules

        with pytest.raises(ValueError):
            self.home.remove_automation_rule("несущ")

    def test_check_automation(self):
        mock_rule = Mock()
        mock_rule.enabled = True
        mock_rule.check_condition.return_value = True
        self.home.automation_rules = {"1": mock_rule}
        self.home.check_automation_rules()
        mock_rule.execute_actions.assert_called_once()

    def test_get_state(self):
        state = self.home.get_state()
        assert state['name'] == "Мой умный дом"
        assert 'rooms' in state
        assert 'automation_rules' in state


# ==================== ТЕСТЫ CLI ====================

class TestSmartHomeCLI:
    def setup_method(self):
        self.cli = SmartHomeCLI()
        # Очищаем устройства для тестов
        for room in self.cli.home.rooms.values():
            room.devices.clear()

        room = list(self.cli.home.rooms.values())[0]
        self.light = LightDevice("тест лампа", room.id)
        room.add_device(self.light)
        self.climate = ClimateDevice("тест кондей", room.id)
        room.add_device(self.climate)
        self.cleaner = SmartCleaner("тест пылесос", room.id)
        room.add_device(self.cleaner)
        self.kettle = SmartKettle("тест чайник", room.id)
        room.add_device(self.kettle)
        self.security = SecuritySystem("тест сигнал")
        self.cli.home.add_security_system(self.security)

    def test_initialization(self):
        assert self.cli.home.name == "Мой умный дом"

    def test_setup_default_owner(self):
        self.cli.home.owner_device = None
        self.cli._setup_default_owner()
        assert self.cli.home.owner_device is not None

    def test_get_device_type_name(self):
        assert self.cli.get_device_type_name(LightDevice("", "")) == "освещение"
        assert self.cli.get_device_type_name(ClimateDevice("", "")) == "климат-контроль"
        assert self.cli.get_device_type_name(SmartCleaner("", "")) == "пылесос"
        assert self.cli.get_device_type_name(SmartKettle("", "")) == "чайник"
        assert self.cli.get_device_type_name(SecuritySystem("")) == "сигнализация"
        assert self.cli.get_device_type_name(OwnerDevice()) == "мобильное устройство"
        assert self.cli.get_device_type_name(Mock()) == "неизвестное устройство"

    def test_get_available_actions(self):
        assert len(self.cli.get_available_actions(LightDevice("", ""))) == 3
        assert len(self.cli.get_available_actions(ClimateDevice("", ""))) == 4
        assert len(self.cli.get_available_actions(SmartCleaner("", ""))) == 3
        assert len(self.cli.get_available_actions(SmartKettle("", ""))) == 4
        assert len(self.cli.get_available_actions(SecuritySystem(""))) == 4
        assert len(self.cli.get_available_actions(OwnerDevice())) == 2

    def test_get_device_icon(self):
        assert self.cli.get_device_icon(self.light) == ""

    def test_show_menu(self, capsys):
        self.cli.show_menu()
        out = capsys.readouterr().out
        assert "Умный дом" in out

    def test_list_rooms(self, capsys):
        self.cli.list_rooms()
        out = capsys.readouterr().out
        assert "КОМНАТЫ" in out

    def test_list_devices(self, capsys):
        self.cli.list_devices()
        out = capsys.readouterr().out
        assert "ВСЕ УСТРОЙСТВА" in out

    def test_list_devices_short(self, capsys):
        self.cli.list_devices_short()
        out = capsys.readouterr().out
        assert "Доступные устройства" in out


    def test_control_lights_no_lights(self, capsys):
        for room in self.cli.home.rooms.values():
            for d in list(room.devices.values()):
                if isinstance(d, LightDevice):
                    room.remove_device(d.id)
        self.cli.control_lights()
        out = capsys.readouterr().out
        assert "Нет лампочек" in out

    def test_control_cleaner_no_cleaner(self, capsys):
        for room in self.cli.home.rooms.values():
            for d in list(room.devices.values()):
                if isinstance(d, SmartCleaner):
                    room.remove_device(d.id)
        self.cli.control_cleaner()
        out = capsys.readouterr().out
        assert "Нет пылесоса" in out

    def test_control_kettle_no_kettle(self, capsys):
        for room in self.cli.home.rooms.values():
            for d in list(room.devices.values()):
                if isinstance(d, SmartKettle):
                    room.remove_device(d.id)
        self.cli.control_kettle()
        out = capsys.readouterr().out
        assert "Нет чайника" in out

    def test_control_security_no_security(self, capsys):
        self.cli.home.security_system = None
        self.cli.control_security()
        out = capsys.readouterr().out
        assert "Сигнализация не установлена" in out

    def test_add_device(self, monkeypatch):
        inputs = iter(['1', 'тест лампа', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()

    def test_add_device_invalid_type(self, monkeypatch):
        inputs = iter(['99', 'тест', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()

    def test_add_device_empty_name(self, monkeypatch):
        inputs = iter(['1', ''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        with pytest.raises(InvalidValueError):
            self.cli.add_device()

    def test_add_device_invalid_room(self, monkeypatch):
        inputs = iter(['1', 'тест', '99'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()

    def test_add_device_security(self, monkeypatch):
        self.cli.home.security_system = None
        inputs = iter(['5', 'тест сигнал'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()
        assert self.cli.home.security_system is not None

    def test_add_device_security_already_exists(self, monkeypatch):
        inputs = iter(['5', 'тест сигнал'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()

    def test_control_menu(self, monkeypatch):
        inputs = iter(['0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_menu()

    def test_control_menu_invalid(self, monkeypatch):
        inputs = iter(['99', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_menu()

    def test_control_lights_with_lights(self, monkeypatch):
        inputs = iter(['1', '1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()

    def test_control_lights_set_brightness(self, monkeypatch):
        inputs = iter(['1', '2', '75', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()
        assert self.light.brightness == 75

    def test_control_lights_set_brightness_invalid(self, monkeypatch):
        inputs = iter(['1', '2', 'abc', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()

    def test_control_lights_turn_on_all(self, monkeypatch):
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()

    def test_control_lights_turn_off_all(self, monkeypatch):
        inputs = iter(['3', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()

    def test_control_climate_with_climate(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_temperature(self, monkeypatch):
        inputs = iter(['1', '2', '24', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_temperature == 24

    def test_control_climate_set_temperature_invalid(self, monkeypatch):
        inputs = iter(['1', '2', 'abc', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_humidity(self, monkeypatch):
        inputs = iter(['1', '3', '55', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_humidity == 55

    def test_control_climate_set_humidity_invalid(self, monkeypatch):
        inputs = iter(['1', '3', 'abc', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_increase_humidity(self, monkeypatch):
        inputs = iter(['1', '4', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_decrease_humidity(self, monkeypatch):
        inputs = iter(['1', '5', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_mode(self, monkeypatch):
        inputs = iter(['1', '6', 'cool', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.mode == "cool"

    def test_control_climate_set_mode_invalid(self, monkeypatch):
        inputs = iter(['1', '6', 'invalid', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_fan_speed(self, monkeypatch):
        inputs = iter(['1', '7', 'high', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.fan_speed == "high"

    def test_control_climate_set_fan_speed_invalid(self, monkeypatch):
        inputs = iter(['1', '7', 'invalid', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_all_18(self, monkeypatch):
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_all_24(self, monkeypatch):
        inputs = iter(['3', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_climate_set_all_humidity_50(self, monkeypatch):
        inputs = iter(['4', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_cleaner_with_cleaner(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()

    def test_control_cleaner_wet_mode(self, monkeypatch):
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()
        assert self.cleaner.mode == "влажная"

    def test_control_cleaner_stop(self, monkeypatch):
        inputs = iter(['3', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()

    def test_control_kettle_with_kettle(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()

    def test_control_kettle_set_temperature(self, monkeypatch):
        inputs = iter(['2', '80', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()
        assert self.kettle.temperature == 80

    def test_control_kettle_set_temperature_invalid(self, monkeypatch):
        inputs = iter(['2', 'abc', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()

    def test_control_security_with_security(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_security()

    def test_control_security_disarm(self, monkeypatch):
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_security()

    def test_quick_commands_all(self, monkeypatch):
        for cmd in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            inputs = iter([cmd])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            self.cli.quick_commands()

    def test_add_automation_rule_time(self, monkeypatch):
        inputs = iter(['тест', '1', '12:00', 'stop'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_add_automation_rule_device_status(self, monkeypatch):
        inputs = iter(['тест', '2', self.light.id, 'включено', 'stop'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_add_automation_rule_with_actions(self, monkeypatch):
        inputs = iter([
            'тест', '1', '12:00',
            self.light.id, '1',
            self.climate.id, '3', '24',
            'stop'
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_add_automation_rule_invalid_condition(self, monkeypatch):
        inputs = iter(['тест', '3', 'stop'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_list_automation_rules(self, capsys):
        self.cli.list_automation_rules()
        out = capsys.readouterr().out
        assert "ПРАВИЛА АВТОМАТИЗАЦИИ" in out

    def test_check_automation(self, capsys):
        self.cli.check_automation()
        out = capsys.readouterr().out
        assert "Проверка правил" in out

    def test_owner_device_menu(self, monkeypatch):
        inputs = iter(['0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_connect(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_disconnect(self, monkeypatch):
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_notification(self, monkeypatch):
        inputs = iter(['3', 'тест', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_notification_empty(self, monkeypatch):
        inputs = iter(['3', '', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_status(self, monkeypatch):
        inputs = iter(['4', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_owner_device_menu_no_device(self, monkeypatch):
        self.cli.home.owner_device = None
        inputs = iter(['0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()

    def test_run_with_save(self, monkeypatch):
        inputs = iter(['s', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.run()

    def test_run_with_invalid_choice(self, monkeypatch):
        inputs = iter(['99', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.run()

    def test_run_with_keyboard_interrupt(self, monkeypatch):
        def mock_input(_):
            raise KeyboardInterrupt()
        monkeypatch.setattr('builtins.input', mock_input)
        self.cli.run()

 

# ==================== ТЕСТЫ MAIN ====================

class TestMain:
    @patch('SmartHomeCLI.SmartHomeCLI')
    def test_main(self, mock_cli_class):
        from main import main
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli
        main()
        mock_cli_class.assert_called_once()
        mock_cli.run.assert_called_once()


# ==================== ТЕСТЫ СОХРАНЕНИЯ ====================

class TestSmartHomePersistence:
    def setup_method(self):
        self.home = SmartHome("Тестовый дом")
        # Очищаем комнаты
        for room in list(self.home.rooms.values()):
            room.devices.clear()

        room = list(self.home.rooms.values())[0]

        self.light = LightDevice("ТестЛампа", room.id)
        self.light.set_brightness(75)
        room.add_device(self.light)

        self.climate = ClimateDevice("ТестКондей", room.id)
        self.climate.set_temperature(24.5)
        self.climate.set_humidity(55)
        self.climate.set_mode("cool")
        room.add_device(self.climate)

    def test_serialize_deserialize(self):
        # Тест сериализации
        data = self.home._serialize_device(self.light)
        assert data['name'] == "ТестЛампа"
        assert data['brightness'] == 75

        data = self.home._serialize_device(self.climate)
        assert data['target_temperature'] == 24.5

        # Тест десериализации
        device = self.home._deserialize_device(
            {'device_type': 'освещение', 'name': 'Новая лампа', 'brightness': 50},
            "room_123"
        )
        assert device is not None
        assert device.name == "Новая лампа"
        assert device.brightness == 50

        # Тест десериализации неизвестного типа
        device = self.home._deserialize_device(
            {'device_type': 'unknown', 'name': 'Что-то'},
            "room_123"
        )
        assert device is None


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================

class TestIntegration:
    def test_full_device_lifecycle(self):
        home = SmartHome("Тест")
        room = list(home.rooms.values())[0]

        light = LightDevice("Лампа", room.id)
        room.add_device(light)

        light.turn_on()
        light.set_brightness(50)

        assert light.status is True
        assert light.brightness == 50

        rule = AutomationRule(
            "Тест",
            {'type': 'device_status', 'device_id': light.id, 'status': 'включено'},
            [{'device_id': light.id, 'type': 'turn_off'}]
        )
        home.add_automation_rule(rule)

        state = home.get_state()
        assert rule.check_condition(state) is True

    def test_climate_auto_adjustment(self):
        device = ClimateDevice("Кондей", "room_123")
        device.turn_on()
        device.target_temperature = 24
        device.target_humidity = 50
        device.temperature = 22
        device.humidity = 45

        device.auto_adjust()

        assert device.temperature == 22.5
        assert device.humidity == 47

    def test_security_alarm_chain(self):
        security = SecuritySystem("Сигнал")
        assert security.armed is False
        assert security.alarm_triggered is False

        security.arm()
        assert security.armed is True

        security.trigger_alarm()
        assert security.alarm_triggered is True

        security.disarm()
        assert security.armed is False
        assert security.alarm_triggered is False