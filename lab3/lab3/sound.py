import pygame
import os
from config import CONFIG

# Инициализация звука
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

MOVE_SOUND_PATH = CONFIG['sound']['move_sound']
WIN_SOUND_PATH = CONFIG['sound']['win_sound']
LOSE_SOUND_PATH = CONFIG['sound']['lose_sound']
MENU_MUSIC_PATH = CONFIG['sound']['menu_music']
GAME_MUSIC_PATH = CONFIG['sound']['game_music']

move_sound = pygame.mixer.Sound(MOVE_SOUND_PATH)
move_sound.set_volume(CONFIG['sound']['sfx_volume'])

win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
win_sound.set_volume(CONFIG['sound']['sfx_volume'])

lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)
lose_sound.set_volume(CONFIG['sound']['sfx_volume'])

def play_menu_music():
    pygame.mixer.music.load(MENU_MUSIC_PATH)
    pygame.mixer.music.set_volume(CONFIG['sound']['music_volume'])
    pygame.mixer.music.play(-1)

def play_game_music():
    pygame.mixer.music.load(GAME_MUSIC_PATH)
    pygame.mixer.music.set_volume(CONFIG['sound']['music_volume'])
    pygame.mixer.music.play(-1)