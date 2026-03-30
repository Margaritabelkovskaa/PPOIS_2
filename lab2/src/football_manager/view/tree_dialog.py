"""
Диалог отображения в виде дерева
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTreeWidget,
                             QTreeWidgetItem, QPushButton)
from PyQt6.QtCore import Qt
from football_manager.model.player import Player
from typing import List


class TreeViewDialog(QDialog):
    """Окно для отображения записей в виде дерева"""

    def __init__(self, players: List[Player], parent=None):
        super().__init__(parent)
        self.players = players

        self.setWindowTitle("Древовидное представление")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._setup_ui()
        self._populate_tree()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Футболисты")
        layout.addWidget(self.tree)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _populate_tree(self):
        teams = {}
        for player in self.players:
            if player.team not in teams:
                teams[player.team] = []
            teams[player.team].append(player)

        for team, team_players in teams.items():
            team_item = QTreeWidgetItem(self.tree)
            team_item.setText(0, f"Команда: {team} ({len(team_players)} игроков)")

            for player in team_players:
                player_item = QTreeWidgetItem(team_item)
                player_item.setText(0, f"{player.full_name}")

                fields = [
                    f"Дата рождения: {player.birth_date.strftime('%Y-%m-%d')}",
                    f"Город: {player.hometown}",
                    f"Позиция: {player.position}",
                    f"Состав: {'Основной' if player.is_starter else 'Запасной'}"
                ]

                for field in fields:
                    field_item = QTreeWidgetItem(player_item)
                    field_item.setText(0, field)

        self.tree.expandAll()