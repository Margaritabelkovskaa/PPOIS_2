"""Юнит-тесты для всех классов умного дома (полная версия)"""

import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch, MagicMock

# Импортируем ВСЕ нужные классы
from exceptions import SmartHomeError, DeviceNotFoundError, RoomNotFoundError, InvalidValueError
from Room import Room
from Devices import (
    SmartDevice, LightDevice, ClimateDevice,
    SecuritySystem, SmartCleaner, SmartKettle
)
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
        self.device.auto_adjust()  # ничего не должно измениться
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
        assert self.device.temperature == 100  # не изменилась

        self.device.set_temperature(80)
        assert self.device.temperature == 80

        self.device.set_temperature(40)
        assert self.device.temperature == 40

        self.device.set_temperature(100)
        assert self.device.temperature == 100

        self.device.set_temperature(30)
        assert self.device.temperature == 100  # не изменилась

        status = self.device.get_status()
        assert status['water'] == "5%"
        assert status['temperature'] == "100°C"


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

        status = self.device.get_status()
        assert status['name'] == "iPhone"
        assert status['connected'] == 'да'

        self.device.send_notification("Тест")

        self.device.disconnect()
        self.device.send_notification("Тест")  # не должно упасть


# ==================== ТЕСТЫ АВТОМАТИЗАЦИИ ====================

