"""
Диалог поиска игроков
"""
from typing import Optional, List
from datetime import date
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QLabel, QGroupBox, QDateEdit,
                             QHeaderView, QSpinBox, QCheckBox)
from PyQt6.QtCore import QDate

from football_manager.model.player import Player
from football_manager.utils.pagination import Paginator


class SearchDialog(QDialog):
    """Окно поиска игроков с постраничным выводом"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.search_results: List[Player] = []
        self.paginator: Optional[Paginator] = None

        self.setWindowTitle("Поиск игроков")
        self.setMinimumSize(1000, 700)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout(self)

        # Группа критериев поиска
        criteria_group = QGroupBox("Критерии поиска")
        criteria_layout = QFormLayout()

        # ФИО
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите часть ФИО")
        criteria_layout.addRow("ФИО содержит:", self.name_edit)

        # Дата рождения
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

        # Позиция
        self.position_combo = QComboBox()
        self.position_combo.addItem("Любая", None)
        for pos in Player.get_positions():
            self.position_combo.addItem(pos, pos)
        criteria_layout.addRow("Позиция:", self.position_combo)

        # Состав
        self.starter_combo = QComboBox()
        self.starter_combo.addItem("Любой", None)
        self.starter_combo.addItem("Основной", True)
        self.starter_combo.addItem("Запасной", False)
        criteria_layout.addRow("Состав:", self.starter_combo)

        # Команда
        self.team_edit = QLineEdit()
        self.team_edit.setPlaceholderText("Введите название команды")
        criteria_layout.addRow("Команда содержит:", self.team_edit)

        # Город
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Введите название города")
        criteria_layout.addRow("Город содержит:", self.city_edit)

        criteria_group.setLayout(criteria_layout)
        layout.addWidget(criteria_group)

        # Кнопка поиска
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self._perform_search)
        search_btn.setMinimumHeight(40)
        layout.addWidget(search_btn)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ФИО", "Дата рождения", "Команда", "Город", "Позиция", "Состав"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Панель пагинации
        pagination_layout = QHBoxLayout()

        self.page_info = QLabel("Страница: 0/0")
        pagination_layout.addWidget(self.page_info)
        pagination_layout.addStretch()

        self.first_btn = QPushButton("|< Первая")
        self.first_btn.clicked.connect(self._first_page)
        self.first_btn.setEnabled(False)
        pagination_layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("< Предыдущая")
        self.prev_btn.clicked.connect(self._prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self._go_to_page)
        self.page_spin.setEnabled(False)
        pagination_layout.addWidget(self.page_spin)

        self.next_btn = QPushButton("Следующая >")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("Последняя >|")
        self.last_btn.clicked.connect(self._last_page)
        self.last_btn.setEnabled(False)
        pagination_layout.addWidget(self.last_btn)

        pagination_layout.addStretch()

        self.per_page_combo = QComboBox()
        self.per_page_combo.addItems(["5", "10", "20", "50"])
        self.per_page_combo.setCurrentText("10")
        self.per_page_combo.currentTextChanged.connect(self._change_per_page)
        self.per_page_combo.setEnabled(False)
        pagination_layout.addWidget(QLabel("Записей на стр:"))
        pagination_layout.addWidget(self.per_page_combo)

        layout.addLayout(pagination_layout)

    def _perform_search(self):
        """Выполнить поиск"""
        name = self.name_edit.text().strip()

        birth_date = None
        if self.use_date_check.isChecked():
            qdate = self.birth_date_edit.date()
            birth_date = date(qdate.year(), qdate.month(), qdate.day())

        position = self.position_combo.currentData()
        is_starter = self.starter_combo.currentData()
        team = self.team_edit.text().strip()
        hometown = self.city_edit.text().strip()

        self.search_results = self.controller.search_players(
            name, birth_date, position, is_starter, team, hometown
        )

        per_page = int(self.per_page_combo.currentText())
        self.paginator = Paginator(self.search_results, per_page)

        self._update_table()

        has_results = len(self.search_results) > 0
        self.first_btn.setEnabled(has_results)
        self.prev_btn.setEnabled(has_results)
        self.next_btn.setEnabled(has_results)
        self.last_btn.setEnabled(has_results)
        self.page_spin.setEnabled(has_results)
        self.per_page_combo.setEnabled(has_results)

    def _update_table(self):
        """Обновить таблицу"""
        if not self.paginator:
            return

        items = self.paginator.get_current_page_items()
        self.table.setRowCount(len(items))

        for i, player in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(player.full_name))
            self.table.setItem(i, 1, QTableWidgetItem(player.birth_date.strftime("%Y-%m-%d")))
            self.table.setItem(i, 2, QTableWidgetItem(player.team))
            self.table.setItem(i, 3, QTableWidgetItem(player.hometown))
            self.table.setItem(i, 4, QTableWidgetItem(player.position))
            self.table.setItem(i, 5, QTableWidgetItem("Основной" if player.is_starter else "Запасной"))

        info = self.paginator.get_info()
        self.page_info.setText(
            f"Страница: {info['current_page']}/{info['total_pages']} "
            f"({info['start_index']}-{info['end_index']} из {info['total_items']})"
        )
        self.page_spin.setMaximum(info['total_pages'])
        self.page_spin.setValue(info['current_page'])

    def _first_page(self):
        if self.paginator:
            self.paginator.first_page()
            self._update_table()

    def _prev_page(self):
        if self.paginator:
            self.paginator.prev_page()
            self._update_table()

    def _next_page(self):
        if self.paginator:
            self.paginator.next_page()
            self._update_table()

    def _last_page(self):
        if self.paginator:
            self.paginator.last_page()
            self._update_table()

    def _go_to_page(self, page):
        if self.paginator and page != self.paginator.current_page:
            self.paginator.current_page = page
            self._update_table()

    def _change_per_page(self, value):
        if self.paginator:
            self.paginator.set_items_per_page(int(value))
            self._update_table()