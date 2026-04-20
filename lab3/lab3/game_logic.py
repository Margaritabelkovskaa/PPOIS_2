from piece import ChessPiece
from sound import move_sound


class ChessGame:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.captured_by_computer = []
        self.captured_by_player = []
        self.move_count = 0
        self.init_board()

    def init_board(self):
        pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i, p in enumerate(pieces):
            self.board[0][i] = ChessPiece(p, 'black', 0, i)
            self.board[7][i] = ChessPiece(p, 'white', 7, i)
        for i in range(8):
            self.board[1][i] = ChessPiece('P', 'black', 1, i)
            self.board[6][i] = ChessPiece('P', 'white', 6, i)

    def calculate_score(self):
        """Возвращает очки только если выиграли белые (игрок)"""
        if not self.game_over or self.winner != 'white':
            return 0
        return max(0, 200 - self.move_count)

    def is_square_attacked(self, row, col, color):
        """Проверяет, атакована ли клетка"""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color != color:
                    moves = piece.get_possible_moves(self.board)
                    for move in moves:
                        if len(move) == 3:
                            move_row, move_col, _ = move
                        else:
                            move_row, move_col = move
                        if (move_row, move_col) == (row, col):
                            return True
        return False

    def is_check(self, color):
        """Проверяет, находится ли король под шахом"""
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.type == 'K' and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        return self.is_square_attacked(king_pos[0], king_pos[1], color)

    def is_move_safe(self, from_r, from_c, to_r, to_c, color):
        """Проверяет, не приводит ли ход к шаху"""
        piece = self.board[from_r][from_c]
        if not piece or piece.color != color:
            return False

        # Для рокировки особая проверка
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            step = 1 if to_c > from_c else -1
            for c in range(from_c, to_c + step, step):
                if self.is_square_attacked(from_r, c, color):
                    return False
            return True

        captured = self.board[to_r][to_c]
        self.board[to_r][to_c] = piece
        self.board[from_r][from_c] = None
        old_r, old_c = piece.row, piece.col
        piece.row, piece.col = to_r, to_c
        in_check = self.is_check(color)
        self.board[from_r][from_c] = piece
        self.board[to_r][to_c] = captured
        piece.row, piece.col = old_r, old_c
        return not in_check

    def get_valid_moves_for_piece(self, row, col):
        """Возвращает все безопасные ходы для фигуры"""
        piece = self.board[row][col]
        if not piece:
            return []
        safe_moves = []
        for move in piece.get_possible_moves(self.board):
            if len(move) == 3:
                mr, mc, promo = move
                if self.is_move_safe(row, col, mr, mc, piece.color):
                    safe_moves.append((mr, mc, promo))
            else:
                mr, mc = move
                if self.is_move_safe(row, col, mr, mc, piece.color):
                    safe_moves.append((mr, mc))
        return safe_moves

    def has_any_moves(self, color):
        """Проверяет, есть ли у игрока хоть один ход"""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    if self.get_valid_moves_for_piece(r, c):
                        return True
        return False

    def make_move(self, from_r, from_c, to_r, to_c):
        """Выполняет ход"""
        piece = self.board[from_r][from_c]
        if not piece or piece.color != self.current_turn:
            return False, None, None

        # Проверяем, допустим ли ход
        is_valid = False
        is_promotion = False
        for move in self.valid_moves:
            if len(move) == 3:
                mr, mc, promo = move
                if mr == to_r and mc == to_c:
                    is_valid = True
                    is_promotion = True
                    break
            else:
                mr, mc = move
                if mr == to_r and mc == to_c:
                    is_valid = True
                    break

        if not is_valid:
            return False, None, None

        # Сохраняем кто ходил ДО выполнения хода
        moved_player = self.current_turn

        # Сохраняем взятую фигуру
        captured = self.board[to_r][to_c]
        captured_info = captured if captured else None

        # Проверка на рокировку
        is_castle = False
        rook = None
        rook_from_c = None
        rook_to_c = None

        if piece.type == 'K' and abs(to_c - from_c) == 2:
            is_castle = True
            if to_c > from_c:
                rook_from_c = 7
                rook_to_c = 5
            else:
                rook_from_c = 0
                rook_to_c = 3
            rook = self.board[to_r][rook_from_c]

        # Выполняем ход короля
        self.board[to_r][to_c] = piece
        self.board[from_r][from_c] = None
        piece.row, piece.col = to_r, to_c
        piece.has_moved = True

        # Звук хода
        if move_sound:
            move_sound.play()

        # Выполняем рокировку
        if is_castle and rook and rook.type == 'R' and not rook.has_moved:
            self.board[to_r][rook_to_c] = rook
            self.board[to_r][rook_from_c] = None
            rook.row = to_r
            rook.col = rook_to_c
            rook.has_moved = True

        # Добавляем взятую фигуру в список
        if captured:
            if captured.color == 'white':
                self.captured_by_computer.append(captured)
            else:
                self.captured_by_player.append(captured)

        self.move_count += 1

        # Меняем игрока
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Проверяем, есть ли ходы у следующего игрока
        has_moves = self.has_any_moves(self.current_turn)

        # Если у игрока нет ходов - это мат или пат
        if not has_moves:
            self.game_over = True
            # Проверяем шах для игрока, который не может ходить
            if self.is_check(self.current_turn):
                # Тот, кто сделал последний ход, выиграл
                self.winner = moved_player
                print(f"МАТ! {self.winner.upper()} ПОБЕДИЛИ!")
            else:
                self.winner = None
                print("ПАТ! НИЧЬЯ!")

        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []

        if is_promotion and piece.type == 'P':
            return True, captured_info, 'promotion'
        return True, captured_info, None

    def select_piece(self, row, col):
        """Выбирает фигуру"""
        if self.game_over:
            return
        piece = self.board[row][col]

        if self.selected_piece:
            if self.selected_pos == (row, col):
                self.selected_piece = None
                self.selected_pos = None
                self.valid_moves = []
            elif piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.selected_pos = (row, col)
                self.valid_moves = self.get_valid_moves_for_piece(row, col)
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.selected_pos = (row, col)
                self.valid_moves = self.get_valid_moves_for_piece(row, col)