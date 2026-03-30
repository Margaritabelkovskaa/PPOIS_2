"""
Главное окно приложения
"""
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMenuBar, QMenu, QToolBar, QStatusBar,
                             QMessageBox, QFileDialog, QLabel, QComboBox,
                             QSpinBox, QHeaderView)
from PyQt6.QtCore import Qt

from football_manager.utils.pagination import Paginator
from .add_dialog import AddPlayerDialog
from .search_dialog import SearchDialog
from .delete_dialog import DeleteDialog
from .tree_dialog import TreeViewDialog


class MainWindow(QMainWindow):
    """Главное окно программы"""

    def __init__(self, controller):
        """controller - экземпляр PlayerController"""
        super().__init__()
        self.controller = controller
        self.paginator: Optional[Paginator] = None

        self.setWindowTitle("Система управления футболистами")
        self.setMinimumSize(1200, 700)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_ui()
        self._setup_statusbar()

        self._refresh_table()

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Файл")

        import_action = file_menu.addAction("&Загрузить из XML")
        import_action.triggered.connect(self._import_xml)

        export_action = file_menu.addAction("&Сохранить в XML")
        export_action.triggered.connect(self._export_xml)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("В&ыход")
        exit_action.triggered.connect(self.close)

        edit_menu = menubar.addMenu("&Правка")

        add_action = edit_menu.addAction("&Добавить")
        add_action.triggered.connect(self._show_add_dialog)

        sample_action = edit_menu.addAction("&Добавить тестовые данные (50 игроков)")
        sample_action.triggered.connect(self._add_sample_players)

        search_action = edit_menu.addAction("&Поиск")
        search_action.triggered.connect(self._show_search_dialog)

        delete_action = edit_menu.addAction("&Удалить")
        delete_action.triggered.connect(self._show_delete_dialog)

        view_menu = menubar.addMenu("&Вид")

        tree_view_action = view_menu.addAction("&Древовидное представление")
        tree_view_action.triggered.connect(self._show_tree_view)

        view_menu.addSeparator()

        refresh_action = view_menu.addAction("&Обновить")
        refresh_action.triggered.connect(self._refresh_table)

        help_menu = menubar.addMenu("&Справка")

        about_action = help_menu.addAction("&О программе")
        about_action.triggered.connect(self._show_about)

    def _setup_toolbar(self):
        toolbar = self.addToolBar("Панель инструментов")

        add_action = toolbar.addAction(" Добавить")
        add_action.triggered.connect(self._show_add_dialog)

        sample_action = toolbar.addAction(" Тестовые")
        sample_action.triggered.connect(self._add_sample_players)

        search_action = toolbar.addAction(" Поиск")
        search_action.triggered.connect(self._show_search_dialog)

        delete_action = toolbar.addAction(" Удалить")
        delete_action.triggered.connect(self._show_delete_dialog)

        toolbar.addSeparator()

        import_action = toolbar.addAction(" Загрузить")
        import_action.triggered.connect(self._import_xml)

        export_action = toolbar.addAction(" Сохранить")
        export_action.triggered.connect(self._export_xml)

        toolbar.addSeparator()

        refresh_action = toolbar.addAction(" Обновить")
        refresh_action.triggered.connect(self._refresh_table)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Дата рождения", "Команда", "Город", "Позиция", "Состав"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        pagination_layout = QHBoxLayout()

        self.page_info = QLabel("Страница: 0/0")
        pagination_layout.addWidget(self.page_info)
        pagination_layout.addStretch()

        self.first_btn = QPushButton("|< Первая")
        self.first_btn.clicked.connect(self._first_page)
        pagination_layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("< Предыдущая")
        self.prev_btn.clicked.connect(self._prev_page)
        pagination_layout.addWidget(self.prev_btn)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self._go_to_page)
        pagination_layout.addWidget(self.page_spin)

        self.next_btn = QPushButton("Следующая >")
        self.next_btn.clicked.connect(self._next_page)
        pagination_layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("Последняя >|")
        self.last_btn.clicked.connect(self._last_page)
        pagination_layout.addWidget(self.last_btn)

        pagination_layout.addStretch()

        self.per_page_combo = QComboBox()
        self.per_page_combo.addItems(["5", "10", "20", "50", "100"])
        self.per_page_combo.setCurrentText("10")
        self.per_page_combo.currentTextChanged.connect(self._change_per_page)
        pagination_layout.addWidget(QLabel("Записей на стр:"))
        pagination_layout.addWidget(self.per_page_combo)

        layout.addLayout(pagination_layout)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов")

    def _refresh_table(self):
        """Обновить таблицу - загружает данные из контроллера"""
        players = self.controller.get_all_players()
        per_page = int(self.per_page_combo.currentText())
        self.paginator = Paginator(players, per_page)
        self._update_table()

    def _update_table(self):
        if not self.paginator:
            return

        items = self.paginator.get_current_page_items()
        self.table.setRowCount(len(items))

        for i, player in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(str(player.id)))
            self.table.setItem(i, 1, QTableWidgetItem(player.full_name))
            self.table.setItem(i, 2, QTableWidgetItem(player.birth_date.strftime("%Y-%m-%d")))
            self.table.setItem(i, 3, QTableWidgetItem(player.team))
            self.table.setItem(i, 4, QTableWidgetItem(player.hometown))
            self.table.setItem(i, 5, QTableWidgetItem(player.position))
            self.table.setItem(i, 6, QTableWidgetItem("Основной" if player.is_starter else "Запасной"))

        info = self.paginator.get_info()
        self.page_info.setText(
            f"Страница: {info['current_page']}/{info['total_pages']} "
            f"({info['start_index']}-{info['end_index']} из {info['total_items']})"
        )
        self.page_spin.setMaximum(info['total_pages'])
        self.page_spin.setValue(info['current_page'])

        self.first_btn.setEnabled(info['current_page'] > 1)
        self.prev_btn.setEnabled(info['current_page'] > 1)
        self.next_btn.setEnabled(info['current_page'] < info['total_pages'])
        self.last_btn.setEnabled(info['current_page'] < info['total_pages'])

        self.status_bar.showMessage(f"Всего записей: {info['total_items']}")

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

    def _show_add_dialog(self):
        from .add_dialog import AddPlayerDialog
        dialog = AddPlayerDialog(self)
        if dialog.exec():
            player = dialog.get_player()
            self.controller.add_player(player)
            self._refresh_table()
            QMessageBox.information(self, "Успех", "Игрок успешно добавлен")

    def _show_search_dialog(self):
        from .search_dialog import SearchDialog
        dialog = SearchDialog(self.controller, self)
        dialog.exec()

    def _show_delete_dialog(self):
        from .delete_dialog import DeleteDialog
        dialog = DeleteDialog(self.controller, self)
        if dialog.exec():
            self._refresh_table()

    def _show_tree_view(self):
        from .tree_dialog import TreeViewDialog
        players = self.controller.get_all_players()
        if not players:
            QMessageBox.information(self, "Информация", "Нет записей для отображения")
            return
        dialog = TreeViewDialog(players, self)
        dialog.exec()

    def _add_sample_players(self):
        """Добавить тестовых игроков"""
        reply = QMessageBox.question(
            self,
            "Добавление тестовых данных",
            "Будет добавлено 50 тестовых игроков. Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.controller.add_sample_players()
            self._refresh_table()
            QMessageBox.information(self, "Успех", "Добавлено 50 тестовых игроков")

    def _import_xml(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите XML файл", "", "XML файлы (*.xml)"
        )

        if filename:
            try:
                count = self.controller.import_from_xml(filename)
                self._refresh_table()
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Загружено {count} записей из файла:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось загрузить файл:\n{str(e)}"
                )

    def _export_xml(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить в XML", "", "XML файлы (*.xml)"
        )

        if filename:
            try:
                self.controller.export_to_xml(filename)
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Данные сохранены в файл:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось сохранить файл:\n{str(e)}"
                )

    def _show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "Система управления футболистами\n"
            "Версия 1.0\n\n"
            "Разработано для управления базой данных футболистов\n"
            "с возможностью добавления, поиска, удаления,\n"
            "импорта/экспорта в XML и древовидного просмотра."
        )