"""
Модуль для постраничного вывода данных
"""
from typing import List, Any


class Paginator:
    """Класс для управления постраничным выводом"""

    def __init__(self, items: List[Any], items_per_page: int = 10):
        self.items = items
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)

    def get_current_page_items(self) -> List[Any]:
        """Получить элементы текущей страницы"""
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def next_page(self):
        """Следующая страница"""
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        """Предыдущая страница"""
        if self.current_page > 1:
            self.current_page -= 1

    def first_page(self):
        """Первая страница"""
        self.current_page = 1

    def last_page(self):
        """Последняя страница"""
        self.current_page = self.total_pages

    def set_items_per_page(self, count: int):
        """Изменить количество записей на странице"""
        self.items_per_page = count
        self.total_pages = max(1, (len(self.items) + count - 1) // count)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

    def get_info(self) -> dict:
        """Получить информацию о пагинации"""
        start = (self.current_page - 1) * self.items_per_page + 1
        end = min(self.current_page * self.items_per_page, len(self.items))

        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'items_per_page': self.items_per_page,
            'total_items': len(self.items),
            'start_index': start if len(self.items) > 0 else 0,
            'end_index': end if len(self.items) > 0 else 0
        }