"""
Работа с базой данных SQLite
"""
import sqlite3
from datetime import date
from typing import List, Optional
from .player import Player


class Database:
    """Класс для работы с базой данных"""

    def __init__(self, db_path="football_players.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Создание таблицы, если её нет"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    team TEXT NOT NULL,
                    hometown TEXT NOT NULL,
                    is_starter INTEGER NOT NULL,
                    position TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_player(self, player: Player) -> int:
        """Добавление нового игрока"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO players (full_name, birth_date, team, hometown, is_starter, position)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                player.full_name.strip(),
                player.birth_date.isoformat(),
                player.team.strip(),
                player.hometown.strip(),
                1 if player.is_starter else 0,
                player.position
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_players(self) -> List[Player]:
        """Получение всех игроков"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players ORDER BY full_name')
            rows = cursor.fetchall()

            players = []
            for row in rows:
                players.append(Player(
                    id=row[0],
                    full_name=row[1],
                    birth_date=date.fromisoformat(row[2]),
                    team=row[3],
                    hometown=row[4],
                    is_starter=bool(row[5]),
                    position=row[6]
                ))
            return players

    def search_players(self, name_part: str = "", birth_date: Optional[date] = None,
                       position: str = "", is_starter: Optional[bool] = None,
                       team: str = "", hometown: str = "") -> List[Player]:
        """
        ПОИСК ПО УСЛОВИЯМ:
        - (ФИО И дата) - оба должны совпадать
        - И (позиция ИЛИ состав) - хотя бы одно
        - И (команда ИЛИ город) - хотя бы одно
        + Игнорирование регистра везде где текст
        """
        all_players = self.get_all_players()
        result = []

        # Приводим поисковые запросы к нижнему регистру
        name_part_lower = name_part.lower() if name_part else ""
        team_lower = team.lower() if team else ""
        hometown_lower = hometown.lower() if hometown else ""

        for player in all_players:
            # === ГРУППА 1: ФИО И дата ===
            group1_ok = True

            # Проверяем ФИО (частичное совпадение, игнорируем регистр)
            if name_part and name_part_lower not in player.full_name.lower():
                group1_ok = False

            # Проверяем дату
            if birth_date and player.birth_date != birth_date:
                group1_ok = False

            if not group1_ok:
                continue

            # === ГРУППА 2: позиция ИЛИ состав ===
            group2_ok = True
            if position or is_starter is not None:
                group2_ok = False
                # Проверяем позицию
                if position and player.position == position:
                    group2_ok = True
                # Проверяем состав
                if is_starter is not None and player.is_starter == is_starter:
                    group2_ok = True

            if not group2_ok:
                continue

            # === ГРУППА 3: команда ИЛИ город ===
            group3_ok = True
            if team or hometown:
                group3_ok = False
                # Проверяем команду (игнорируем регистр)
                if team and team_lower in player.team.lower():
                    group3_ok = True
                # Проверяем город (игнорируем регистр)
                if hometown and hometown_lower in player.hometown.lower():
                    group3_ok = True

            if group3_ok:
                result.append(player)

        return result

    def delete_players(self, name_part: str = "", birth_date: Optional[date] = None,
                       position: str = "", is_starter: Optional[bool] = None,
                       team: str = "", hometown: str = "") -> int:
        """
        УДАЛЕНИЕ ПО ТЕМ ЖЕ УСЛОВИЯМ
        Возвращает количество удаленных записей
        """
        # Находим игроков для удаления
        to_delete = self.search_players(name_part, birth_date, position,
                                        is_starter, team, hometown)

        if not to_delete:
            return 0

        # Удаляем каждого
        deleted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for player in to_delete:
                cursor.execute("DELETE FROM players WHERE id = ?", (player.id,))
                deleted += cursor.rowcount
            conn.commit()

        return deleted

    def clear_all(self):
        """Очистка всех записей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players")
            conn.commit()

    def add_sample_players(self):
        """Добавление тестовых игроков"""
        import random
        from datetime import date

        first_names = ["Александр", "Дмитрий", "Максим", "Сергей", "Андрей",
                       "Алексей", "Артем", "Илья", "Кирилл", "Михаил"]

        last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
                      "Попов", "Васильев", "Зайцев", "Соколов", "Михайлов"]

        patronymics = ["Александрович", "Дмитриевич", "Максимович", "Сергеевич", "Андреевич",
                       "Алексеевич", "Артемович", "Ильич", "Кириллович", "Михайлович"]

        teams = ["Спартак", "ЦСКА", "Динамо", "Зенит", "Локомотив",
                 "Краснодар", "Ростов", "Рубин", "Урал"]

        cities = ["Москва", "Санкт-Петербург", "Казань", "Краснодар", "Ростов-на-Дону",
                  "Екатеринбург", "Нижний Новгород", "Минск", "Волгоград", "Воронеж"]

        positions = ["Вратарь", "Защитник", "Полузащитник", "Нападающий"]

        used_names = set()
        added = 0

        while added < 50:
            last = random.choice(last_names)
            first = random.choice(first_names)
            patronymic = random.choice(patronymics)

            full_name = f"{last} {first} {patronymic}"

            if full_name in used_names:
                continue
            used_names.add(full_name)

            year = random.randint(1985, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            if month == 2 and day > 28:
                day = 28
            birth_date = date(year, month, day)

            player = Player(
                full_name=full_name,
                birth_date=birth_date,
                team=random.choice(teams),
                hometown=random.choice(cities),
                is_starter=random.choice([True, False]),
                position=random.choice(positions)
            )

            self.add_player(player)
            added += 1