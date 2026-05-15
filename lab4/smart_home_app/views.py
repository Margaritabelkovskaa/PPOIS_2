from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from datetime import datetime

from core.SmartHome import SmartHome
from core.LightDevice import LightDevice
from core.ClimateDevice import ClimateDevice
from core.SmartCleaner import SmartCleaner
from core.SmartKettle import SmartKettle
from core.SecuritySystem import SecuritySystem
from core.Room import Room
from core.OwnerDevice import OwnerDevice
from core.Automation import AutomationRule

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
home = SmartHome("Умный дом")

# Путь к файлу сохранения
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(BASE_DIR, 'smarthome_state.json')

# История сообщений
owner_messages = []


def _create_demo_data():
    """Создание демо-устройств со всеми параметрами"""
    print("Создаем демо-устройства...")

    for room in home.rooms.values():
        if room.name == "спальня" and len(room.devices) == 0:
            light = LightDevice("Люстра", room.id)
            light.set_brightness(100)
            light.turn_on()
            room.add_device(light)
            print(f"  + Люстра в спальне (яркость 100%, включена)")

        elif room.name == "гостиная" and len(room.devices) == 0:
            climate = ClimateDevice("Кондиционер", room.id)
            climate.set_temperature(22)
            climate.set_humidity(50)
            climate.set_mode("auto")
            climate.set_fan_speed("medium")
            climate.turn_on()
            room.add_device(climate)
            print(f"  + Кондиционер в гостиной (22°C, 50%, режим auto)")

            cleaner = SmartCleaner("Робот-пылесос", room.id)
            cleaner.set_mode("обычный")
            room.add_device(cleaner)
            print(f"  + Пылесос в гостиной (режим обычный)")

        elif room.name == "кухня" and len(room.devices) == 0:
            kettle = SmartKettle("Электрический чайник", room.id)
            room.add_device(kettle)
            print(f"  + Чайник на кухне")

            light = LightDevice("Свет на кухне", room.id)
            light.set_brightness(75)
            room.add_device(light)
            print(f"  + Свет на кухне (яркость 75%)")

        elif room.name == "детская" and len(room.devices) == 0:
            light = LightDevice("Ночник", room.id)
            light.set_brightness(30)
            room.add_device(light)
            print(f"  + Ночник в детской (яркость 30%)")

            climate = ClimateDevice("Обогреватель", room.id)
            climate.set_temperature(24)
            climate.set_mode("heat")
            room.add_device(climate)
            print(f"  + Обогреватель в детской (24°C, режим обогрев)")

        elif room.name == "ванная" and len(room.devices) == 0:
            climate = ClimateDevice("Вентиляция", room.id)
            climate.set_mode("dry")
            climate.set_fan_speed("high")
            room.add_device(climate)
            print(f"  + Вентиляция в ванной (режим осушение)")

        elif room.name == "коридор" and len(room.devices) == 0:
            light = LightDevice("Свет в коридоре", room.id)
            light.set_brightness(50)
            room.add_device(light)
            print(f"  + Свет в коридоре (яркость 50%)")

    if not home.security_system:
        security = SecuritySystem("Охранная сигнализация")
        home.add_security_system(security)
        print(f"  + Сигнализация")

    if not home.owner_device:
        owner = OwnerDevice("Мобильный телефон хозяина")
        home.add_owner_device(owner)
        owner.connect()
        print(f"  + Устройство хозяина")

    try:
        home.save_state(STATE_FILE)
        print(f"✓ Состояние сохранено")
    except Exception as e:
        print(f"✗ Ошибка сохранения: {e}")


# Загрузка состояния
print("\n" + "=" * 50)
print("ЗАГРУЗКА УМНОГО ДОМА")
print("=" * 50)

if os.path.exists(STATE_FILE):
    try:
        home.load_state(STATE_FILE)
        print(f" Загружено из {STATE_FILE}")
    except Exception as e:
        print(f"✗ Ошибка загрузки: {e}")
        _create_demo_data()
else:
    print("Файл не найден, создаем демо-данные")
    _create_demo_data()

print(f"\nКОМНАТ: {len(home.rooms)}")
for room in home.rooms.values():
    print(f"{room.name}: {len(room.devices)} устройств")
    for device in room.devices.values():
        if isinstance(device, LightDevice):
            print(f"      💡 {device.name}: яркость {device.brightness}%, {'вкл' if device.status else 'выкл'}")
        elif isinstance(device, ClimateDevice):
            print(
                f"      🌡️ {device.name}: {device.target_temperature}°C, {device.target_humidity}%, режим {device.mode}")
        elif isinstance(device, SmartCleaner):
            print(f"      🤖 {device.name}: режим {device.mode}")
        elif isinstance(device, SmartKettle):
            print(f"      🍵 {device.name}: вода {device.water_level}%, {device.temperature}°C")
print("=" * 50 + "\n")


# ========== VIEWS ==========

def index(request):
    return render(request, 'smart_home/index.html', {
        'home': home,
        'rooms_count': len(home.rooms),
        'devices_count': sum(len(room.devices) for room in home.rooms.values())
    })


