"""
Простые тесты для умного дома
Запуск: python manage.py test
"""

from django.test import TestCase, Client
import json


class SimplePagesTest(TestCase):
    """Простые тесты для проверки страниц"""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        """Главная страница открывается"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page(self):
        """Страница панели открывается"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_rooms_page(self):
        """Страница комнат открывается"""
        response = self.client.get('/rooms/')
        self.assertEqual(response.status_code, 200)

    def test_security_page(self):
        """Страница безопасности открывается"""
        response = self.client.get('/security/')
        self.assertEqual(response.status_code, 200)

    def test_owner_page(self):
        """Страница хозяина открывается"""
        response = self.client.get('/owner/')
        self.assertEqual(response.status_code, 200)

    def test_automation_page(self):
        """Страница автоматизации открывается"""
        response = self.client.get('/automation/')
        self.assertEqual(response.status_code, 200)

    def test_404_page(self):
        """Несуществующая страница возвращает 404"""
        response = self.client.get('/page-not-found-12345/')
        self.assertEqual(response.status_code, 404)


class SimpleAPITest(TestCase):
    """Простые тесты для API"""

    def setUp(self):
        self.client = Client()

    def test_get_devices_api(self):
        """API получения списка устройств работает"""
        response = self.client.get('/api/devices/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('devices', data)

    def test_add_light_device(self):
        """Добавление лампочки через API"""
        data = {
            'device_type': 'light',
            'name': 'Тест лампа',
            'room_name': 'спальня'
        }
        response = self.client.post(
            '/api/device/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content)
        self.assertTrue(result['success'])

    def test_add_device_empty_name(self):
        """Добавление устройства без названия - ошибка"""
        data = {
            'device_type': 'light',
            'name': '',
            'room_name': 'спальня'
        }
        response = self.client.post(
            '/api/device/',
            data=json.dumps(data),
            content_type='application/json'
        )

        result = json.loads(response.content)
        self.assertFalse(result['success'])

    def test_add_device_invalid_room(self):
        """Добавление в несуществующую комнату - ошибка"""
        data = {
            'device_type': 'light',
            'name': 'Лампа',
            'room_name': 'несущ'
        }
        response = self.client.post(
            '/api/device/',
            data=json.dumps(data),
            content_type='application/json'
        )

        result = json.loads(response.content)
        self.assertFalse(result['success'])

    def test_save_state(self):
        """Сохранение состояния работает"""
        response = self.client.post('/api/save/')
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content)
        self.assertTrue(result['success'])


class SimpleDeviceTest(TestCase):
    """Простые тесты для устройств"""

    def test_light_on_off(self):
        """Включение и выключение лампы"""
        from core.Room import Room
        from core.LightDevice import LightDevice

        room = Room("тест")
        lamp = LightDevice("Лампа", room.id)

        # Изначально выключена
        self.assertFalse(lamp.status)

        # Включаем
        lamp.turn_on()
        self.assertTrue(lamp.status)

        # Выключаем
        lamp.turn_off()
        self.assertFalse(lamp.status)

    def test_light_brightness(self):
        """Установка яркости лампы"""
        from core.Room import Room
        from core.LightDevice import LightDevice

        room = Room("тест")
        lamp = LightDevice("Лампа", room.id)

        lamp.set_brightness(50)
        self.assertEqual(lamp.brightness, 50)

    def test_climate_temperature(self):
        """Установка температуры кондиционера"""
        from core.Room import Room
        from core.ClimateDevice import ClimateDevice

        room = Room("тест")
        climate = ClimateDevice("Кондей", room.id)

        climate.set_temperature(24)
        self.assertEqual(climate.target_temperature, 24)

    def test_climate_humidity(self):
        """Установка влажности"""
        from core.Room import Room
        from core.ClimateDevice import ClimateDevice

        room = Room("тест")
        climate = ClimateDevice("Кондей", room.id)

        climate.set_humidity(55)
        self.assertEqual(climate.target_humidity, 55)

    def test_cleaner(self):
        """Запуск и остановка пылесоса"""
        from core.Room import Room
        from core.SmartCleaner import SmartCleaner

        room = Room("тест")
        cleaner = SmartCleaner("Пылесос", room.id)

        cleaner.clean()
        self.assertTrue(cleaner.status)

        cleaner.stop()
        self.assertFalse(cleaner.status)

    def test_kettle_boil(self):
        """Кипячение чайника"""
        from core.Room import Room
        from core.SmartKettle import SmartKettle

        room = Room("тест")
        kettle = SmartKettle("Чайник", room.id)

        kettle.boil()
        self.assertEqual(kettle.temperature, 100)


class SimpleRoomTest(TestCase):
    """Простые тесты для комнат"""

    def test_add_device_to_room(self):
        """Добавление устройства в комнату"""
        from core.Room import Room
        from core.LightDevice import LightDevice

        room = Room("спальня")
        lamp = LightDevice("Лампа", room.id)

        room.add_device(lamp)
        self.assertIn(lamp.id, room.devices)

    def test_remove_device_from_room(self):
        """Удаление устройства из комнаты"""
        from core.Room import Room
        from core.LightDevice import LightDevice

        room = Room("спальня")
        lamp = LightDevice("Лампа", room.id)

        room.add_device(lamp)
        self.assertIn(lamp.id, room.devices)

        room.remove_device(lamp.id)
        self.assertNotIn(lamp.id, room.devices)


class SimpleSecurityTest(TestCase):
    """Простые тесты для сигнализации"""

    def test_arm_disarm(self):
        """Постановка и снятие с охраны"""
        from core.SecuritySystem import SecuritySystem

        security = SecuritySystem("Сигнализация")

        security.arm()
        self.assertTrue(security.armed)

        security.disarm()
        self.assertFalse(security.armed)

    def test_trigger_alarm(self):
        """Срабатывание тревоги"""
        from core.SecuritySystem import SecuritySystem

        security = SecuritySystem("Сигнализация")

        security.arm()
        security.trigger_alarm()
        self.assertTrue(security.alarm_triggered)


class SimpleAutomationTest(TestCase):
    """Простые тесты для автоматизации"""

    def test_create_rule(self):
        """Создание правила автоматизации"""
        from core.Automation import AutomationRule

        condition = {'type': 'time', 'time': '12:00'}
        actions = [{'device_id': '123', 'type': 'turn_on'}]

        rule = AutomationRule("Тест", condition, actions)

        self.assertEqual(rule.name, "Тест")
        self.assertTrue(rule.enabled)
        self.assertIsNotNone(rule.id)