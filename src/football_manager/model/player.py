"""
Модель данных футболиста
"""
from datetime import date
from dataclasses import dataclass
from typing import Optional


@dataclass
class Player:
    """Класс представляющий одного футболиста"""
    full_name: str  # ФИО игрока
    birth_date: date  # Дата рождения
    team: str  # Футбольная команда
    hometown: str  # Домашний город
    is_starter: bool  # True - основной состав, False - запасной
    position: str  # Позиция на поле
    id: Optional[int] = None  # ID в базе данных

    @staticmethod
    def get_positions():
        """Список допустимых позиций на поле"""
        return ["Вратарь", "Защитник", "Полузащитник", "Нападающий"]

    def to_dict(self):
        """Преобразование в словарь для сохранения"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'birth_date': self.birth_date.isoformat(),
            'team': self.team,
            'hometown': self.hometown,
            'is_starter': self.is_starter,
            'position': self.position
        }