"""
Обработка XML файлов
SAX парсер для чтения, DOM для записи
"""
import xml.sax
import xml.dom.minidom
from datetime import date
from typing import List
from football_manager.model.player import Player


class PlayerSAXHandler(xml.sax.ContentHandler):
    """SAX парсер для чтения XML"""

    def __init__(self):
        self.players = []
        self.current_element = ""
        self.current_player = {}

    def startElement(self, name, attrs):
        self.current_element = name
        if name == "player":
            self.current_player = {}

    def endElement(self, name):
        if name == "player":
            if self._is_valid_player(self.current_player):
                try:
                    player = Player(
                        full_name=self.current_player.get('full_name', ''),
                        birth_date=date.fromisoformat(self.current_player.get('birth_date', '2000-01-01')),
                        team=self.current_player.get('team', ''),
                        hometown=self.current_player.get('hometown', ''),
                        is_starter=self.current_player.get('is_starter', 'False').lower() == 'true',
                        position=self.current_player.get('position', '')
                    )
                    self.players.append(player)
                except:
                    pass
            self.current_player = {}

    def characters(self, content):
        if content.strip():
            self.current_player[self.current_element] = content.strip()

    def _is_valid_player(self, data):
        required = ['full_name', 'birth_date', 'team', 'hometown', 'is_starter', 'position']
        return all(field in data for field in required)


class XMLHandler:
    """Класс для работы с XML файлами"""

    @staticmethod
    def write_to_file(players: List[Player], filename: str):
        """Запись в XML с использованием DOM парсера"""
        doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "players", None)
        root = doc.documentElement

        for player in players:
            player_elem = doc.createElement("player")

            fields = [
                ("full_name", player.full_name),
                ("birth_date", player.birth_date.isoformat()),
                ("team", player.team),
                ("hometown", player.hometown),
                ("is_starter", str(player.is_starter).lower()),
                ("position", player.position)
            ]

            for field_name, field_value in fields:
                field_elem = doc.createElement(field_name)
                field_elem.appendChild(doc.createTextNode(field_value))
                player_elem.appendChild(field_elem)

            root.appendChild(player_elem)

        with open(filename, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent="  ", newl="\n", encoding='utf-8')

    @staticmethod
    def read_from_file(filename: str) -> List[Player]:
        """Чтение из XML с использованием SAX парсера"""
        handler = PlayerSAXHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filename)
        return handler.players