"""
Диалог удаления игроков
"""
from datetime import date
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton,
                             QMessageBox, QGroupBox, QDateEdit,
                             QCheckBox, QLabel)
from PyQt6.QtCore import QDate

from football_manager.model.player import Player


class DeleteDialog(QDialog):
    """Окно удаления игроков по критериям"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

        self.setWindowTitle("Удаление игроков")
        self.setModal(True)
        self.setMinimumWidth(400)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        warning = QLabel("Внимание! Удаление нельзя отменить.")
        warning.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning)

        criteria_group = QGroupBox("Критерии удаления")
        criteria_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите часть ФИО")
        criteria_layout.addRow("ФИО содержит:", self.name_edit)

        date_layout = QHBoxLayout()
        self.use_date_check = QCheckBox("Использовать")
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDate(QDate.currentDate())
        self.birth_date_edit.setEnabled(False)
        self.use_date_check.toggled.connect(self.birth_date_edit.setEnabled)
        date_layout.addWidget(self.use_date_check)
        date_layout.addWidget(self.birth_date_edit)
        criteria_layout.addRow("Дата рождения:", date_layout)

        self.position_combo = QComboBox()
        self.position_combo.addItem("Любая", None)
        for pos in Player.get_positions():
            self.position_combo.addItem(pos, pos)
        criteria_layout.addRow("Позиция:", self.position_combo)

        self.starter_combo = QComboBox()
        self.starter_combo.addItem("Любой", None)
        self.starter_combo.addItem("Основной", True)
        self.starter_combo.addItem("Запасной", False)
        criteria_layout.addRow("Состав:", self.starter_combo)

        self.team_edit = QLineEdit()
        self.team_edit.setPlaceholderText("Введите название команды")
        criteria_layout.addRow("Команда содержит:", self.team_edit)

        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Введите название города")
        criteria_layout.addRow("Город содержит:", self.city_edit)

        criteria_group.setLayout(criteria_layout)
        layout.addWidget(criteria_group)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete)
        delete_btn.setMinimumHeight(40)
        delete_btn.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        layout.addWidget(delete_btn)

    def _delete(self):
        name = self.name_edit.text().strip()

        birth_date = None
        if self.use_date_check.isChecked():
            qdate = self.birth_date_edit.date()
            birth_date = date(qdate.year(), qdate.month(), qdate.day())

        position = self.position_combo.currentData()
        is_starter = self.starter_combo.currentData()
        team = self.team_edit.text().strip()
        hometown = self.city_edit.text().strip()

        found = self.controller.search_players(
            name, birth_date, position, is_starter, team, hometown
        )

        if not found:
            QMessageBox.information(
                self,
                "Результат",
                "Записей для удаления не найдено"
            )
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Найдено записей: {len(found)}\n\n"
            f"Вы действительно хотите удалить эти записи?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted = self.controller.delete_players(
                name, birth_date, position, is_starter, team, hometown
            )

            QMessageBox.information(
                self,
                "Результат удаления",
                f"Удалено записей: {deleted}"
            )

            self.accept()