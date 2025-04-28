# robot.py
import pygame
import random
from collections import deque

# Colores
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)      # FREE
ORANGE = (255, 165, 0)   # PICKUP
RED = (255, 0, 0)        # DELIVERING

# Estados
FREE = "FREE"
PICKUP = "PICKUP"
DELIVERING = "DELIVERING"

class Robot:
    def __init__(self, grid_x, grid_y, radius, grid):
        # Posición en la cuadrícula
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Posición en píxeles (para dibujar)
        self.x = (grid_x + 0.5) * grid.cell_size
        self.y = (grid_y + 0.5) * grid.cell_size
        self.target_x = self.x
        self.target_y = self.y
        self.radius = radius
        self.grid = grid

        # Animación
        self.animating = False
        self.animation_speed = 5

        # Ruta planificada + recuperación
        self.path = []
        self.recovery_stack = []
        self.in_collision_avoidance = False

        # Estado y carga
        self.state = FREE
        self.carrying_item = None

        # Punteros a objetivo de pickup/delivery
        self.pickup_target = None
        self.delivery_target = None

        # Marcar en matriz
        self.grid.matrix[self.grid_y][self.grid_x] = "*"

    def draw(self, screen):
        # Cuerpo
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius)
        # Sombrero según estado
        if self.state == FREE:
            hat = GREEN
        elif self.state == PICKUP:
            hat = ORANGE
        else:
            hat = RED
        hw, hh = self.radius * 1.2, self.radius * 0.5
        pygame.draw.rect(
            screen,
            hat,
            (self.x - hw / 2, self.y - self.radius - hh, hw, hh)
        )

    def set_state(self, new_state):
        self.state = new_state

    def update(self):
        if not self.animating:
            return
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        if abs(dx) < self.animation_speed and abs(dy) < self.animation_speed:
            self.x, self.y = self.target_x, self.target_y
            self.animating = False
        else:
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            self.x += dx / dist * self.animation_speed
            self.y += dy / dist * self.animation_speed

    # ---------- Movimientos básicos ----------
    def _move_up(self):
        if self.animating: return False
        if self.grid_y > 0 and self.grid.matrix[self.grid_y - 1][self.grid_x] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_y -= 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_y = (self.grid_y + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_down(self):
        if self.animating: return False
        if self.grid_y < self.grid.rows - 1 and self.grid.matrix[self.grid_y + 1][self.grid_x] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_y += 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_y = (self.grid_y + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_left(self):
        if self.animating: return False
        if self.grid_x > 0 and self.grid.matrix[self.grid_y][self.grid_x - 1] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_x -= 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_x = (self.grid_x + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_right(self):
        if self.animating: return False
        if self.grid_x < self.grid.cols - 1 and self.grid.matrix[self.grid_y][self.grid_x + 1] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_x += 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_x = (self.grid_x + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def move_randomly(self):
        if self.animating: return
        directions = [self._move_up, self._move_down, self._move_left, self._move_right]
        random.shuffle(directions)
        for fn in directions:
            if fn():
                break

    # ---------- Planificación de ruta (BFS) ----------
    def compute_path(self, dest_x, dest_y):
        start = (self.grid_x, self.grid_y)
        goal = (dest_x, dest_y)
        R, C = self.grid.rows, self.grid.cols
        mat = self.grid.matrix
        visited = [[False] * C for _ in range(R)]
        prev = {}

        queue = deque([start])
        visited[self.grid_y][self.grid_x] = True
        moves = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for d, (dx, dy) in moves.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < C and 0 <= ny < R and not visited[ny][nx]:
                    if (nx, ny) == goal or mat[ny][nx] is None:
                        visited[ny][nx] = True
                        prev[(nx, ny)] = (x, y, d)
                        queue.append((nx, ny))

        # Reconstruir
        path = []
        cur = goal
        if cur not in prev and cur != start:
            return []
        while cur != start:
            x0, y0, d = prev[cur]
            path.append(d)
            cur = (x0, y0)
        path.reverse()
        return path

    def move_to(self, dx, dy):
        self.path = self.compute_path(dx, dy)
        self.recovery_stack = []
        self.in_collision_avoidance = False

    # ---------- Helpers de evitación ----------
    def can_move(self, d):
        if self.animating: return False
        deltas = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}
        dx, dy = deltas[d]
        nx, ny = self.grid_x + dx, self.grid_y + dy
        return (
            0 <= nx < self.grid.cols and
            0 <= ny < self.grid.rows and
            self.grid.matrix[ny][nx] is None
        )

    def call_move(self, d):
        return {
            'u': self._move_up,
            'd': self._move_down,
            'l': self._move_left,
            'r': self._move_right,
        }[d]()

    def random_avoid_move(self):
        dirs = list('udlr')
        random.shuffle(dirs)
        opp = {'u': 'd', 'd': 'u', 'l': 'r', 'r': 'l'}
        for d in dirs:
            if self.can_move(d):
                if self.call_move(d):
                    self.recovery_stack.append(opp[d])
                break

    # ---------- Ejecución con evitación ----------
    def perform_move(self):
        if self.animating:
            return

        # Modo evitación
        if self.in_collision_avoidance:
            if self.path:
                nd = self.path[0]
                if self.can_move(nd):
                    if self.recovery_stack:
                        self.call_move(self.recovery_stack.pop())
                    else:
                        self.in_collision_avoidance = False
                else:
                    self.random_avoid_move()
            else:
                if self.recovery_stack:
                    self.call_move(self.recovery_stack.pop())
                else:
                    self.in_collision_avoidance = False
            return

        # Seguir ruta
        if self.path:
            d = self.path.pop(0)
            if not self.call_move(d):
                self.in_collision_avoidance = True
                self.path.insert(0, d)
                self.random_avoid_move()
        else:
            self.move_randomly()