class TestAutomationRule:
    def setup_method(self):
        self.rule = AutomationRule(
            "тест",
            {'type': 'time', 'time': '12:00'},
            [{'device_id': '123', 'type': 'turn_on'}]
        )

    def test_initialization(self):
        assert self.rule.name == "тест"
        assert self.rule.condition == {'type': 'time', 'time': '12:00'}
        assert self.rule.actions == [{'device_id': '123', 'type': 'turn_on'}]
        assert self.rule.enabled is True
        assert self.rule.id is not None
        assert isinstance(self.rule.created_at, datetime)

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

        # Тест для time условия
        desc1 = self.rule.get_condition_description(mock_home)
        assert "Время: 12:00" in desc1

        # Тест для device_status условия
        rule2 = AutomationRule("тест",
                               {'type': 'device_status', 'device_id': 'dev1', 'status': 'включено'}, [])

        # Вариант 1: мокаем get_device чтобы он возвращал устройство
        mock_device = Mock()
        mock_device.name = "Тестовое устройство"
        mock_device.get_device_type.return_value = "тест"
        mock_home.get_device.return_value = mock_device

        desc2 = rule2.get_condition_description(mock_home)
        # Теперь должно вернуть описание с именем устройства, а не ID
        assert "Устройство: Тестовое устройство (тест)" in desc2
        assert "статус: включено" in desc2

        # Вариант 2: если устройство не найдено
        mock_home.get_device.side_effect = Exception("Not found")
        desc3 = rule2.get_condition_description(mock_home)
        assert "Устройство ID: dev1" in desc3

    def test_action_descriptions(self):
        actions = [
            {'device_id': '1', 'type': 'turn_on'},
            {'device_id': '2', 'type': 'set_humidity', 'humidity': 55},
            {'device_id': '3', 'type': 'unknown'}
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
        assert len(descs) == 3

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
        self.rule.execute_actions(mock_home)  # не должно упасть


# ==================== ТЕСТЫ УМНОГО ДОМА ====================

class TestSmartHome:
    def setup_method(self):
        self.home = SmartHome("Мой умный дом")

    def test_initialization(self):
        assert self.home.name == "Мой умный дом"
        assert len(self.home.rooms) == 4
        assert self.home.security_system is None
        assert self.home.owner_device is None

    def test_default_rooms(self):
        names = [r.name for r in self.home.rooms.values()]
        assert "спальня" in names
        assert "кухня" in names
        assert "гостиная" in names
        assert "коридор" in names

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
        room = list(self.home.rooms.values())[0]
        light = LightDevice("лампа", room.id)
        room.add_device(light)

        sec = SecuritySystem("сигнал")
        self.home.add_security_system(sec)

        owner = OwnerDevice("iPhone")
        self.home.add_owner_device(owner)

        rule = AutomationRule("тест", {}, [])
        self.home.add_automation_rule(rule)

        state = self.home.get_state()
        assert state['name'] == "Мой умный дом"
        assert len(state['rooms']) == 4
        assert 'security_system' in state
        assert 'owner_device' in state
        assert len(state['automation_rules']) == 1


# ==================== ТЕСТЫ CLI ====================

class TestSmartHomeCLI:
    def setup_method(self):
        self.cli = SmartHomeCLI()
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
        self.owner = OwnerDevice("тест айфон")
        self.cli.home.add_owner_device(self.owner)

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

    def test_get_available_actions(self):
        assert len(self.cli.get_available_actions(LightDevice("", ""))) == 3
        assert len(self.cli.get_available_actions(ClimateDevice("", ""))) == 4
        assert len(self.cli.get_available_actions(SmartCleaner("", ""))) == 3
        assert len(self.cli.get_available_actions(SmartKettle("", ""))) == 4
        assert len(self.cli.get_available_actions(SecuritySystem(""))) == 4
        assert len(self.cli.get_available_actions(OwnerDevice())) == 2

    def test_show_menu(self, capsys):
        self.cli.show_menu()
        out = capsys.readouterr().out
        assert "=== Умный дом:" in out

    def test_run_exit(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: '0')
        self.cli.run()

    def test_control_lights_basic(self, monkeypatch):
        inputs = iter(['1', '1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()

    def test_control_lights_set_brightness(self, monkeypatch):
        inputs = iter(['1', '2', '75', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()
        assert self.light.brightness == 75

    def test_control_lights_no_lights(self, monkeypatch, capsys):
        for room in self.cli.home.rooms.values():
            for d in list(room.devices.values()):
                if isinstance(d, LightDevice):
                    room.remove_device(d.id)
        self.cli.control_lights()
        out = capsys.readouterr().out
        assert "Нет лампочек" in out

    def test_control_climate_temperature(self, monkeypatch):
        inputs = iter(['1', '2', '24.5', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_temperature == 24.5

    def test_control_climate_humidity(self, monkeypatch):
        inputs = iter(['1', '3', '55', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_humidity == 55

    def test_control_climate_set_all(self, monkeypatch):
        inputs = iter([str(len(self.cli.home.rooms) + 1), '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()

    def test_control_cleaner(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()

    def test_control_kettle(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()

    def test_control_security(self, monkeypatch):
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_security()

    def test_quick_commands(self, monkeypatch):
        for cmd in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            monkeypatch.setattr('builtins.input', lambda _: cmd)
            self.cli.quick_commands()

    def test_add_device_all_types(self, monkeypatch):
        types = ['1', '2', '3', '4']
        for t in types:
            inputs = iter([t, f"тест {t}", '1'])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            self.cli.add_device()

    def test_add_device_security(self, monkeypatch):
        self.cli.home.security_system = None
        inputs = iter(['5', 'новая сигнал'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_device()
        assert self.cli.home.security_system is not None

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

    def test_add_automation_rule(self, monkeypatch):
        inputs = iter(['тест', '1', '12:00', 'stop'])
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

    def test_monitor_security(self, capsys):
        self.cli.monitor_security()
        out = capsys.readouterr().out
        assert "МОНИТОРИНГ БЕЗОПАСНОСТИ" in out

    def test_owner_device_menu(self, monkeypatch):
        self.cli.home.owner_device = None
        inputs = iter(['1', 'тест', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()
        assert self.cli.home.owner_device is not None


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


# ==================== ТЕСТЫ ИНТЕГРАЦИИ ====================

class TestIntegration:
    def test_full_scenario(self):
        home = SmartHome("Тест")
        room = home.get_room("спальня")

        light = LightDevice("лампа", room.id)
        room.add_device(light)
        climate = ClimateDevice("кондей", room.id)
        room.add_device(climate)
        security = SecuritySystem("сигнал")
        home.add_security_system(security)
        owner = OwnerDevice("iPhone")
        home.add_owner_device(owner)

        light.turn_on()
        light.set_brightness(50)
        assert light.brightness == 50

        climate.set_temperature(24)
        climate.set_humidity(55)
        assert climate.target_humidity == 55

        security.arm()
        assert security.armed is True

        state = home.get_state()
        assert len(state['rooms']) == 4


# ==================== ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ АВТОМАТИЗАЦИИ ====================

class TestAutomationRuleAdditional:
    """Дополнительные тесты для AutomationRule"""

    def setup_method(self):
        self.rule = AutomationRule(
            "тест",
            {'type': 'time', 'time': '12:00'},
            [{'device_id': '123', 'type': 'turn_on'}]
        )

    def test_get_actions_description_all_action_types(self):
        """Тест всех типов действий в описании"""
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

        def mock_get_device(device_id):
            device = Mock()
            device.name = f"Устройство {device_id}"
            device.get_device_type.return_value = "тест"
            return device

        mock_home.get_device.side_effect = mock_get_device

        descriptions = rule.get_actions_description(mock_home)
        assert len(descriptions) == 9

        # Проверяем наличие всех типов действий
        descriptions_str = " ".join(descriptions)
        assert "Включить" in descriptions_str
        assert "Выключить" in descriptions_str
        assert "установить 25°C" in descriptions_str
        assert "установить влажность 55%" in descriptions_str
        assert "яркость 50%" in descriptions_str
        assert "Запустить" in descriptions_str
        assert "вскипятить" in descriptions_str
        assert "Поставить на охрану" in descriptions_str
        assert "Снять с охраны" in descriptions_str

    def test_execute_actions_all_types(self, capsys):
        """Тест выполнения всех типов действий"""
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
            # Добавляем все необходимые методы
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
        captured = capsys.readouterr()

        assert "Выполняется правило: тест" in captured.out
        devices['1'].turn_on.assert_called_once()
        devices['2'].turn_off.assert_called_once()
        devices['3'].set_temperature.assert_called_with(25)
        devices['4'].set_humidity.assert_called_with(55)
        devices['5'].set_brightness.assert_called_with(50)
        devices['6'].clean.assert_called_once()
        devices['7'].boil.assert_called_once()
        devices['8'].arm.assert_called_once()
        devices['9'].disarm.assert_called_once()

    def test_execute_actions_device_without_method(self, capsys):
        """Тест выполнения действия когда у устройства нет метода"""
        actions = [
            {'device_id': '1', 'type': 'set_humidity', 'humidity': 55},
            {'device_id': '2', 'type': 'set_temperature', 'temperature': 25}
        ]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()

        # Устройство без метода set_humidity
        device1 = Mock()
        device1.name = "Устройство 1"
        del device1.set_humidity

        # Устройство с методом set_temperature
        device2 = Mock()
        device2.name = "Устройство 2"
        device2.set_temperature = Mock()

        def mock_get_device(device_id):
            if device_id == '1':
                return device1
            return device2

        mock_home.get_device.side_effect = mock_get_device

        rule.execute_actions(mock_home)
        captured = capsys.readouterr()

        assert "Выполняется правило: тест" in captured.out
        device2.set_temperature.assert_called_with(25)
        # Проверяем что для device1 не было ошибки
        assert "Ошибка" not in captured.out


# ==================== ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ АВТОМАТИЗАЦИИ (ПОВЫШЕНИЕ ПОКРЫТИЯ) ====================

class TestAutomationRuleCoverage:
    """Тесты для повышения покрытия Automation.py"""

    def setup_method(self):
        self.rule = AutomationRule(
            "тест",
            {'type': 'time', 'time': '12:00'},
            [{'device_id': '123', 'type': 'turn_on'}]
        )

    def test_get_actions_description_all_branches(self):
        """Тест всех веток get_actions_description"""
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
            {'device_id': '10', 'type': 'unknown_type'}  # неизвестный тип
        ]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()

        def mock_get_device(device_id):
            device = Mock()
            device.name = f"Устройство {device_id}"
            device.get_device_type.return_value = "тест"
            return device

        mock_home.get_device.side_effect = mock_get_device

        descriptions = rule.get_actions_description(mock_home)
        assert len(descriptions) == 10

    def test_get_actions_description_device_not_found(self):
        """Тест ветки когда устройство не найдено"""
        actions = [{'device_id': '999', 'type': 'turn_on'}]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        mock_home.get_device.side_effect = Exception("Not found")

        descriptions = rule.get_actions_description(mock_home)
        assert "Действие для устройства 999" in descriptions[0]

    def test_execute_actions_set_humidity_branch(self, capsys):
        """Тест выполнения действия set_humidity"""
        actions = [{'device_id': '1', 'type': 'set_humidity', 'humidity': 55}]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        device = Mock()
        device.name = "Устройство 1"
        device.set_humidity = Mock()
        mock_home.get_device.return_value = device

        rule.execute_actions(mock_home)
        device.set_humidity.assert_called_with(55)

    def test_execute_actions_set_humidity_no_method(self, capsys):
        """Тест выполнения set_humidity когда нет метода"""
        actions = [{'device_id': '1', 'type': 'set_humidity', 'humidity': 55}]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        device = Mock()
        device.name = "Устройство 1"
        del device.set_humidity
        mock_home.get_device.return_value = device

        rule.execute_actions(mock_home)
        captured = capsys.readouterr()
        assert "Выполняется правило: тест" in captured.out

    def test_execute_actions_all_climate_branches(self, capsys):
        """Тест всех веток климат-контроля"""
        actions = [
            {'device_id': '1', 'type': 'set_temperature', 'temperature': 25},
            {'device_id': '2', 'type': 'set_humidity', 'humidity': 55}
        ]
        rule = AutomationRule("тест", {}, actions)

        mock_home = Mock()
        devices = {}
        for i in range(1, 3):
            device = Mock()
            device.name = f"Устройство {i}"
            device.set_temperature = Mock()
            device.set_humidity = Mock()
            devices[str(i)] = device

        mock_home.get_device.side_effect = lambda x: devices[x]

        rule.execute_actions(mock_home)
        devices['1'].set_temperature.assert_called_with(25)
        devices['2'].set_humidity.assert_called_with(55)


# ==================== ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ CLI ====================

class TestSmartHomeCLICoverage:
    """Тесты для повышения покрытия SmartHomeCLI.py"""

    def setup_method(self):
        self.cli = SmartHomeCLI()
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
        self.owner = OwnerDevice("тест айфон")
        self.cli.home.add_owner_device(self.owner)

    def test_get_device_icon(self):
        """Тест get_device_icon (для совместимости)"""
        assert self.cli.get_device_icon(self.light) == ""
        assert self.cli.get_device_icon(self.climate) == ""
        assert self.cli.get_device_icon(self.cleaner) == ""
        assert self.cli.get_device_icon(self.kettle) == ""
        assert self.cli.get_device_icon(self.security) == ""
        assert self.cli.get_device_icon(self.owner) == ""

    def test_control_lights_turn_on_all(self, monkeypatch):
        """Тест включения всего света"""
        self.light.turn_off()
        # В методе control_lights() опция включения всего света = len(lights) + 1
        # Так как у нас 1 лампа, len(lights) + 1 = 2
        option = '2'
        inputs = iter([option])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()
        assert self.light.status is True

    def test_control_lights_turn_off_all(self, monkeypatch):
        """Тест выключения всего света"""
        self.light.turn_on()
        # Выбираем опцию "Выключить ВЕСЬ свет" (len(lights) + 2)
        # Так как у нас 1 лампа, len(lights) + 2 = 3
        option = '3'
        inputs = iter([option])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_lights()
        assert self.light.status is False

    def test_control_climate_set_all_18(self, monkeypatch):
        """Тест установки всем 18°C"""
        self.climate.target_temperature = 25
        # В методе control_climate(): опция "Установить ВСЕМ 18°C" = len(climate) + 1
        # Так как у нас 1 устройство, len(climate) + 1 = 2
        option = '2'
        inputs = iter([option])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_temperature == 18

    def test_control_climate_set_all_24(self, monkeypatch):
        """Тест установки всем 24°C"""
        self.climate.target_temperature = 20
        # Опция "Установить ВСЕМ 24°C" = len(climate) + 2 = 3
        option = '3'
        inputs = iter([option])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_temperature == 24

    def test_control_climate_set_all_humidity_50(self, monkeypatch):
        """Тест установки всем влажности 50%"""
        self.climate.target_humidity = 60
        # Опция "Установить ВСЕМ влажность 50%" = len(climate) + 3 = 4
        option = '4'
        inputs = iter([option])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_climate()
        assert self.climate.target_humidity == 50

    def test_control_cleaner_all_modes(self, monkeypatch):
        """Тест всех режимов пылесоса"""
        # Обычная уборка
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()
        assert self.cleaner.mode == "обычный"

        # Влажная уборка
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()
        assert self.cleaner.mode == "влажная"

        # Остановка
        self.cleaner.clean()
        inputs = iter(['3', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_cleaner()
        assert self.cleaner.status is False

    def test_control_kettle_all_modes(self, monkeypatch):
        """Тест всех режимов чайника"""
        # Кипячение
        self.kettle.temperature = 20
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()
        assert self.kettle.temperature == 100

        # Нагрев до температуры
        inputs = iter(['2', '85', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_kettle()
        assert self.kettle.temperature == 85

    def test_control_security_all_modes(self, monkeypatch):
        """Тест всех режимов сигнализации"""
        # Постановка на охрану
        self.security.armed = False
        inputs = iter(['1', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_security()
        assert self.security.armed is True

        # Снятие с охраны
        inputs = iter(['2', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.control_security()
        assert self.security.armed is False

    def test_quick_commands_all(self, monkeypatch):
        """Тест всех быстрых команд"""
        commands = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        for cmd in commands:
            monkeypatch.setattr('builtins.input', lambda _: cmd)
            self.cli.quick_commands()

    def test_add_automation_rule_with_device_status(self, monkeypatch):
        """Тест добавления правила по статусу устройства"""
        inputs = iter(['тест', '2', self.light.id, 'включено', 'stop'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_add_automation_rule_with_actions(self, monkeypatch):
        """Тест добавления правила с действиями"""
        inputs = iter([
            'тест', '1', '12:00',
            self.light.id, '1',  # включить
            self.climate.id, '3', '24',  # установить температуру
            self.climate.id, '4', '55',  # установить влажность
            'stop'
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.add_automation_rule()

    def test_owner_device_menu_create_with_default_name(self, monkeypatch):
        """Тест создания устройства с именем по умолчанию"""
        self.cli.home.owner_device = None
        inputs = iter(['1', '', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        self.cli.owner_device_menu()
        assert self.cli.home.owner_device is not None
        assert self.cli.home.owner_device.name == "Мобильное устройство хозяина"


# ==================== ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ MAIN ====================

class TestMainCoverage:
    """Тесты для повышения покрытия main.py"""


    @patch('SmartHomeCLI.SmartHomeCLI')
    def test_main_with_exception(self, mock_cli_class):
        """Тест main с исключением"""
        from main import main
        mock_cli = Mock()
        error_msg = "Тестовая ошибка"
        mock_cli.run.side_effect = Exception(error_msg)
        mock_cli_class.return_value = mock_cli

        # Просто проверяем что функция вызывается и не падает
        try:
            main()
        except:
            pytest.fail("main() не должна выбрасывать исключение")


# ==================== ТЕСТЫ ДЛЯ НЕПОКРЫТЫХ СТРОК В DEVICES ====================

class TestDevicesCoverage:
    """Тесты для непокрытых строк в Devices.py"""

    def test_climate_device_temperature_range_attributes(self):
        """Тест атрибутов диапазона температуры"""
        device = ClimateDevice("тест", "room_123")
        device.set_temperature_range(20, 25)
        assert hasattr(device, 'min_temperature')
        assert hasattr(device, 'max_temperature')
        assert device.min_temperature == 20
        assert device.max_temperature == 25

    def test_climate_device_humidity_range_attributes(self):
        """Тест атрибутов диапазона влажности"""
        device = ClimateDevice("тест", "room_123")
        device.set_humidity_range(40, 60)
        assert hasattr(device, 'min_humidity')
        assert hasattr(device, 'max_humidity')
        assert device.min_humidity == 40
        assert device.max_humidity == 60

    def test_climate_device_get_status_with_ranges(self):
        """Тест get_status с диапазонами"""
        device = ClimateDevice("тест", "room_123")
        device.set_temperature_range(20, 25)
        device.set_humidity_range(40, 60)

        status = device.get_status()
        assert 'min_temperature' in status
        assert 'max_temperature' in status
        assert 'min_humidity' in status
        assert 'max_humidity' in status