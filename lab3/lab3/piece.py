import pygame
import os
from constants import SQUARE_SIZE


class ChessPiece:
    def __init__(self, piece_type, color, row, col):
        self.type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False
        self.image = None
        self.small_image = None
        self.load_image()

    def load_image(self):
        size = SQUARE_SIZE - 10
        small_size = 45
        filename = f"assets/pieces/{self.color}_{self.type}.png"
        if os.path.exists(filename):
            try:
                img = pygame.image.load(filename)
                self.image = pygame.transform.scale(img, (size, size))
                self.small_image = pygame.transform.scale(img, (small_size, small_size))
                return
            except:
                pass
        self.create_text_piece()

    def create_text_piece(self):
        size = SQUARE_SIZE - 10
        small_size = 45
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.small_image = pygame.Surface((small_size, small_size), pygame.SRCALPHA)

        if self.color == 'white':
            bg_color = (245, 245, 245)
            text_color = (0, 0, 0)
        else:
            bg_color = (60, 60, 60)
            text_color = (255, 255, 255)

        self.image.fill(bg_color)
        self.small_image.fill(bg_color)

        font = pygame.font.Font(None, 45)
        small_font = pygame.font.Font(None, 35)

        text = font.render(self.type, True, text_color)
        text_rect = text.get_rect(center=(size // 2, size // 2))
        self.image.blit(text, text_rect)

        small_text = small_font.render(self.type, True, text_color)
        small_text_rect = small_text.get_rect(center=(small_size // 2, small_size // 2))
        self.small_image.blit(small_text, small_text_rect)

        pygame.draw.rect(self.image, text_color, self.image.get_rect(), 2)
        pygame.draw.rect(self.small_image, text_color, self.small_image.get_rect(), 1)

    def get_possible_moves(self, board):
        moves = []

        if self.type == 'P':
            direction = -1 if self.color == 'white' else 1
            new_row = self.row + direction

            if 0 <= new_row < 8 and board[new_row][self.col] is None:
                if (self.color == 'white' and new_row == 0) or (self.color == 'black' and new_row == 7):
                    moves.append((new_row, self.col, 'promotion'))
                else:
                    moves.append((new_row, self.col))

                if not self.has_moved:
                    new_row2 = self.row + 2 * direction
                    if 0 <= new_row2 < 8 and board[new_row2][self.col] is None:
                        moves.append((new_row2, self.col))

            for dc in [-1, 1]:
                new_col = self.col + dc
                new_row = self.row + direction
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = board[new_row][new_col]
                    if target and target.color != self.color:
                        if (self.color == 'white' and new_row == 0) or (self.color == 'black' and new_row == 7):
                            moves.append((new_row, new_col, 'promotion'))
                        else:
                            moves.append((new_row, new_col))

        elif self.type == 'R':
            for r in range(self.row - 1, -1, -1):
                if board[r][self.col] is None:
                    moves.append((r, self.col))
                else:
                    if board[r][self.col].color != self.color:
                        moves.append((r, self.col))
                    break
            for r in range(self.row + 1, 8):
                if board[r][self.col] is None:
                    moves.append((r, self.col))
                else:
                    if board[r][self.col].color != self.color:
                        moves.append((r, self.col))
                    break
            for c in range(self.col - 1, -1, -1):
                if board[self.row][c] is None:
                    moves.append((self.row, c))
                else:
                    if board[self.row][c].color != self.color:
                        moves.append((self.row, c))
                    break
            for c in range(self.col + 1, 8):
                if board[self.row][c] is None:
                    moves.append((self.row, c))
                else:
                    if board[self.row][c].color != self.color:
                        moves.append((self.row, c))
                    break

        elif self.type == 'N':
            offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for dr, dc in offsets:
                new_r, new_c = self.row + dr, self.col + dc
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    target = board[new_r][new_c]
                    if target is None or target.color != self.color:
                        moves.append((new_r, new_c))

        elif self.type == 'B':
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        moves.append((r, c))
                    else:
                        if board[r][c].color != self.color:
                            moves.append((r, c))
                        break
                    r += dr
                    c += dc

        elif self.type == 'Q':
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        moves.append((r, c))
                    else:
                        if board[r][c].color != self.color:
                            moves.append((r, c))
                        break
                    r += dr
                    c += dc

        elif self.type == 'K':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_r, new_c = self.row + dr, self.col + dc
                    if 0 <= new_r < 8 and 0 <= new_c < 8:
                        target = board[new_r][new_c]
                        if target is None or target.color != self.color:
                            moves.append((new_r, new_c))

            if not self.has_moved:
                if self.color == 'white':
                    row = 7
                else:
                    row = 0

                right_rook = board[row][7]
                if right_rook and right_rook.type == 'R' and not right_rook.has_moved:
                    empty = True
                    for c in range(self.col + 1, 7):
                        if board[row][c] is not None:
                            empty = False
                            break
                    if empty:
                        moves.append((row, 6))

                left_rook = board[row][0]
                if left_rook and left_rook.type == 'R' and not left_rook.has_moved:
                    empty = True
                    for c in range(1, self.col):
                        if board[row][c] is not None:
                            empty = False
                            break
                    if empty:
                        moves.append((row, 2))

        return moves