import pygame
import threading
from constants import *
from game_logic import ChessGame
from sound import move_sound, win_sound, lose_sound, play_game_music
from animations import MoveAnimation, CaptureAnimation, Particle, CheckFlash
from network import Network
from piece import ChessPiece
import os


class PromotionDialog:
    # Тот же класс, что и в ui.py
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color
        self.selected = None
        self.running = True
        self.small_font = pygame.font.Font(None, 20)

        self.width = 400
        self.height = 180
        self.x = (WINDOW_WIDTH - self.width) // 2
        self.y = (WINDOW_HEIGHT - self.height) // 2

        self.pieces = ['Q', 'R', 'B', 'N']
        self.piece_names = {'Q': 'Ферзь', 'R': 'Ладья', 'B': 'Слон', 'N': 'Конь'}

        self.images = []
        for piece in self.pieces:
            filename = f"assets/pieces/{color}_{piece}.png"
            if os.path.exists(filename):
                try:
                    img = pygame.image.load(filename)
                    img = pygame.transform.scale(img, (60, 60))
                    self.images.append(img)
                except:
                    self.create_text_image(piece)
            else:
                self.create_text_image(piece)

        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)

    def create_text_image(self, piece):
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        symbols = {'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'}
        font = pygame.font.Font(None, 50)
        text_color = (255, 255, 255) if self.color == 'black' else (0, 0, 0)
        text = font.render(symbols[piece], True, text_color)
        text_rect = text.get_rect(center=(30, 30))
        surf.blit(text, text_rect)
        self.images.append(surf)

    def draw(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, GOLD, (self.x, self.y, self.width, self.height), 3)

        title = self.title_font.render("ВЫБЕРИТЕ ФИГУРУ", True, GOLD)
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 40))
        self.screen.blit(title, title_rect)

        button_width = 70
        button_height = 70
        start_x = self.x + (self.width - (4 * button_width + 30)) // 2
        button_y = self.y + 80

        for i, (piece, img) in enumerate(zip(self.pieces, self.images)):
            button_x = start_x + i * (button_width + 10)

            pygame.draw.rect(self.screen, GRAY, (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, WHITE, (button_x, button_y, button_width, button_height), 2)

            self.screen.blit(img, (button_x + 5, button_y + 5))

            name = self.piece_names[piece]
            name_text = self.small_font.render(name, True, WHITE)
            name_rect = name_text.get_rect(center=(button_x + button_width // 2, button_y + button_height + 15))
            self.screen.blit(name_text, name_rect)

        hint = self.small_font.render("Нажмите 1-4 или кликните на фигуру", True, WHITE)
        hint_rect = hint.get_rect(center=(self.x + self.width // 2, self.y + self.height - 15))
        self.screen.blit(hint, hint_rect)

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            button_width = 70
            button_height = 70
            start_x = self.x + (self.width - (4 * button_width + 30)) // 2
            button_y = self.y + 80

            for i in range(4):
                button_x = start_x + i * (button_width + 10)
                if (button_x <= x <= button_x + button_width and
                        button_y <= y <= button_y + button_height):
                    self.selected = self.pieces[i]
                    self.running = False
                    return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.selected = 'Q'
                self.running = False
                return True
            elif event.key == pygame.K_2:
                self.selected = 'R'
                self.running = False
                return True
            elif event.key == pygame.K_3:
                self.selected = 'B'
                self.running = False
                return True
            elif event.key == pygame.K_4:
                self.selected = 'N'
                self.running = False
                return True

        return False

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'Q'
                self.handle_event(event)

            self.draw()
            clock.tick(60)

        return self.selected if self.selected else 'Q'


class OnlineGame:
    def __init__(self, screen, network, player_color):
        self.screen = screen
        self.network = network
        self.player_color = player_color
        self.game = ChessGame()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 72)

        if player_color == 'white':
            self.my_turn = True
        else:
            self.my_turn = False
        self.game.current_turn = 'white'

        self.running = True
        self.game_over = False
        self.winner = None
        self.opponent_disconnected = False
        self.dialog_shown = False

        self.move_animation = None
        self.capture_animations = []
        self.particles = []
        self.check_flash = None
        self.waiting_for_animation = False
        self.pending_rotation = False

        if player_color == 'black':
            self.angle = 180
        else:
            self.angle = 0
        self.target_angle = 0
        self.waiting_for_rotation = False

        print(f"Твой цвет: {player_color}")
        print(f"Твой ход: {self.my_turn}")

        play_game_music()

        self.receive_thread = threading.Thread(target=self.receive_moves, daemon=True)
        self.receive_thread.start()

    def receive_moves(self):
        while self.running:
            data = self.network.receive()
            if data:
                print(f"Получено от сервера: {data}")
                if data.get('type') == 'move':
                    from_r, from_c, to_r, to_c = data['move']
                    piece = self.game.board[from_r][from_c]
                    if piece:
                        self.game.selected_piece = piece
                        self.game.selected_pos = (from_r, from_c)
                        self.game.valid_moves = self.game.get_valid_moves_for_piece(from_r, from_c)

                        is_valid = False
                        for move in self.game.valid_moves:
                            if len(move) == 3:
                                mr, mc, _ = move
                                if mr == to_r and mc == to_c:
                                    is_valid = True
                                    break
                            else:
                                mr, mc = move
                                if mr == to_r and mc == to_c:
                                    is_valid = True
                                    break

                        if is_valid:
                            success, captured, promotion = self.game.make_move(from_r, from_c, to_r, to_c)
                            if success:
                                self.my_turn = True
                                print(f"Противник сходил. Теперь твой ход!")
                                self.start_move_animation(from_r, from_c, to_r, to_c, captured)
                                self.check_game_over()
                elif data.get('type') == 'game_over':
                    self.game_over = True
                    self.winner = data.get('winner')
                elif data.get('type') == 'disconnect':
                    self.opponent_disconnected = True
                    self.running = False

    def start_move_animation(self, from_r, from_c, to_r, to_c, captured_piece=None):
        if self.player_color == 'black':
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
                for _ in range(15):
                    self.particles.append(Particle(captured_x + 45, captured_y + 45, ORANGE))
            self.waiting_for_animation = True

    def check_game_over(self):
        if self.game.game_over:
            self.game_over = True
            self.winner = self.game.winner
            score = self.game.calculate_score()
            self.network.send({'type': 'game_over', 'winner': self.winner, 'score': score})

    def rotate_board(self):
        self.target_angle = 180 - self.angle
        self.waiting_for_rotation = True

    def update_rotation(self):
        if self.waiting_for_rotation:
            step = 10
            if self.angle < self.target_angle:
                self.angle = min(self.angle + step, self.target_angle)
                if self.angle >= self.target_angle:
                    self.waiting_for_rotation = False
            elif self.angle > self.target_angle:
                self.angle = max(self.angle - step, self.target_angle)
                if self.angle <= self.target_angle:
                    self.waiting_for_rotation = False

    def update_animations(self):
        if self.move_animation and self.move_animation.is_finished():
            self.move_animation = None
        if self.waiting_for_animation and not self.move_animation:
            self.waiting_for_animation = False
            if self.pending_rotation:
                self.rotate_board()
                self.pending_rotation = False
            return True
        self.particles = [p for p in self.particles if p.update()]
        self.capture_animations = [c for c in self.capture_animations if not c.is_finished()]
        if self.check_flash:
            if not self.check_flash.update():
                self.check_flash = None
        return not self.waiting_for_animation

    def draw_panels(self):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, LEFT_PANEL, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, GOLD, (LEFT_PANEL, 0), (LEFT_PANEL, WINDOW_HEIGHT), 3)
        pygame.draw.rect(self.screen, DARK_GRAY, (WINDOW_WIDTH - RIGHT_PANEL, 0, RIGHT_PANEL, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, GOLD, (WINDOW_WIDTH - RIGHT_PANEL, 0),
                         (WINDOW_WIDTH - RIGHT_PANEL, WINDOW_HEIGHT), 3)

        title1 = self.small_font.render("ВЗЯЛ", True, GOLD)
        title1_rect = title1.get_rect(center=(LEFT_PANEL // 2, 30))
        self.screen.blit(title1, title1_rect)
        title2 = self.small_font.render("ПРОТИВНИК", True, GOLD)
        title2_rect = title2.get_rect(center=(LEFT_PANEL // 2, 50))
        self.screen.blit(title2, title2_rect)

        title3 = self.small_font.render("ВЗЯЛ", True, GOLD)
        title3_rect = title3.get_rect(center=(WINDOW_WIDTH - RIGHT_PANEL // 2, 30))
        self.screen.blit(title3, title3_rect)
        title4 = self.small_font.render("ВЫ", True, GOLD)
        title4_rect = title4.get_rect(center=(WINDOW_WIDTH - RIGHT_PANEL // 2, 50))
        self.screen.blit(title4, title4_rect)

        y_offset = 85
        x_center = LEFT_PANEL // 2 - 15
        for i, piece in enumerate(self.game.captured_by_computer):
            y = y_offset + i * 35
            if y < WINDOW_HEIGHT - 60 and piece.small_image:
                small_img = pygame.transform.scale(piece.small_image, (30, 30))
                self.screen.blit(small_img, (x_center, y))

        x_center = WINDOW_WIDTH - RIGHT_PANEL + (RIGHT_PANEL // 2 - 15)
        for i, piece in enumerate(self.game.captured_by_player):
            y = y_offset + i * 35
            if y < WINDOW_HEIGHT - 60 and piece.small_image:
                small_img = pygame.transform.scale(piece.small_image, (30, 30))
                self.screen.blit(small_img, (x_center, y))

    def draw_board(self):
        start_x = LEFT_PANEL
        for row in range(8):
            for col in range(8):
                if self.player_color == 'black':
                    draw_row = 7 - row
                    draw_col = 7 - col
                else:
                    draw_row = row
                    draw_col = col
                color = LIGHT_BROWN if (draw_row + draw_col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color,
                                 (start_x + col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        start_x = LEFT_PANEL
        for row in range(8):
            for col in range(8):
                if self.player_color == 'black':
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
        start_x = LEFT_PANEL
        if self.game.selected_piece and self.game.selected_pos is not None:
            sel_row, sel_col = self.game.selected_pos
            if self.player_color == 'black':
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
                if self.player_color == 'black':
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
                    if self.player_color == 'black':
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
        start_x = LEFT_PANEL
        board_width = SQUARE_SIZE * 8
        center_x = start_x + board_width // 2

        if self.game_over:
            if self.winner == self.player_color:
                text = "ВЫ ПОБЕДИЛИ!"
                text_color = GREEN
            elif self.winner:
                text = "ВЫ ПРОИГРАЛИ!"
                text_color = RED
            else:
                text = "ПАТ! НИЧЬЯ!"
                text_color = YELLOW
        elif self.my_turn:
            text = "ВАШ ХОД"
            text_color = GREEN
        else:
            text = "ХОД ПРОТИВНИКА..."
            text_color = YELLOW

        text_surf = self.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(center_x, WINDOW_HEIGHT - 25))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
        pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10), 2)
        self.screen.blit(text_surf, text_rect)

        hint = self.small_font.render("ESC - меню", True, WHITE)
        self.screen.blit(hint, (start_x + 10, WINDOW_HEIGHT - 25))

    def get_board_coords(self, screen_row, screen_col):
        if self.player_color == 'black':
            return 7 - screen_row, 7 - screen_col
        return screen_row, screen_col

    def run(self):
        score = None
        while self.running:
            self.update_rotation()
            self.update_animations()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.my_turn:
                    x, y = pygame.mouse.get_pos()
                    if LEFT_PANEL < x < WINDOW_WIDTH - RIGHT_PANEL:
                        screen_col = (x - LEFT_PANEL) // SQUARE_SIZE
                        screen_row = y // SQUARE_SIZE
                        if 0 <= screen_row < 8 and 0 <= screen_col < 8:
                            board_row, board_col = self.get_board_coords(screen_row, screen_col)

                            self.game.select_piece(board_row, board_col)

                            if self.game.selected_piece and self.game.selected_pos is not None:
                                from_r, from_c = self.game.selected_pos

                                # СОХРАНЯЕМ ЦВЕТ ИГРОКА ДО ХОДА
                                player_color = self.player_color

                                # Проверяем, является ли клик допустимым ходом
                                is_valid = False
                                for move in self.game.valid_moves:
                                    if len(move) == 3:
                                        mr, mc, _ = move
                                        if mr == board_row and mc == board_col:
                                            is_valid = True
                                            break
                                    else:
                                        mr, mc = move
                                        if mr == board_row and mc == board_col:
                                            is_valid = True
                                            break

                                if is_valid:
                                    success, captured, promotion = self.game.make_move(from_r, from_c, board_row, board_col)
                                    if success:
                                        if move_sound:
                                            move_sound.play()
                                        self.network.send(
                                            {'type': 'move', 'move': (from_r, from_c, board_row, board_col)})
                                        self.my_turn = False
                                        self.start_move_animation(from_r, from_c, board_row, board_col, captured)

                                        # ОБРАБОТКА ПРЕВРАЩЕНИЯ С ПРАВИЛЬНЫМ ЦВЕТОМ
                                        if promotion == 'promotion':
                                            dialog = PromotionDialog(self.screen, player_color)
                                            chosen_piece = dialog.run()
                                            self.game.board[board_row][board_col] = ChessPiece(
                                                chosen_piece,
                                                player_color,
                                                board_row,
                                                board_col
                                            )
                                            self.game.board[board_row][board_col].load_image()

                                        self.check_game_over()
                                        self.game.selected_piece = None
                                        self.game.selected_pos = None
                                        self.game.valid_moves = []

            if self.game_over and not self.dialog_shown:
                self.dialog_shown = True
                if self.winner == self.player_color:
                    if win_sound:
                        win_sound.play()
                    message = "ВЫ ПОБЕДИЛИ!"
                    message_color = GREEN
                    score = self.game.calculate_score()
                elif self.winner:
                    if lose_sound:
                        lose_sound.play()
                    message = "ВЫ ПРОИГРАЛИ!"
                    message_color = RED
                    score = None
                else:
                    message = "ПАТ! НИЧЬЯ!"
                    message_color = YELLOW
                    score = None

                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                text_surf = self.big_font.render(message, True, message_color)
                text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
                self.screen.blit(text_surf, text_rect)

                if score is not None:
                    score_text = self.font.render(f"Ваши очки: {score}", True, WHITE)
                    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
                    self.screen.blit(score_text, score_rect)

                info_text = self.small_font.render("Нажмите любую клавишу для продолжения", True, WHITE)
                info_rect = info_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
                self.screen.blit(info_text, info_rect)

                pygame.display.flip()

                waiting = True
                while waiting:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            return None
                        if ev.type == pygame.KEYDOWN:
                            waiting = False
                        if ev.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                    self.clock.tick(60)

                return score

            if self.opponent_disconnected:
                font = pygame.font.Font(None, 36)
                text = font.render("ПРОТИВНИК ОТКЛЮЧИЛСЯ", True, RED)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(2000)
                return None

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