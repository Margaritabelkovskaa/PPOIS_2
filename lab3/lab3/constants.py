from config import CONFIG

# Размеры окна - возвращаем как было
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
BOARD_SIZE = CONFIG['board']['size']
SQUARE_SIZE = 100  # Возвращаем 100
LEFT_PANEL = 100
RIGHT_PANEL = 100

# Цвета из конфига
colors = CONFIG['colors']
LIGHT_BROWN = tuple(colors['light_brown'])
DARK_BROWN = tuple(colors['dark_brown'])
WHITE = tuple(colors['white'])
BLACK = tuple(colors['black'])
GREEN = tuple(colors['green'])
YELLOW = tuple(colors['yellow'])
RED = tuple(colors['red'])
GOLD = tuple(colors['gold'])
BLUE = tuple(colors['blue'])
ORANGE = tuple(colors['orange'])
DARK_GRAY = tuple(colors['dark_gray'])
GRAY = tuple(colors['gray'])

# Параметры анимации
MOVE_DURATION = CONFIG['animation']['move_duration']
ROTATE_STEP = CONFIG['animation']['rotate_step']
CAPTURE_PARTICLES = CONFIG['animation']['capture_particles']
CHECK_FLASH_DURATION = CONFIG['animation']['check_flash_duration']

# Ценности фигур
PIECE_VALUES = CONFIG['piece_values']

# Глубина ИИ
AI_DEPTHS = {
    'easy': CONFIG['ai']['easy_depth'],
    'medium': CONFIG['ai']['medium_depth'],
    'hard': CONFIG['ai']['hard_depth'],
    'expert': CONFIG['ai']['expert_depth']
}