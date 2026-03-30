"""
Контроллер - связывает модель и представление
"""
from typing import List, Optional
from datetime import date
from football_manager.model.player import Player
from football_manager.model.database import Database
from football_manager.utils.xml_handler import XMLHandler


class PlayerController:
    """Контроллер для управления игроками"""

    def __init__(self, database: Database):
        self.db = database

    def add_player(self, player: Player) -> int:
        """Добавить игрока"""
        return self.db.add_player(player)

    def get_all_players(self) -> List[Player]:
        """Получить всех игроков"""
        return self.db.get_all_players()

    def search_players(self, name_part: str = "", birth_date: Optional[date] = None,
                       position: str = "", is_starter: Optional[bool] = None,
                       team: str = "", hometown: str = "") -> List[Player]:
        """Поиск игроков"""
        return self.db.search_players(
            name_part, birth_date, position, is_starter, team, hometown
        )

    def delete_players(self, name_part: str = "", birth_date: Optional[date] = None,
                       position: str = "", is_starter: Optional[bool] = None,
                       team: str = "", hometown: str = "") -> int:
        """Удаление игроков"""
        return self.db.delete_players(
            name_part, birth_date, position, is_starter, team, hometown
        )

    def import_from_xml(self, filename: str) -> int:
        """Импорт из XML"""
        players = XMLHandler.read_from_file(filename)
        count = 0
        for player in players:
            self.db.add_player(player)
            count += 1
        return count

    def export_to_xml(self, filename: str) -> None:
        """Экспорт в XML"""
        players = self.db.get_all_players()
        XMLHandler.write_to_file(players, filename)

    def clear_all(self):
        """Очистить все записи"""
        self.db.clear_all()

    def add_sample_players(self):
        """Добавить тестовые данные"""
        self.db.add_sample_players()