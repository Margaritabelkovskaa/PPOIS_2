import pygame
from constants import *
from game_logic import ChessGame
from ai import ChessAI
from sound import move_sound, win_sound, lose_sound, play_game_music
from animations import MoveAnimation, CaptureAnimation, Particle, CheckFlash, BoardRotationAnimation, CompositeAnimation
from piece import ChessPiece
import os


class PromotionDialog:
    """Диалог выбора фигуры при превращении пешки"""
    # ... (код без изменений) ...


class Game:
    def __init__(self, screen, vs_computer=False, ai_difficulty='medium'):
        self.screen = screen
        self.vs_computer = vs_computer
        self.ai_difficulty = ai_difficulty
        self.game = ChessGame()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 72)

        # === ПОВОРОТ ДОСКИ ТЕПЕРЬ ЧЕРЕЗ АНИМАЦИЮ ===
        self.angle = 0  # Текущий угол
        self.rotation_animation = None  # Анимация поворота
        self.pending_rotation = False  # Запланирован ли поворот

        self.fullscreen = False

        # === АНИМАЦИИ ===
        self.move_animation = None
        self.capture_animations = []
        self.particles = []
        self.check_flash = None
        self.waiting_for_animation = False

        if vs_computer:
            self.ai = ChessAI(difficulty=ai_difficulty)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def add_particles(self, x, y):
        for _ in range(15):
            self.particles.append(Particle(x, y, ORANGE))

    def start_move_animation(self, from_r, from_c, to_r, to_c, captured_piece=None):
        """Запускает анимацию перемещения фигуры"""
        if not self.vs_computer and self.angle >= 90:
            display_from_r = 7 - from_r
            display_from_c = 7 - from_c
            display_to_r = 7 - to_r
            display_to_c = 7 - to_c
        else:
            display_from_r = from_r
            display_from_c = from_c
            display_to_r = to_r
            display_to_c = to_c

        start_x = LEFT_PANEL + display_from_c * SQUARE_SIZE + 5
        start_y = display_from_r * SQUARE_SIZE + 5
        end_x = LEFT_PANEL + display_to_c * SQUARE_SIZE + 5
        end_y = display_to_r * SQUARE_SIZE + 5

        piece = self.game.board[to_r][to_c]
        if piece and piece.image:
            self.move_animation = MoveAnimation(
                (start_x, start_y), (end_x, end_y), piece.image,
                from_r, from_c, to_r, to_c, duration=12
            )

            if captured_piece and captured_piece.image:
                captured_x = LEFT_PANEL + display_to_c * SQUARE_SIZE + 5
                captured_y = display_to_r * SQUARE_SIZE + 5
                capture_anim = CaptureAnimation(
                    (captured_x, captured_y), captured_piece.image, duration=12
                )
                self.capture_animations.append(capture_anim)
                self.add_particles(captured_x + 45, captured_y + 45)

            self.waiting_for_animation = True

    def update_animations(self):
        """
        Обновляет все анимации
        Возвращает True, если все анимации закончились
        """
        # Обновляем анимацию движения
        if self.move_animation and self.move_animation.is_finished():
            self.move_animation = None

        # Обновляем анимацию поворота
        if self.rotation_animation and self.rotation_animation.is_finished():
            self.rotation_animation = None

        # Если ждали анимацию и она закончилась
        if self.waiting_for_animation and not self.move_animation:
            self.waiting_for_animation = False
            if self.pending_rotation:
                self.start_rotation_animation()  # Запускаем анимацию поворота
                self.pending_rotation = False
            return True

        # Обновляем угол поворота если есть анимация
        if self.rotation_animation and not self.rotation_animation.is_finished():
            self.angle = self.rotation_animation.update()

        # Обновляем частицы
        self.particles = [p for p in self.particles if p.update()]

        # Обновляем анимации взятия
        self.capture_animations = [c for c in self.capture_animations if not c.is_finished()]

        # Обновляем вспышку шаха
        if self.check_flash:
            if not self.check_flash.update():
                self.check_flash = None

        return not self.waiting_for_animation and (not self.rotation_animation or self.rotation_animation.is_finished())

    def start_rotation_animation(self):
        """Запускает анимацию поворота доски"""
        if not self.vs_computer:
            target_angle = 180 - self.angle
            self.rotation_animation = BoardRotationAnimation(
                start_angle=self.angle,
                target_angle=target_angle,
                duration=ROTATE_STEP  # Используем ROTATE_STEP из констант
            )
            # Обновляем угол сразу, чтобы анимация начала работать
            self.angle = self.rotation_animation.update()

    def draw_panels(self):
        """Рисует боковые панели"""
        # ... (код без изменений) ...

    def draw_board(self):
        """Рисует шахматную доску"""
        start_x = LEFT_PANEL
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color,
                                 (start_x + col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        """Рисует все фигуры на доске"""
        start_x = LEFT_PANEL
        for row in range(8):
            for col in range(8):
                if not self.vs_computer and self.angle >= 90:
                    board_row = 7 - row
                    board_col = 7 - col
                else:
                    board_row = row
                    board_col = col
                piece = self.game.board[board_row][board_col]
                if piece and piece.image:
                    if self.move_animation and self.move_animation.active:
                        if (board_row, board_col) == (self.move_animation.from_row, self.move_animation.from_col):
                            continue
                    x = start_x + col * SQUARE_SIZE + 5
                    y = row * SQUARE_SIZE + 5
                    self.screen.blit(piece.image, (x, y))

        if self.move_animation:
            self.move_animation.draw(self.screen)

        for anim in self.capture_animations:
            anim.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

    def draw_highlights(self):
        """Рисует подсветку: выбранная фигура, возможные ходы, шах"""
        start_x = LEFT_PANEL
        if self.game.selected_piece and self.game.selected_pos is not None:
            sel_row, sel_col = self.game.selected_pos
            if not self.vs_computer and self.angle >= 90:
                display_row = 7 - sel_row
                display_col = 7 - sel_col
            else:
                display_row = sel_row
                display_col = sel_col
            pygame.draw.rect(self.screen, YELLOW,
                             (start_x + display_col * SQUARE_SIZE, display_row * SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE), 3)
            for move in self.game.valid_moves:
                if len(move) == 3:
                    move_row, move_col, _ = move
                else:
                    move_row, move_col = move
                if not self.vs_computer and self.angle >= 90:
                    display_move_row = 7 - move_row
                    display_move_col = 7 - move_col
                else:
                    display_move_row = move_row
                    display_move_col = move_col
                center_x = start_x + display_move_col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = display_move_row * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.draw.circle(self.screen, GREEN, (center_x, center_y), SQUARE_SIZE // 8)

        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece and piece.type == 'K' and self.game.is_check(piece.color):
                    if not self.vs_computer and self.angle >= 90:
                        display_row = 7 - row
                        display_col = 7 - col
                    else:
                        display_row = row
                        display_col = col
                    pygame.draw.rect(self.screen, RED,
                                     (start_x + display_col * SQUARE_SIZE, display_row * SQUARE_SIZE,
                                      SQUARE_SIZE, SQUARE_SIZE), 3)
                    if not self.check_flash:
                        self.check_flash = CheckFlash(duration=8)

    def draw_status(self):
        """Рисует статус игры (чей ход, шах, победа)"""
        start_x = LEFT_PANEL
        board_width = SQUARE_SIZE * 8
        center_x = start_x + board_width // 2

        color_names = {'white': 'БЕЛЫЕ', 'black': 'ЧЕРНЫЕ'}

        if self.game.game_over:
            if self.game.winner:
                winner_ru = color_names.get(self.game.winner, self.game.winner.upper())
                text = f"Победили {winner_ru}!"
            else:
                text = "Пат!"
        else:
            current_ru = "БЕЛЫЕ" if self.game.current_turn == 'white' else "ЧЕРНЫЕ"
            text = f"Ход: {current_ru}"
            if self.game.is_check(self.game.current_turn):
                text += " (ШАХ!)"

        text_surf = self.small_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 25))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
        pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10), 2)
        self.screen.blit(text_surf, text_rect)

        hint = self.small_font.render("ESC - меню, F11 - полный экран", True, WHITE)
        self.screen.blit(hint, (start_x + 10, WINDOW_HEIGHT - 25))

        if self.vs_computer:
            diff_text = self.small_font.render(f"Сложность: {self.ai_difficulty.upper()}", True, GOLD)
            self.screen.blit(diff_text, (start_x + board_width - 150, WINDOW_HEIGHT - 25))

    def show_game_over_dialog(self, score):
        """Показывает диалог окончания игры"""
        # ... (код без изменений) ...

    def get_board_coords(self, screen_row, screen_col):
        """Преобразует экранные координаты в координаты доски с учетом поворота"""
        if not self.vs_computer and self.angle >= 90:
            return 7 - screen_row, 7 - screen_col
        return screen_row, screen_col

    def computer_move(self):
        """Ход компьютера"""
        if self.game.game_over or self.game.current_turn != 'black':
            return False
        best_move = self.ai.get_best_move(self.game.board)
        if best_move:
            from_r, from_c, to_r, to_c = best_move
            self.game.selected_piece = self.game.board[from_r][from_c]
            self.game.selected_pos = (from_r, from_c)
            self.game.valid_moves = [(to_r, to_c)]
            success, captured, promotion = self.game.make_move(from_r, from_c, to_r, to_c)
            if success:
                self.start_move_animation(from_r, from_c, to_r, to_c, captured)
                if promotion == 'promotion':
                    self.game.board[to_r][to_c] = ChessPiece('Q', 'black', to_r, to_c)
                    self.game.board[to_r][to_c].load_image()
                if not self.vs_computer:
                    self.pending_rotation = True
            self.game.selected_piece = None
            self.game.selected_pos = None
            self.game.valid_moves = []
            return True
        return False

    def run(self):
        """Главный игровой цикл"""
        running = True
        ai_move_delay = 0
        final_score = None

        play_game_music()

        while running:
            # Обновляем анимации
            animations_finished = self.update_animations()

            # Ход компьютера (если нужно)
            if self.vs_computer and not self.game.game_over and self.game.current_turn == 'black' and animations_finished:
                if ai_move_delay <= 0:
                    self.computer_move()
                    ai_move_delay = 10
                else:
                    ai_move_delay -= 1

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game.game_over and animations_finished:
                    x, y = pygame.mouse.get_pos()
                    if LEFT_PANEL < x < WINDOW_WIDTH - RIGHT_PANEL:
                        screen_col = (x - LEFT_PANEL) // SQUARE_SIZE
                        screen_row = y // SQUARE_SIZE
                        if 0 <= screen_row < 8 and 0 <= screen_col < 8:
                            board_row, board_col = self.get_board_coords(screen_row, screen_col)
                            if self.game.selected_piece and self.game.selected_pos is not None:
                                from_r, from_c = self.game.selected_pos
                                player_color = self.game.current_turn
                                success, captured, promotion = self.game.make_move(from_r, from_c, board_row, board_col)
                                if success:
                                    self.start_move_animation(from_r, from_c, board_row, board_col, captured)
                                    if move_sound:
                                        move_sound.play()
                                    if promotion == 'promotion':
                                        dialog = PromotionDialog(self.screen, player_color)
                                        chosen_piece = dialog.run()
                                        self.game.board[board_row][board_col] = ChessPiece(
                                            chosen_piece, player_color, board_row, board_col
                                        )
                                        self.game.board[board_row][board_col].load_image()
                                    if not self.vs_computer:
                                        self.pending_rotation = True
                                else:
                                    self.game.select_piece(board_row, board_col)
                            else:
                                self.game.select_piece(board_row, board_col)

            # Проверка окончания игры
            if self.game.game_over and animations_finished:
                if self.vs_computer and self.game.winner == 'white':
                    final_score = self.game.calculate_score()
                else:
                    final_score = None
                self.show_game_over_dialog(final_score if final_score else 0)
                if self.vs_computer and self.game.winner == 'white':
                    return final_score
                else:
                    return None

            # Отрисовка
            if self.check_flash:
                self.check_flash.draw(self.screen)

            self.draw_panels()
            self.draw_board()
            self.draw_pieces()
            self.draw_highlights()
            self.draw_status()

            pygame.display.flip()
            self.clock.tick(60)

        return None