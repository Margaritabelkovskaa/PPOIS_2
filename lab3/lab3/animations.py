import pygame
import random
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, ORANGE, RED, ROTATE_STEP


class MoveAnimation:
    """Анимация плавного перемещения фигуры"""

    def __init__(self, from_pos, to_pos, piece_image, from_row, from_col, to_row, to_col, duration=15):
        self.from_x, self.from_y = from_pos
        self.to_x, self.to_y = to_pos
        self.piece_image = piece_image
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.duration = duration
        self.current_step = 0
        self.active = True

    def update(self):
        if not self.active:
            return None, None, None

        self.current_step += 1
        if self.current_step >= self.duration:
            self.active = False
            return (self.to_x, self.to_y), self.to_row, self.to_col

        t = self.current_step / self.duration
        t = 1 - (1 - t) ** 2  # ease-out

        x = self.from_x + (self.to_x - self.from_x) * t
        y = self.from_y + (self.to_y - self.from_y) * t
        return (x, y), self.from_row, self.from_col

    def draw(self, screen):
        if self.active:
            pos, _, _ = self.update()
            if pos:
                screen.blit(self.piece_image, pos)

    def is_finished(self):
        return not self.active


class CaptureAnimation:
    """Анимация взятия фигуры (вращение и уменьшение)"""

    def __init__(self, pos, piece_image, duration=15):
        self.x, self.y = pos
        self.original_image = piece_image
        self.duration = duration
        self.current_step = 0
        self.active = True
        self.angle = 0
        self.scale = 1.0

    def update(self):
        if not self.active:
            return None

        self.current_step += 1
        if self.current_step >= self.duration:
            self.active = False
            return None

        t = self.current_step / self.duration
        self.angle = t * 360
        self.scale = 1.0 - t
        return (self.x, self.y)

    def draw(self, screen):
        if self.active:
            pos = self.update()
            if pos:
                size = self.original_image.get_size()
                new_size = (int(size[0] * self.scale), int(size[1] * self.scale))
                if new_size[0] > 0 and new_size[1] > 0:
                    scaled = pygame.transform.scale(self.original_image, new_size)
                    rotated = pygame.transform.rotate(scaled, self.angle)
                    rect = rotated.get_rect(center=(pos[0] + size[0] // 2, pos[1] + size[1] // 2))
                    screen.blit(rotated, rect)

    def is_finished(self):
        return not self.active


class Particle:
    """Частица для эффекта взрыва при взятии"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-12, -3)
        self.color = color
        self.lifetime = 40
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.6
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = min(255, int(255 * self.lifetime / 40))
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class CheckFlash:
    """Вспышка экрана при шахе"""

    def __init__(self, duration=8):
        self.duration = duration
        self.current_step = 0
        self.active = True

    def update(self):
        self.current_step += 1
        if self.current_step >= self.duration:
            self.active = False
        return self.active

    def draw(self, screen):
        if self.active:
            alpha = int(120 * (1 - self.current_step / self.duration))
            flash_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, alpha))
            screen.blit(flash_surf, (0, 0))


class BoardRotationAnimation:
    """
    Анимация поворота доски
    Плавно изменяет угол от start_angle до target_angle
    """

    def __init__(self, start_angle, target_angle, duration=18):
        """
        start_angle: начальный угол (0 или 180)
        target_angle: целевой угол (180 или 0)
        duration: длительность анимации в кадрах
        """
        self.start_angle = start_angle
        self.target_angle = target_angle
        self.duration = duration
        self.current_step = 0
        self.active = True
        self.current_angle = start_angle

        # Шаг изменения угла за кадр
        self.step = (target_angle - start_angle) / duration

    def update(self):
        """
        Обновляет анимацию
        Возвращает текущий угол поворота
        """
        if not self.active:
            return self.target_angle

        self.current_step += 1

        if self.current_step >= self.duration:
            self.active = False
            return self.target_angle

        # Плавное изменение угла
        t = self.current_step / self.duration
        # Используем ease-out для более естественной анимации
        t = 1 - (1 - t) ** 2
        self.current_angle = self.start_angle + (self.target_angle - self.start_angle) * t

        return self.current_angle

    def draw(self, screen):
        """
        Анимация поворота не рисует ничего сама,
        этот метод нужен только для совместимости с другими анимациями
        """
        pass

    def is_finished(self):
        """Проверяет, закончилась ли анимация"""
        return not self.active

    def get_current_angle(self):
        """Возвращает текущий угол поворота"""
        return self.current_angle if self.active else self.target_angle


class CompositeAnimation:
    """
    Композитная анимация - управляет несколькими анимациями одновременно
    """

    def __init__(self):
        self.animations = []
        self.active = True

    def add_animation(self, animation):
        """Добавляет анимацию в композит"""
        self.animations.append(animation)

    def update(self):
        """Обновляет все анимации"""
        all_finished = True

        for anim in self.animations:
            if not anim.is_finished():
                anim.update()
                all_finished = False

        if all_finished:
            self.active = False

        return self.active

    def is_finished(self):
        """Проверяет, закончились ли все анимации"""
        return not self.active

    def draw(self, screen):
        """Рисует все анимации"""
        for anim in self.animations:
            anim.draw(screen)

    def get_rotation_angle(self):
        """
        Возвращает текущий угол поворота из анимации поворота (если есть)
        """
        for anim in self.animations:
            if isinstance(anim, BoardRotationAnimation):
                return anim.get_current_angle()
        return 0