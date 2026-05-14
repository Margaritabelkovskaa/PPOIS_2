"""Правила автоматизации"""

import uuid
from datetime import datetime

class AutomationRule:
    """Правило автоматизации"""

    def __init__(self, name: str, condition: dict, actions: list):
        self.id = str(uuid.uuid4())
        self.name = name
        self.condition = condition
        self.actions = actions
        self.enabled = True
        self.created_at = datetime.now()

    def check_condition(self, home_state: dict) -> bool:
        condition_type = self.condition.get('type')

        if condition_type == 'time':
            current_time = datetime.now().time()
            target_time = datetime.strptime(self.condition['time'], '%H:%M').time()
            return current_time >= target_time

        elif condition_type == 'device_status':
            device_id = self.condition['device_id']
            expected_status = self.condition['status']

            for room in home_state.get('rooms', {}).values():
                if device_id in room.get('devices', {}):
                    device = room['devices'][device_id]
                    current_status = 'включено' if device.get('status') else 'выключено'
                    return current_status == expected_status

        return False

    def get_condition_description(self, home) -> str:
        """Получить читаемое описание условия"""
        condition_type = self.condition.get('type')

        if condition_type == 'time':
            return f"Время: {self.condition['time']}"

        elif condition_type == 'device_status':
            device_id = self.condition['device_id']
            expected = self.condition['status']

            try:
                device = home.get_device(device_id)
                device_name = f"{device.name} ({device.get_device_type()})"
                return f"Устройство: {device_name} -> статус: {expected}"
            except:
                return f"Устройство ID: {device_id} -> статус: {expected}"

        return "Неизвестное условие"

    def get_actions_description(self, home) -> list:
        """Получить читаемое описание действий"""
        descriptions = []

        for action in self.actions:
            try:
                device = home.get_device(action['device_id'])
                device_name = f"{device.name} ({device.get_device_type()})"

                action_type = action.get('type')
                if action_type == 'turn_on':
                    descriptions.append(f"Включить {device_name}")
                elif action_type == 'turn_off':
                    descriptions.append(f"Выключить {device_name}")
                elif action_type == 'set_temperature':
                    descriptions.append(f"{device_name} установить {action['temperature']}°C")
                elif action_type == 'set_humidity':
                    descriptions.append(f"{device_name} установить влажность {action['humidity']}%")
                elif action_type == 'set_brightness':
                    descriptions.append(f"{device_name} яркость {action['brightness']}%")
                elif action_type == 'start_cleaning':
                    descriptions.append(f"Запустить {device_name}")
                elif action_type == 'boil':
                    descriptions.append(f"{device_name} вскипятить")
                elif action_type == 'arm_alarm':
                    descriptions.append(f"Поставить на охрану {device_name}")
                elif action_type == 'disarm_alarm':
                    descriptions.append(f"Снять с охраны {device_name}")
                else:
                    descriptions.append(f"{device_name}: {action_type}")
            except:
                descriptions.append(f"Действие для устройства {action['device_id']}")

        return descriptions

    def execute_actions(self, home) -> None:
        if not self.enabled:
            return

        print(f"\nВыполняется правило: {self.name}")
        for action in self.actions:
            try:
                action_type = action.get('type')
                device = home.get_device(action['device_id'])

                if action_type == 'turn_on':
                    device.turn_on()
                    print(f"  {device.name} включен")
                elif action_type == 'turn_off':
                    device.turn_off()
                    print(f"  {device.name} выключен")
                elif action_type == 'set_temperature':
                    if hasattr(device, 'set_temperature'):
                        device.set_temperature(action['temperature'])
                        print(f"  {device.name} температура {action['temperature']}°C")
                elif action_type == 'set_humidity':
                    if hasattr(device, 'set_humidity'):
                        device.set_humidity(action['humidity'])
                        print(f"  {device.name} влажность {action['humidity']}%")
                elif action_type == 'set_brightness':
                    if hasattr(device, 'set_brightness'):
                        device.set_brightness(action['brightness'])
                        print(f"  {device.name} яркость {action['brightness']}%")
                elif action_type == 'start_cleaning':
                    if hasattr(device, 'clean'):
                        device.clean()
                        print(f"  {device.name} начал уборку")
                elif action_type == 'boil':
                    if hasattr(device, 'boil'):
                        device.boil()
                        print(f"  {device.name} кипятит")
                elif action_type == 'arm_alarm':
                    if hasattr(device, 'arm'):
                        device.arm()
                        print(f"  {device.name} на охране")
                elif action_type == 'disarm_alarm':
                    if hasattr(device, 'disarm'):
                        device.disarm()
                        print(f"  {device.name} снят с охраны")

            except Exception as e:
                print(f"  Ошибка: {e}")