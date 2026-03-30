"""
Диалог добавления нового игрока
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QCheckBox,
                             QDialogButtonBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import QDate
from datetime import date
from football_manager.model.player import Player


class AddPlayerDialog(QDialog):
    """Окно для добавления нового игрока"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить игрока")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите ФИО полностью")
        form.addRow("ФИО:", self.name_edit)

        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate.currentDate().addYears(-25))
        self.birth_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Дата рождения:", self.birth_date)

        self.team_edit = QLineEdit()
        self.team_edit.setPlaceholderText("Введите название команды")
        form.addRow("Команда:", self.team_edit)

        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Введите домашний город")
        form.addRow("Город:", self.city_edit)

        self.position_combo = QComboBox()
        self.position_combo.addItems(Player.get_positions())
        form.addRow("Позиция:", self.position_combo)

        self.starter_check = QCheckBox("Основной состав")
        self.starter_check.setChecked(True)
        form.addRow("", self.starter_check)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО")
            return

        if not self.team_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите команду")
            return

        if not self.city_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите город")
            return

        self.accept()

    def get_player(self) -> Player:
        return Player(
            full_name=self.name_edit.text().strip(),
            birth_date=date(
                self.birth_date.date().year(),
                self.birth_date.date().month(),
                self.birth_date.date().day()
            ),
            team=self.team_edit.text().strip(),
            hometown=self.city_edit.text().strip(),
            is_starter=self.starter_check.isChecked(),
            position=self.position_combo.currentText()
        )