def dashboard(request):
    devices = []
    for room in home.rooms.values():
        for device in room.devices.values():
            device_data = {
                'id': device.id,
                'name': device.name,
                'type': device.get_device_type(),
                'room': room.name,
                'status': device.status
            }

            if isinstance(device, LightDevice):
                device_data['brightness'] = device.brightness
            elif isinstance(device, ClimateDevice):
                device_data['temperature'] = device.temperature
                device_data['target_temperature'] = device.target_temperature
                device_data['humidity'] = device.humidity
                device_data['target_humidity'] = device.target_humidity
                device_data['mode'] = device.mode
                device_data['fan_speed'] = device.fan_speed
            elif isinstance(device, SmartCleaner):
                device_data['mode'] = device.mode
            elif isinstance(device, SmartKettle):
                device_data['water_level'] = device.water_level
                device_data['temperature'] = device.temperature
                device_data['boiling'] = device.boiling

            devices.append(device_data)

    return render(request, 'smart_home/dashboard.html', {
        'home': home,
        'devices': devices
    })


def rooms(request):
    rooms_data = []
    for room in home.rooms.values():
        devices_data = []
        for device in room.devices.values():
            device_data = {
                'id': device.id,
                'name': device.name,
                'type': device.get_device_type(),
                'status': device.status
            }
            if isinstance(device, LightDevice):
                device_data['brightness'] = device.brightness
            elif isinstance(device, ClimateDevice):
                device_data['target_temperature'] = device.target_temperature
                device_data['target_humidity'] = device.target_humidity
                device_data['mode'] = device.mode
            devices_data.append(device_data)

        rooms_data.append({
            'id': room.id,
            'name': room.name,
            'devices_count': len(room.devices),
            'devices': devices_data
        })
    return render(request, 'smart_home/rooms.html', {'rooms': rooms_data})


def devices(request):
    devices_list = []
    for room in home.rooms.values():
        for device in room.devices.values():
            device_data = {
                'id': device.id,
                'name': device.name,
                'type': device.get_device_type(),
                'room': room.name,
                'status': device.status
            }
            if isinstance(device, LightDevice):
                device_data['brightness'] = device.brightness
            elif isinstance(device, ClimateDevice):
                device_data['target_temperature'] = device.target_temperature
                device_data['target_humidity'] = device.target_humidity
                device_data['mode'] = device.mode
            devices_list.append(device_data)
    return render(request, 'smart_home/devices.html', {'devices': devices_list})


def security(request):
    return render(request, 'smart_home/security.html', {
        'security': home.security_system,
        'armed': home.security_system.armed if home.security_system else False,
        'alarm': home.security_system.alarm_triggered if home.security_system else False
    })


def owner(request):
    global owner_messages
    return render(request, 'smart_home/owner.html', {
        'owner': home.owner_device,
        'messages': owner_messages
    })


def automation(request):
    rules = []
    for rule in home.automation_rules.values():
        rules.append({
            'id': rule.id,
            'name': rule.name,
            'condition_desc': rule.get_condition_description(home),
            'actions_desc': rule.get_actions_description(home),
            'enabled': rule.enabled
        })
    return render(request, 'smart_home/automation.html', {
        'home': home,
        'rules': rules
    })


# ========== API ENDPOINTS ==========

