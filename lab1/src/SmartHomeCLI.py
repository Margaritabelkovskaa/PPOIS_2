"""Интерфейс командной строки с поддержкой сохранения состояния"""

from SmartHome import SmartHome
from Room import Room
from SmartDevice import SmartDevice
from LightDevice import LightDevice
from ClimateDevice import ClimateDevice
from SecuritySystem import SecuritySystem
from SmartCleaner import SmartCleaner
from SmartKettle import SmartKettle
from OwnerDevice import OwnerDevice
from Automation import AutomationRule
from exceptions import SmartHomeError, InvalidValueError, DeviceNotFoundError


class SmartHomeCLI:
    """Интерфейс командной строки"""

    def __init__(self):
        self.home = SmartHome("Мой умный дом")
        self.state_file = "smarthome_state.json"

        # Пытаемся загрузить сохраненное состояние
        try:
            self.home.load_state(self.state_file)
        except Exception as e:
            print(f"Предупреждение: {e}")

        # Если устройство хозяина не загрузилось, создаем по умолчанию
        if not self.home.owner_device:
            self._setup_default_owner()

        print("SmartHomeCLI инициализирован")

    def _setup_default_owner(self) -> None:
        """Установка устройства хозяина по умолчанию"""
        try:
            owner = OwnerDevice("Мобильный телефон хозяина")
            self.home.add_owner_device(owner)
            print("Устройство хозяина настроено")
        except Exception as e:
            print(f"Не удалось настроить устройство хозяина: {e}")

    def run(self) -> None:
        """Запуск основного цикла программы"""
        while True:
            try:
                self.show_menu()
                choice = input("\nВыберите действие: ").strip().lower()

                if choice == '0':
                    self._exit_program()
                    break
                elif choice == '1':
                    self.list_rooms()
                elif choice == '2':
                    self.add_device()
                elif choice == '3':
                    self.list_devices()
                elif choice == '4':
                    self.control_menu()
                elif choice == '5':
                    self.add_automation_rule()
                elif choice == '6':
                    self.list_automation_rules()
                elif choice == '7':
                    self.check_automation()
                elif choice == '8':
                    self.monitor_security()
                elif choice == '9':
                    self.owner_device_menu()
                elif choice == 's':
                    self.home.save_state(self.state_file)
                else:
                    print("Неверный выбор")

            except KeyboardInterrupt:
                print("\nПрограмма прервана пользователем")
                self._exit_program()
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    def _exit_program(self) -> None:
        """Действия при выходе из программы"""
        print("\nСохраняем состояние перед выходом...")
        try:
            self.home.save_state(self.state_file)
            print("До свидания!")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            print("До свидания!")

    def show_menu(self) -> None:
        """Показать главное меню"""
        print(f"\n{'='*40}")
        print(f"   Умный дом: {self.home.name}")
        print(f"{'='*40}")
        print("1. Список комнат")
        print("2. Добавить устройство")
        print("3. Список устройств")
        print("4. Управление устройствами")
        print("5. Добавить правило автоматизации")
        print("6. Список правил")
        print("7. Проверить автоматизацию")
        print("8. Мониторинг безопасности")
        print("9. Мобильное устройство хозяина")
        print("s. Сохранить состояние")
        print("0. Выход (с сохранением)")

    # ==================== МЕТОДЫ УПРАВЛЕНИЯ ====================

    def control_menu(self) -> None:
        """Главное меню управления устройствами"""
        while True:
            print("\n=== УПРАВЛЕНИЕ УСТРОЙСТВАМИ ===")
            print("1. Управление светом")
            print("2. Управление климатом")
            print("3. Управление пылесосом")
            print("4. Управление чайником")
            print("5. Управление сигнализацией")
            print("6. Быстрые команды")
            print("0. Назад")

            choice = input("Выберите: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self.control_lights()
            elif choice == '2':
                self.control_climate()
            elif choice == '3':
                self.control_cleaner()
            elif choice == '4':
                self.control_kettle()
            elif choice == '5':
                self.control_security()
            elif choice == '6':
                self.quick_commands()
            else:
                print("Неверный выбор")

    def control_lights(self) -> None:
        """Управление освещением"""
        print("\n=== УПРАВЛЕНИЕ СВЕТОМ ===")

        # Собираем все лампочки
        lights = []
        for room in self.home.rooms.values():
            for device in room.devices.values():
                if isinstance(device, LightDevice):
                    lights.append((room, device))

        if not lights:
            print("Нет лампочек")
            return

        # Показываем список лампочек
        for i, (room, light) in enumerate(lights, 1):
            status = "включен" if light.status else "выключен"
            print(f"{i}. {status} {light.name} ({room.name}) - яркость {light.brightness}%")

        print(f"\n{len(lights)+1}. Включить ВЕСЬ свет")
        print(f"{len(lights)+2}. Выключить ВЕСЬ свет")
        print("0. Назад")

        choice = input("Выберите: ").strip()
        if not choice.isdigit():
            return

        idx = int(choice)
        if idx == 0:
            return
        elif 1 <= idx <= len(lights):
            room, light = lights[idx-1]
            print("\n1. Вкл/Выкл")
            print("2. Установить яркость")

            action = input("Выберите: ").strip()
            if action == '1':
                if light.status:
                    light.turn_off()
                    print(f"{light.name} выключен")
                else:
                    light.turn_on()
                    print(f"{light.name} включён")
            elif action == '2':
                try:
                    b = int(input("Яркость (0-100): "))
                    light.set_brightness(b)
                    print(f"Яркость {light.name} установлена на {b}%")
                except ValueError:
                    print("Ошибка: введите число")
                except InvalidValueError as e:
                    print(f"Ошибка: {e}")

        elif idx == len(lights) + 1:
            count = 0
            for room, light in lights:
                if not light.status:
                    light.turn_on()
                    count += 1
            print(f"Включено {count} лампочек")

        elif idx == len(lights) + 2:
            count = 0
            for room, light in lights:
                if light.status:
                    light.turn_off()
                    count += 1
            print(f"Выключено {count} лампочек")

    def control_climate(self) -> None:
        """Управление климатом (температура и влажность)"""
        print("\n=== УПРАВЛЕНИЕ КЛИМАТОМ ===")

        climate = []
        for room in self.home.rooms.values():
            for device in room.devices.values():
                if isinstance(device, ClimateDevice):
                    climate.append((room, device))

        if not climate:
            print("Нет климат-устройств")
            return

        for i, (room, clim) in enumerate(climate, 1):
            status = "включен" if clim.status else "выключен"
            print(f"{i}. {status} {clim.name} ({room.name}) - "
                  f"цель {clim.target_temperature}°C, "
                  f"влажность цель {clim.target_humidity}%, "
                  f"режим: {clim.mode}")

        print(f"\n{len(climate)+1}. Установить ВСЕМ 18°C")
        print(f"{len(climate)+2}. Установить ВСЕМ 24°C")
        print(f"{len(climate)+3}. Установить ВСЕМ влажность 50%")
        print("0. Назад")

        choice = input("Выберите: ").strip()
        if not choice.isdigit():
            return

        idx = int(choice)
        if idx == 0:
            return
        elif 1 <= idx <= len(climate):
            room, clim = climate[idx-1]
            self._climate_device_menu(clim)
        elif idx == len(climate) + 1:
            for room, clim in climate:
                clim.set_temperature(18)
            print("Всем установлена 18°C")
        elif idx == len(climate) + 2:
            for room, clim in climate:
                clim.set_temperature(24)
            print("Всем установлена 24°C")
        elif idx == len(climate) + 3:
            for room, clim in climate:
                clim.set_humidity(50)
            print("Всем установлена влажность 50%")

    def _climate_device_menu(self, device: ClimateDevice) -> None:
        """Меню управления конкретным климат-устройством"""
        while True:
            print(f"\n--- {device.name} ---")
            print(f"Температура: текущая {device.temperature}°C, цель {device.target_temperature}°C")
            print(f"Влажность: текущая {device.humidity}%, цель {device.target_humidity}%")
            print(f"Режим: {device.mode}, вентилятор: {device.fan_speed}")
            print("\n1. Вкл/Выкл")
            print("2. Установить температуру")
            print("3. Установить влажность")
            print("4. Увеличить влажность")
            print("5. Уменьшить влажность")
            print("6. Установить режим")
            print("7. Установить скорость вентилятора")
            print("0. Назад")

            choice = input("Выберите: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                if device.status:
                    device.turn_off()
                    print(f"{device.name} выключен")
                else:
                    device.turn_on()
                    print(f"{device.name} включён")
            elif choice == '2':
                try:
                    temp = float(input(f"Температура (16-30) [сейчас {device.target_temperature}°C]: "))
                    device.set_temperature(temp)
                    print(f"Температура установлена на {temp}°C")
                except ValueError:
                    print("Ошибка: введите число")
                except InvalidValueError as e:
                    print(f"Ошибка: {e}")
            elif choice == '3':
                try:
                    hum = float(input(f"Влажность (30-80) [сейчас {device.target_humidity}%]: "))
                    device.set_humidity(hum)
                    print(f"Влажность установлена на {hum}%")
                except ValueError:
                    print("Ошибка: введите число")
                except InvalidValueError as e:
                    print(f"Ошибка: {e}")
            elif choice == '4':
                device.increase_humidity()
            elif choice == '5':
                device.decrease_humidity()
            elif choice == '6':
                print("Доступные режимы: auto, cool, heat, dry, fan_only")
                mode = input("Введите режим: ").strip()
                try:
                    device.set_mode(mode)
                    print(f"Режим установлен: {mode}")
                except InvalidValueError as e:
                    print(f"Ошибка: {e}")
            elif choice == '7':
                print("Доступные скорости: auto, low, medium, high")
                speed = input("Введите скорость: ").strip()
                try:
                    device.set_fan_speed(speed)
                    print(f"Скорость вентилятора установлена: {speed}")
                except InvalidValueError as e:
                    print(f"Ошибка: {e}")

    def control_cleaner(self) -> None:
        """Управление пылесосом"""
        print("\n=== УПРАВЛЕНИЕ ПЫЛЕСОСОМ ===")

        cleaner = None
        cleaner_room = None
        for room in self.home.rooms.values():
            for device in room.devices.values():
                if isinstance(device, SmartCleaner):
                    cleaner = device
                    cleaner_room = room
                    break
            if cleaner:
                break

        if not cleaner:
            print("Нет пылесоса")
            return

        print(f"\n{cleaner.name} ({cleaner_room.name})")
        print(f"Режим: {cleaner.mode}")
        print(f"Статус: {'включен' if cleaner.status else 'выключен'}")

        print("\n1. Обычная уборка")
        print("2. Влажная уборка")
        print("3. Остановить")
        print("0. Назад")

        action = input("Выберите: ").strip()

        if action == '1':
            cleaner.set_mode("обычный")
            cleaner.clean()
        elif action == '2':
            cleaner.set_mode("влажная")
            cleaner.clean()
        elif action == '3':
            cleaner.stop()

    def control_kettle(self) -> None:
        """Управление чайником"""
        print("\n=== УПРАВЛЕНИЕ ЧАЙНИКОМ ===")

        kettle = None
        kettle_room = None
        for room in self.home.rooms.values():
            for device in room.devices.values():
                if isinstance(device, SmartKettle):
                    kettle = device
                    kettle_room = room
                    break
            if kettle:
                break

        if not kettle:
            print("Нет чайника")
            return

        print(f"\n{kettle.name} ({kettle_room.name})")
        print(f"Вода: {kettle.water_level}%")
        print(f"Температура: {kettle.temperature}°C")
        print(f"Статус: {'включен' if kettle.status else 'выключен'}")

        print("\n1. Вскипятить")
        print("2. Нагреть до температуры")
        print("0. Назад")

        action = input("Выберите: ").strip()

        if action == '1':
            kettle.boil()
        elif action == '2':
            try:
                temp = int(input("Температура (40-100): "))
                kettle.set_temperature(temp)
            except ValueError:
                print("Ошибка: введите число")

    def control_security(self) -> None:
        """Управление сигнализацией"""
        print("\n=== УПРАВЛЕНИЕ СИГНАЛИЗАЦИЕЙ ===")

        if not self.home.security_system:
            print("Сигнализация не установлена")
            return

        sec = self.home.security_system
        status = "НА ОХРАНЕ" if sec.armed else "СНЯТО"
        alarm = "ТРЕВОГА!" if sec.alarm_triggered else "Спокойно"

        print(f"\n{sec.name}")
        print(f"   Статус: {status}")
        print(f"   Состояние: {alarm}")

        print("\n1. Поставить на охрану")
        print("2. Снять с охраны")
        print("0. Назад")

        action = input("Выберите: ").strip()

        if action == '1':
            sec.arm()
        elif action == '2':
            sec.disarm()

    def quick_commands(self) -> None:
        """Быстрые команды"""
        print("\n=== БЫСТРЫЕ КОМАНДЫ ===")
        print("1. Включить ВЕСЬ свет")
        print("2. Выключить ВЕСЬ свет")
        print("3. Установить ВСЕМ 18°C")
        print("4. Установить ВСЕМ 24°C")
        print("5. Установить ВСЕМ влажность 50%")
        print("6. Поставить на охрану")
        print("7. Снять с охраны")
        print("8. Запустить пылесос (обычный)")
        print("9. Запустить пылесос (влажный)")
        print("10. Остановить пылесос")
        print("11. Вскипятить чайник")
        print("0. Назад")

        choice = input("Выберите: ").strip()

        if choice == '1':
            count = 0
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, LightDevice) and not d.status:
                        d.turn_on()
                        count += 1
            print(f"Включено {count} лампочек")

        elif choice == '2':
            count = 0
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, LightDevice) and d.status:
                        d.turn_off()
                        count += 1
            print(f"Выключено {count} лампочек")

        elif choice == '3':
            count = 0
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, ClimateDevice):
                        d.set_temperature(18)
                        count += 1
            print(f"Установлено 18°C на {count} устройствах")

        elif choice == '4':
            count = 0
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, ClimateDevice):
                        d.set_temperature(24)
                        count += 1
            print(f"Установлено 24°C на {count} устройствах")

        elif choice == '5':
            count = 0
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, ClimateDevice):
                        d.set_humidity(50)
                        count += 1
            print(f"Установлена влажность 50% на {count} устройствах")

        elif choice == '6':
            if self.home.security_system:
                self.home.security_system.arm()
            else:
                print("Сигнализация не установлена")

        elif choice == '7':
            if self.home.security_system:
                self.home.security_system.disarm()
            else:
                print("Сигнализация не установлена")

        elif choice == '8':
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, SmartCleaner):
                        d.set_mode("обычный")
                        d.clean()
                        return
            print("Пылесос не найден")

        elif choice == '9':
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, SmartCleaner):
                        d.set_mode("влажная")
                        d.clean()
                        return
            print("Пылесос не найден")

        elif choice == '10':
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, SmartCleaner):
                        d.stop()
                        return
            print("Пылесос не найден")

        elif choice == '11':
            for room in self.home.rooms.values():
                for d in room.devices.values():
                    if isinstance(d, SmartKettle):
                        d.boil()
                        return
            print("Чайник не найден")

    # ==================== МЕТОДЫ ДЛЯ КОМНАТ И УСТРОЙСТВ ====================

    def list_rooms(self) -> None:
        """Список комнат"""
        print("\n=== КОМНАТЫ (фиксированный список) ===")
        if not self.home.rooms:
            print("Нет комнат")
            return

        for room in self.home.rooms.values():
            devices_count = len(room.devices)
            print(f"Комната: {room.name}")
            print(f"   ID: {room.id}")
            print(f"   Устройств: {devices_count}")
            if devices_count > 0:
                print("   Устройства:")
                for device in room.devices.values():
                    print(f"     - {device.name} ({device.get_device_type()})")

    def add_device(self) -> None:
        """Добавление устройства"""
        print("\n=== ТИПЫ УСТРОЙСТВ ===")
        print("1. Освещение")
        print("2. Климат-контроль")
        print("3. Пылесос")
        print("4. Чайник")
        print("5. Сигнализация (на весь дом)")

        type_choice = input("Выберите тип: ").strip()
        name = input("Введите название устройства: ").strip()

        if not name:
            raise InvalidValueError("Название не может быть пустым")

        if type_choice == '5':
            if self.home.security_system:
                print("Сигнализация уже установлена")
                return
            device = SecuritySystem(name)
            self.home.add_security_system(device)
            print(f"Сигнализация '{name}' установлена")
            return

        # Показываем список доступных комнат
        print("\nДоступные комнаты:")
        rooms_list = list(self.home.rooms.values())
        for i, room in enumerate(rooms_list, 1):
            print(f"{i}. {room.name}")

        try:
            room_choice = int(input("Выберите номер комнаты: ")) - 1
            if 0 <= room_choice < len(rooms_list):
                room = rooms_list[room_choice]
            else:
                print("Неверный выбор комнаты")
                return
        except ValueError:
            print("Ошибка: введите число")
            return

        device = None
        if type_choice == '1':
            device = LightDevice(name, room.id)
        elif type_choice == '2':
            device = ClimateDevice(name, room.id)
        elif type_choice == '3':
            device = SmartCleaner(name, room.id)
        elif type_choice == '4':
            device = SmartKettle(name, room.id)
        else:
            print("Неверный тип")
            return

        room.add_device(device)
        print(f"Устройство '{name}' добавлено в комнату '{room.name}'")
        print(f"   ID устройства: {device.id}")

    def list_devices(self) -> None:
        """Список всех устройств"""
        print("\n=== ВСЕ УСТРОЙСТВА ===")

        # Сигнализация
        if self.home.security_system:
            sec = self.home.security_system
            status = "НА ОХРАНЕ" if sec.armed else "СНЯТО"
            print(f"\nСИГНАЛИЗАЦИЯ:")
            print(f"   {sec.name} - {status}")
            print(f"   ID: {sec.id}")

        # Устройство хозяина
        if self.home.owner_device:
            owner = self.home.owner_device
            status = "подключен" if owner.connected else "отключен"
            print(f"\nУСТРОЙСТВО ХОЗЯИНА:")
            print(f"   {owner.name} - {status}")
            print(f"   ID: {owner.id}")

        # Устройства в комнатах
        devices_found = False
        for room in self.home.rooms.values():
            if room.devices:
                devices_found = True
                print(f"\nКомната: {room.name}")
                for device in room.devices.values():
                    status = device.get_status()
                    print(f"   {device.name} - {status['status']}")
                    if isinstance(device, ClimateDevice):
                        print(f"      Температура: {device.temperature}°C, цель: {device.target_temperature}°C")
                        print(f"      Влажность: {device.humidity}%, цель: {device.target_humidity}%")
                    elif isinstance(device, LightDevice):
                        print(f"      Яркость: {device.brightness}%")
                    elif isinstance(device, SmartKettle):
                        print(f"      Вода: {device.water_level}%, температура: {device.temperature}°C")
                    elif isinstance(device, SmartCleaner):
                        print(f"      Режим: {device.mode}")
                    print(f"      ID: {device.id}")

        if not devices_found and not self.home.security_system and not self.home.owner_device:
            print("Нет устройств")

    # ==================== МЕТОДЫ ДЛЯ АВТОМАТИЗАЦИИ ====================

    def add_automation_rule(self) -> None:
        """Добавление правила автоматизации"""
        name = input("Введите название правила: ").strip()

        print("\n=== ТИП УСЛОВИЯ ===")
        print("1. По времени")
        print("2. По статусу устройства")

        condition_type = input("Выберите: ").strip()
        condition = {}

        if condition_type == '1':
            time_str = input("Время (ЧЧ:ММ): ").strip()
            condition = {'type': 'time', 'time': time_str}
            print(f"Условие: Время {time_str}")
        elif condition_type == '2':
            # Показываем список устройств для выбора
            self.list_devices_short()
            device_id = input("ID устройства: ").strip()
            status = input("Статус (включено/выключено): ").strip()
            condition = {'type': 'device_status', 'device_id': device_id, 'status': status}

            try:
                device = self.home.get_device(device_id)
                print(f"Условие: {device.name} -> {status}")
            except:
                print(f"Условие: устройство {device_id} -> {status}")
        else:
            print("Неверный тип")
            return

        print("\n=== ДОБАВЛЕНИЕ ДЕЙСТВИЙ (stop - завершить) ===")
        actions = []
        while True:
            print("\nСписок устройств:")
            self.list_devices_short()

            device_id = input("\nID устройства для действия (или 'stop' для завершения): ").strip()
            if device_id.lower() == 'stop':
                break

            try:
                device = self.home.get_device(device_id)
            except DeviceNotFoundError:
                print("Устройство не найдено")
                continue

            print(f"\nУстройство: {device.name} ({self.get_device_type_name(device)})")
            print("Доступные действия:")

            available_actions = self.get_available_actions(device)
            for key, desc in available_actions.items():
                print(f"  {key}. {desc}")

            action_choice = input("Выберите действие: ").strip()

            # Создаем действие на основе выбора
            action = {'device_id': device_id}

            if action_choice == '1':
                action['type'] = 'turn_on'
            elif action_choice == '2':
                action['type'] = 'turn_off'
            elif action_choice == '3' and 'температуру' in str(available_actions):
                action['type'] = 'set_temperature'
                try:
                    action['temperature'] = float(input("Температура: "))
                except ValueError:
                    print("Ошибка: введите число")
                    continue
            elif action_choice == '4' and 'влажность' in str(available_actions):
                action['type'] = 'set_humidity'
                try:
                    action['humidity'] = float(input("Влажность (30-80): "))
                except ValueError:
                    print("Ошибка: введите число")
                    continue
            elif action_choice == '5' and 'яркость' in str(available_actions):
                action['type'] = 'set_brightness'
                try:
                    action['brightness'] = int(input("Яркость (0-100): "))
                except ValueError:
                    print("Ошибка: введите число")
                    continue
            elif action_choice == '6' and 'уборку' in str(available_actions):
                action['type'] = 'start_cleaning'
            elif action_choice == '7' and 'вскипятить' in str(available_actions):
                action['type'] = 'boil'
            elif action_choice == '8' and 'охрану' in str(available_actions):
                action['type'] = 'arm_alarm'
            elif action_choice == '9' and 'охраны' in str(available_actions):
                action['type'] = 'disarm_alarm'
            else:
                print("Неверный выбор действия")
                continue

            actions.append(action)
            print(f"Действие добавлено для {device.name}")

        if condition and actions:
            rule = AutomationRule(name, condition, actions)
            self.home.add_automation_rule(rule)
            print(f"Правило '{name}' добавлено")

            print("\nДЕТАЛИ ПРАВИЛА:")
            print(f"Условие: {rule.get_condition_description(self.home)}")
            print("Действия:")
            for desc in rule.get_actions_description(self.home):
                print(f"  {desc}")

    def list_devices_short(self) -> None:
        """Краткий список устройств (только ID и название)"""
        print("\n--- Доступные устройства ---")

        # Сигнализация
        if self.home.security_system:
            sec = self.home.security_system
            print(f"  • {sec.id} - {sec.name} (сигнализация)")

        # Устройство хозяина
        if self.home.owner_device:
            owner = self.home.owner_device
            print(f"  • {owner.id} - {owner.name} (мобильное устройство)")

        # Устройства в комнатах
        for room in self.home.rooms.values():
            for device in room.devices.values():
                type_name = self.get_device_type_name(device)
                print(f"  • {device.id} - {device.name} ({type_name} в {room.name})")

    def get_device_icon(self, device) -> str:
        """Получить иконку для типа устройства (заглушка для совместимости)"""
        return ""

    def get_device_type_name(self, device) -> str:
        """Получить русское название типа устройства"""
        if isinstance(device, LightDevice):
            return "освещение"
        elif isinstance(device, ClimateDevice):
            return "климат-контроль"
        elif isinstance(device, SmartCleaner):
            return "пылесос"
        elif isinstance(device, SmartKettle):
            return "чайник"
        elif isinstance(device, SecuritySystem):
            return "сигнализация"
        elif isinstance(device, OwnerDevice):
            return "мобильное устройство"
        else:
            return "неизвестное устройство"

    def get_available_actions(self, device) -> dict:
        """Получить словарь доступных действий для устройства"""
        actions = {
            '1': "Включить",
            '2': "Выключить"
        }

        if isinstance(device, LightDevice):
            actions['5'] = "Установить яркость"
        elif isinstance(device, ClimateDevice):
            actions['3'] = "Установить температуру"
            actions['4'] = "Установить влажность"
        elif isinstance(device, SmartCleaner):
            actions['6'] = "Начать уборку"
        elif isinstance(device, SmartKettle):
            actions['3'] = "Установить температуру"
            actions['7'] = "Вскипятить"
        elif isinstance(device, SecuritySystem):
            actions['8'] = "Поставить на охрану"
            actions['9'] = "Снять с охраны"

        return actions

    def list_automation_rules(self) -> None:
        """Список правил автоматизации"""
        print("\n=== ПРАВИЛА АВТОМАТИЗАЦИИ ===")
        if not self.home.automation_rules:
            print("Нет правил")
            return

        for rule in self.home.automation_rules.values():
            print(f"\nПравило: {rule.name}")
            print(f"   ID: {rule.id}")
            print(f"   Условие: {rule.get_condition_description(self.home)}")
            print("   Действия:")
            for desc in rule.get_actions_description(self.home):
                print(f"     {desc}")
            print(f"   Активно: {'да' if rule.enabled else 'нет'}")
            print(f"   Создано: {rule.created_at.strftime('%d.%m.%Y %H:%M')}")

    def check_automation(self) -> None:
        """Проверка правил автоматизации"""
        print("Проверка правил автоматизации...")
        self.home.check_automation_rules()
        print("Проверка завершена")

    def monitor_security(self) -> None:
        """Мониторинг безопасности"""
        print("\n=== УПРАВЛЕНИЕ СИГНАЛИЗАЦИЕЙ ===")

        if not self.home.security_system:
            print("Сигнализация не установлена")
            return

        sec = self.home.security_system
        status = "НА ОХРАНЕ" if sec.armed else "СНЯТО"
        alarm = "ТРЕВОГА!" if sec.alarm_triggered else "Спокойно"

        print(f"\n{sec.name}")
        print(f"   Статус: {status}")
        print(f"   Состояние: {alarm}")

        print("\n1. Поставить на охрану")
        print("2. Снять с охраны")
        print("3. ИМИТИРОВАТЬ ТРЕВОГУ")  # <<< ДОБАВЬ ЭТО
        print("0. Назад")

        action = input("Выберите: ").strip()

        if action == '1':
            sec.arm()
        elif action == '2':
            sec.disarm()
        elif action == '3':  # <<< ДОБАВЬ ЭТО
            sec.trigger_alarm()  # <<< ВЫЗЫВАЕМ ТРЕВОГУ
            print(" ТРЕВОГА СРАБОТАЛА!")
    # ==================== МЕТОДЫ ДЛЯ УСТРОЙСТВА ХОЗЯИНА ====================

    def owner_device_menu(self) -> None:
        """Меню управления устройством хозяина"""
        while True:
            print("\n=== МОБИЛЬНОЕ УСТРОЙСТВО ХОЗЯИНА ===")

            # Проверяем наличие устройства
            if not self.home.owner_device:
                print("КРИТИЧЕСКАЯ ОШИБКА: Устройство хозяина не найдено!")
                print("Перезапустите программу")
                break

            # Устройство есть - показываем меню
            status = self.home.owner_device.get_status()
            print(f"Устройство: {status['name']}")
            print(f"Статус: {'подключен' if status['connected'] == 'да' else 'отключен'}")

            print("\n1. Подключиться к системе")
            print("2. Отключиться от системы")
            print("3. Отправить уведомление")
            print("4. Показать статус")
            print("0. Назад")

            choice = input("Выберите: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self.home.owner_device.connect()
            elif choice == '2':
                self.home.owner_device.disconnect()
            elif choice == '3':
                msg = input("Введите сообщение: ").strip()
                if msg:
                    self.home.owner_device.send_notification(msg)
                else:
                    print("Сообщение не может быть пустым")
            elif choice == '4':
                status = self.home.owner_device.get_status()
                for key, value in status.items():
                    print(f"  {key}: {value}")