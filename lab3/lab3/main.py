import pygame
import sys
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, DARK_GRAY, GOLD, YELLOW, WHITE, BLUE, GREEN, RED
from sound import play_menu_music
from highscores import HighScores
from ui import Game
from network import Network
from online_game import OnlineGame


def show_highscores(screen, highscores):
    """Отображает таблицу рекордов"""
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 24)

    running = True
    while running:
        screen.fill(DARK_GRAY)
        title = title_font.render("ТАБЛИЦА РЕКОРДОВ", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        y = 120
        headers = ["#", "ИМЯ", "ОЧКИ", "ДАТА"]
        for i, header in enumerate(headers):
            x = 150 + i * 200
            text = font.render(header, True, YELLOW)
            screen.blit(text, (x, y))

        y += 50
        for i, score in enumerate(highscores.get_scores()[:10]):
            color = GOLD if i == 0 else WHITE
            text = font.render(str(i + 1), True, color)
            screen.blit(text, (150, y))
            text = font.render(score['name'][:15], True, color)
            screen.blit(text, (350, y))
            text = font.render(str(score['score']), True, color)
            screen.blit(text, (550, y))
            text = small_font.render(score['date'], True, (150, 150, 150))
            screen.blit(text, (750, y))
            y += 40

        info_text = small_font.render("Нажмите ESC для возврата в меню", True, WHITE)
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        screen.blit(info_text, info_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False


def show_help(screen):
    """Отображает справку с правилами игры"""
    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 20)

    rules = [
        "ПРАВИЛА ИГРЫ В ШАХМАТЫ:",
        "",
        "1. Цель игры - поставить мат королю противника.",
        "",
        "2. Ходы фигур:",
        "   - Король (K): ходит на 1 клетку в любом направлении",
        "   - Ферзь (Q): ходит по вертикали, горизонтали и диагонали",
        "   - Ладья (R): ходит по вертикали и горизонтали",
        "   - Слон (B): ходит по диагонали",
        "   - Конь (N): ходит буквой 'Г' (2+1)",
        "   - Пешка (P): ходит вперед на 1, бьет по диагонали",
        "",
        "3. Особые правила:",
        "   - Первый ход пешки - на 2 клетки",
        "   - Рокировка - одновременный ход короля и ладьи",
        "   - Взятие на проходе",
        "   - Превращение пешки при достижении последней горизонтали",
        "",
        "4. Шах - король под атакой, мат - шах и нет защиты",
        "",
        "УПРАВЛЕНИЕ:",
        "   - Клик мыши - выбор фигуры/ход",
        "   - ESC - выход в главное меню",
        "   - F11 - полный экран"
    ]

    running = True
    while running:
        screen.fill(DARK_GRAY)
        title = title_font.render("СПРАВКА", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(title, title_rect)

        y = 100
        for line in rules:
            if line.startswith("ПРАВИЛА"):
                text = font.render(line, True, YELLOW)
            elif line.startswith("УПРАВЛЕНИЕ"):
                text = font.render(line, True, YELLOW)
                y += 20
            elif line.startswith("   "):
                text = small_font.render(line, True, (150, 150, 150))
            elif line == "":
                y += 10
                continue
            else:
                text = font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30

        info_text = small_font.render("Нажмите ESC для возврата в меню", True, WHITE)
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        screen.blit(info_text, info_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False


def show_new_record_dialog(screen, score):
    """Показывает диалог для ввода имени при новом рекорде"""
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 48)

    name = ""
    active = True

    while active:
        screen.fill(DARK_GRAY)
        title = big_font.render("НОВЫЙ РЕКОРД!", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        score_text = font.render(f"Ваш результат: {score} очков!", True, GREEN)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
        screen.blit(score_text, score_rect)

        prompt = font.render("Введите ваше имя:", True, WHITE)
        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH // 2, 260))
        screen.blit(prompt, prompt_rect)

        name_surface = font.render(name + "_", True, YELLOW)
        name_rect = name_surface.get_rect(center=(WINDOW_WIDTH // 2, 330))
        screen.blit(name_surface, name_rect)

        info = font.render("Нажмите ENTER для сохранения, ESC для отмены", True, (150, 150, 150))
        info_rect = info.get_rect(center=(WINDOW_WIDTH // 2, 450))
        screen.blit(info, info_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 20:
                    name += event.unicode

    return None


def choose_difficulty(screen):
    """Меню выбора сложности для игры с компьютером"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    difficulties = ["EASY", "MEDIUM", "HARD", "EXPERT", "НАЗАД"]
    selected = 1
    descriptions = {
        "EASY": "Случайные ходы",
        "MEDIUM": "Видит на 2 хода",
        "HARD": "Видит на 3 хода",
        "EXPERT": "Видит на 4 хода"
    }
    while True:
        screen.fill(DARK_GRAY)
        title = font.render("ВЫБЕРИТЕ СЛОЖНОСТЬ", True, GOLD)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        for i, diff in enumerate(difficulties):
            color = YELLOW if i == selected else WHITE
            text = font.render(diff, True, color)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 150 + i * 60))
        if selected < len(difficulties) - 1:
            desc = descriptions.get(difficulties[selected], "")
            desc_text = small_font.render(desc, True, BLUE)
            screen.blit(desc_text, (WINDOW_WIDTH // 2 - desc_text.get_width() // 2, 450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(difficulties)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(difficulties)
                elif event.key == pygame.K_RETURN:
                    if difficulties[selected] == "НАЗАД":
                        return None
                    else:
                        return difficulties[selected].lower()


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Шахматы")

    highscores = HighScores()
    play_menu_music()

    font = pygame.font.Font(None, 48)

    # ГЛАВНОЕ МЕНЮ
    options = ["ИГРАТЬ", "ТАБЛИЦА РЕКОРДОВ", "СПРАВКА", "ВЫХОД"]
    selected = 0

    while True:
        screen.fill(DARK_GRAY)
        title = font.render("ШАХМАТЫ", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            text = font.render(opt, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 200 + i * 70))
            screen.blit(text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        # ПОДМЕНЮ ВЫБОРА ТИПА ИГРЫ
                        game_type_options = ["ЛОКАЛЬНАЯ", "ОНЛАЙН", "НАЗАД"]
                        game_type_selected = 0
                        game_type_running = True

                        while game_type_running:
                            screen.fill(DARK_GRAY)
                            title = font.render("ВЫБЕРИТЕ ТИП ИГРЫ", True, GOLD)
                            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
                            screen.blit(title, title_rect)

                            for i, opt in enumerate(game_type_options):
                                color = YELLOW if i == game_type_selected else WHITE
                                text = font.render(opt, True, color)
                                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 70))
                                screen.blit(text, text_rect)

                            pygame.display.flip()

                            for gt_event in pygame.event.get():
                                if gt_event.type == pygame.QUIT:
                                    pygame.quit()
                                    return
                                if gt_event.type == pygame.KEYDOWN:
                                    if gt_event.key == pygame.K_UP:
                                        game_type_selected = (game_type_selected - 1) % 3
                                    elif gt_event.key == pygame.K_DOWN:
                                        game_type_selected = (game_type_selected + 1) % 3
                                    elif gt_event.key == pygame.K_RETURN:
                                        if game_type_selected == 0:
                                            # ЛОКАЛЬНАЯ ИГРА - подменю 2 игрока или компьютер
                                            mode_options = ["2 ИГРОКА", "ПРОТИВ КОМПЬЮТЕРА", "НАЗАД"]
                                            mode_selected = 0
                                            mode_running = True

                                            while mode_running:
                                                screen.fill(DARK_GRAY)
                                                title = font.render("ВЫБЕРИТЕ РЕЖИМ", True, GOLD)
                                                title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
                                                screen.blit(title, title_rect)

                                                for i, opt in enumerate(mode_options):
                                                    color = YELLOW if i == mode_selected else WHITE
                                                    text = font.render(opt, True, color)
                                                    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 70))
                                                    screen.blit(text, text_rect)

                                                pygame.display.flip()

                                                for mode_event in pygame.event.get():
                                                    if mode_event.type == pygame.QUIT:
                                                        pygame.quit()
                                                        return
                                                    if mode_event.type == pygame.KEYDOWN:
                                                        if mode_event.key == pygame.K_UP:
                                                            mode_selected = (mode_selected - 1) % 3
                                                        elif mode_event.key == pygame.K_DOWN:
                                                            mode_selected = (mode_selected + 1) % 3
                                                        elif mode_event.key == pygame.K_RETURN:
                                                            if mode_selected == 0:
                                                                # 2 ИГРОКА
                                                                game = Game(screen, vs_computer=False)
                                                                score = game.run()
                                                                if score and highscores.is_high_score(score):
                                                                    name = show_new_record_dialog(screen, score)
                                                                    if name:
                                                                        highscores.add_score(name, score)
                                                                mode_running = False
                                                                play_menu_music()
                                                            elif mode_selected == 1:
                                                                # ПРОТИВ КОМПЬЮТЕРА
                                                                difficulty = choose_difficulty(screen)
                                                                if difficulty:
                                                                    game = Game(screen, vs_computer=True,
                                                                                ai_difficulty=difficulty)
                                                                    score = game.run()
                                                                    if score and highscores.is_high_score(score):
                                                                        name = show_new_record_dialog(screen, score)
                                                                        if name:
                                                                            highscores.add_score(name, score)
                                                                mode_running = False
                                                                play_menu_music()
                                                            else:
                                                                mode_running = False
                                            game_type_running = False

                                        elif game_type_selected == 1:
                                            # ОНЛАЙН ИГРА - подменю создать или подключиться
                                            online_options = ["СОЗДАТЬ ИГРУ (СЕРВЕР)", "ПОДКЛЮЧИТЬСЯ (КЛИЕНТ)", "НАЗАД"]
                                            online_selected = 0
                                            online_running = True

                                            while online_running:
                                                screen.fill(DARK_GRAY)
                                                title = font.render("ОНЛАЙН ИГРА", True, GOLD)
                                                title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
                                                screen.blit(title, title_rect)

                                                for i, opt in enumerate(online_options):
                                                    color = YELLOW if i == online_selected else WHITE
                                                    text = font.render(opt, True, color)
                                                    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 250 + i * 70))
                                                    screen.blit(text, text_rect)

                                                # Подсказка
                                                hint = pygame.font.Font(None, 20).render(
                                                    "Сначала запустите server.py в отдельном терминале", True, BLUE)
                                                hint_rect = hint.get_rect(
                                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                                                screen.blit(hint, hint_rect)

                                                pygame.display.flip()

                                                for online_event in pygame.event.get():
                                                    if online_event.type == pygame.QUIT:
                                                        pygame.quit()
                                                        return
                                                    if online_event.type == pygame.KEYDOWN:
                                                        if online_event.key == pygame.K_UP:
                                                            online_selected = (online_selected - 1) % 3
                                                        elif online_event.key == pygame.K_DOWN:
                                                            online_selected = (online_selected + 1) % 3
                                                        elif online_event.key == pygame.K_RETURN:
                                                            if online_selected == 0:
                                                                # СОЗДАТЬ ИГРУ (СЕРВЕР)
                                                                network = Network(host='localhost', port=5555)
                                                                if network.connect():
                                                                    game = OnlineGame(screen, network,
                                                                                      network.player_color)
                                                                    score = game.run()
                                                                    if score and highscores.is_high_score(score):
                                                                        name = show_new_record_dialog(screen, score)
                                                                        if name:
                                                                            highscores.add_score(name, score)
                                                                    network.close()
                                                                else:
                                                                    print(
                                                                        "Не удалось подключиться к серверу. Убедитесь, что server.py запущен.")
                                                                online_running = False
                                                                play_menu_music()
                                                            elif online_selected == 1:
                                                                # ПОДКЛЮЧИТЬСЯ (КЛИЕНТ)
                                                                network = Network(host='localhost', port=5555)
                                                                if network.connect():
                                                                    game = OnlineGame(screen, network,
                                                                                      network.player_color)
                                                                    score = game.run()
                                                                    if score and highscores.is_high_score(score):
                                                                        name = show_new_record_dialog(screen, score)
                                                                        if name:
                                                                            highscores.add_score(name, score)
                                                                    network.close()
                                                                else:
                                                                    print(
                                                                        "Не удалось подключиться к серверу. Убедитесь, что server.py запущен.")
                                                                online_running = False
                                                                play_menu_music()
                                                            else:
                                                                online_running = False
                                            game_type_running = False
                                        else:
                                            game_type_running = False
                    elif selected == 1:
                        show_highscores(screen, highscores)
                    elif selected == 2:
                        show_help(screen)
                    else:
                        pygame.quit()
                        return


if __name__ == "__main__":
    main()