@csrf_exempt
@require_http_methods(["POST"])
def api_add_device(request):
    try:
        data = json.loads(request.body)
        device_type = data.get('device_type')
        name = data.get('name')
        room_name = data.get('room_name')

        if not name:
            return JsonResponse({'success': False, 'error': 'Введите название'})

        room = None
        for r in home.rooms.values():
            if r.name == room_name:
                room = r
                break

        if not room:
            return JsonResponse({'success': False, 'error': 'Комната не найдена'})

        if device_type == 'light':
            device = LightDevice(name, room.id)
        elif device_type == 'climate':
            device = ClimateDevice(name, room.id)
        elif device_type == 'cleaner':
            device = SmartCleaner(name, room.id)
        elif device_type == 'kettle':
            device = SmartKettle(name, room.id)
        else:
            return JsonResponse({'success': False, 'error': 'Неизвестный тип'})

        room.add_device(device)
        home.save_state(STATE_FILE)
        return JsonResponse({'success': True, 'message': f'Устройство "{name}" добавлено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_toggle_device(request, device_id):
    try:
        device = home.get_device(device_id)
        if device:
            if device.status:
                device.turn_off()
            else:
                device.turn_on()
            home.save_state(STATE_FILE)
            home.check_automation_rules()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не найдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_device(request, device_id):
    try:
        for room in home.rooms.values():
            if device_id in room.devices:
                room.remove_device(device_id)
                home.save_state(STATE_FILE)
                return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не найдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== УПРАВЛЕНИЕ ОСВЕЩЕНИЕМ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_set_brightness(request, device_id):
    try:
        data = json.loads(request.body)
        brightness = data.get('brightness')
        device = home.get_device(device_id)
        if hasattr(device, 'set_brightness'):
            device.set_brightness(brightness)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не поддерживает яркость'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== УПРАВЛЕНИЕ КЛИМАТОМ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_set_temperature(request, device_id):
    try:
        data = json.loads(request.body)
        temperature = data.get('temperature')
        device = home.get_device(device_id)
        if hasattr(device, 'set_temperature'):
            device.set_temperature(temperature)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не поддерживает температуру'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_set_humidity(request, device_id):
    try:
        data = json.loads(request.body)
        humidity = data.get('humidity')
        device = home.get_device(device_id)
        if hasattr(device, 'set_humidity'):
            device.set_humidity(humidity)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не поддерживает влажность'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_set_mode(request, device_id):
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        device = home.get_device(device_id)
        if hasattr(device, 'set_mode'):
            device.set_mode(mode)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        elif hasattr(device, 'mode'):
            device.mode = mode
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не поддерживает режимы'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_set_fan_speed(request, device_id):
    try:
        data = json.loads(request.body)
        fan_speed = data.get('fan_speed')
        device = home.get_device(device_id)
        if hasattr(device, 'set_fan_speed'):
            device.set_fan_speed(fan_speed)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не поддерживает скорость вентилятора'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== УПРАВЛЕНИЕ ЧАЙНИКОМ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_boil_kettle(request, device_id):
    try:
        device = home.get_device(device_id)
        if hasattr(device, 'boil'):
            device.boil()
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не чайник'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_set_kettle_temperature(request, device_id):
    try:
        data = json.loads(request.body)
        temperature = data.get('temperature')
        device = home.get_device(device_id)
        if hasattr(device, 'set_temperature'):
            device.set_temperature(temperature)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не чайник'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== УПРАВЛЕНИЕ ПЫЛЕСОСОМ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_start_cleaning(request, device_id):
    try:
        device = home.get_device(device_id)
        if hasattr(device, 'clean'):
            device.clean()
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не пылесос'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_stop_cleaning(request, device_id):
    try:
        device = home.get_device(device_id)
        if hasattr(device, 'stop'):
            device.stop()
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не пылесос'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_set_cleaner_mode(request, device_id):
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        device = home.get_device(device_id)
        if hasattr(device, 'set_mode'):
            device.set_mode(mode)
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Устройство не пылесос'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== БЕЗОПАСНОСТЬ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_arm_security(request):
    try:
        if home.security_system:
            home.security_system.arm()
            home.save_state(STATE_FILE)
            if home.owner_device and home.owner_device.connected:
                home.owner_device.send_notification(" Сигнализация поставлена на охрану")
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет сигнализации'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_disarm_security(request):
    try:
        if home.security_system:
            home.security_system.disarm()
            home.save_state(STATE_FILE)
            if home.owner_device and home.owner_device.connected:
                home.owner_device.send_notification(" Сигнализация снята с охраны")
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет сигнализации'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_trigger_alarm(request):
    try:
        if home.security_system:
            home.security_system.trigger_alarm()
            home.save_state(STATE_FILE)
            if home.security_system.alarm_triggered and home.owner_device and home.owner_device.connected:
                home.owner_device.send_notification("🚨 ТРЕВОГА! Сработала сигнализация!")
                global owner_messages
                owner_messages.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'message': " ТРЕВОГА! Сработала сигнализация!"
                })
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет сигнализации'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== УСТРОЙСТВО ХОЗЯИНА ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_owner_connect(request):
    try:
        if home.owner_device:
            home.owner_device.connect()
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет устройства'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_owner_disconnect(request):
    try:
        if home.owner_device:
            home.owner_device.disconnect()
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет устройства'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_owner_notify(request):
    global owner_messages
    try:
        data = json.loads(request.body)
        message = data.get('message', '')

        if home.owner_device:
            home.owner_device.send_notification(message)
            owner_messages.append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'message': message
            })
            if len(owner_messages) > 50:
                owner_messages = owner_messages[-50:]
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Нет устройства'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== АВТОМАТИЗАЦИЯ ==========
@csrf_exempt
@require_http_methods(["POST"])
def api_add_automation(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        condition = data.get('condition')
        actions = data.get('actions')

        if not name:
            return JsonResponse({'success': False, 'error': 'Введите название'})

        rule = AutomationRule(name, condition, actions)
        home.add_automation_rule(rule)
        home.save_state(STATE_FILE)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_toggle_automation(request, rule_id):
    try:
        if rule_id in home.automation_rules:
            home.automation_rules[rule_id].enabled = not home.automation_rules[rule_id].enabled
            home.save_state(STATE_FILE)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Правило не найдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_delete_automation(request, rule_id):
    try:
        home.remove_automation_rule(rule_id)
        home.save_state(STATE_FILE)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def api_get_devices(request):
    devices_list = []
    for room in home.rooms.values():
        for device in room.devices.values():
            devices_list.append({
                'id': device.id,
                'name': device.name,
                'type': device.get_device_type(),
                'room': room.name
            })
    return JsonResponse({'success': True, 'devices': devices_list})
@csrf_exempt
@require_http_methods(["POST"])
def api_clear_history(request):
    """Очистка истории сообщений"""
    global owner_messages
    try:
        owner_messages = []
        home.save_state(STATE_FILE)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})