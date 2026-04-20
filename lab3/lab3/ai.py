import random
from constants import PIECE_VALUES, AI_DEPTHS


class ChessAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.piece_values = PIECE_VALUES
        self.max_depth = AI_DEPTHS.get(difficulty, 2)

    def evaluate_board(self, board):
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece:
                    value = self.piece_values.get(piece.type, 0)
                    if piece.color == 'black':
                        score += value
                    else:
                        score -= value
        return score

    def get_all_moves(self, board, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color == color:
                    all_moves = piece.get_possible_moves(board)
                    for mr, mc in all_moves:
                        if self.is_move_safe(board, row, col, mr, mc, color):
                            moves.append((row, col, mr, mc))
        return moves

    def is_move_safe(self, board, from_r, from_c, to_r, to_c, color):
        piece = board[from_r][from_c]
        if not piece or piece.color != color:
            return False

        # Для рокировки особая проверка
        if piece.type == 'K' and abs(to_c - from_c) == 2:
            return True

        captured = board[to_r][to_c]
        board[to_r][to_c] = piece
        board[from_r][from_c] = None
        old_r, old_c = piece.row, piece.col
        piece.row, piece.col = to_r, to_c
        in_check = self.is_check(board, color)
        board[from_r][from_c] = piece
        board[to_r][to_c] = captured
        piece.row, piece.col = old_r, old_c
        return not in_check

    def is_check(self, board, color):
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.type == 'K' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        if not king_pos:
            return False
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color != color:
                    if king_pos in piece.get_possible_moves(board):
                        return True
        return False

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0:
            return self.evaluate_board(board)
        if is_maximizing:
            max_score = -float('inf')
            moves = self.get_all_moves(board, 'black')
            for move in moves:
                from_r, from_c, to_r, to_c = move
                piece = board[from_r][from_c]
                captured = board[to_r][to_c]
                board[to_r][to_c] = piece
                board[from_r][from_c] = None
                old_r, old_c = piece.row, piece.col
                piece.row, piece.col = to_r, to_c
                score = self.minimax(board, depth - 1, alpha, beta, False)
                board[from_r][from_c] = piece
                board[to_r][to_c] = captured
                piece.row, piece.col = old_r, old_c
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            moves = self.get_all_moves(board, 'white')
            for move in moves:
                from_r, from_c, to_r, to_c = move
                piece = board[from_r][from_c]
                captured = board[to_r][to_c]
                board[to_r][to_c] = piece
                board[from_r][from_c] = None
                old_r, old_c = piece.row, piece.col
                piece.row, piece.col = to_r, to_c
                score = self.minimax(board, depth - 1, alpha, beta, True)
                board[from_r][from_c] = piece
                board[to_r][to_c] = captured
                piece.row, piece.col = old_r, old_c
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score

    def get_best_move(self, board):
        moves = self.get_all_moves(board, 'black')
        if not moves:
            return None
        if self.difficulty == 'easy':
            return random.choice(moves)
        best_move = None
        best_score = -float('inf')
        for move in moves:
            from_r, from_c, to_r, to_c = move
            piece = board[from_r][from_c]
            captured = board[to_r][to_c]
            board[to_r][to_c] = piece
            board[from_r][from_c] = None
            old_r, old_c = piece.row, piece.col
            piece.row, piece.col = to_r, to_c
            score = self.minimax(board, self.max_depth - 1, -float('inf'), float('inf'), False)
            board[from_r][from_c] = piece
            board[to_r][to_c] = captured
            piece.row, piece.col = old_r, old_c
            if score > best_score:
                best_score = score
                best_move = move
        return best_move