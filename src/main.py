"""
Точка входа в приложение
"""
import sys
from PyQt6.QtWidgets import QApplication
from football_manager.model.database import Database
from football_manager.controller.player_controller import PlayerController
from football_manager.view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Создаем модель
    model = Database("students.db")

    # Создаем контроллер
    controller = PlayerController(model)

    # Создаем окно
    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()