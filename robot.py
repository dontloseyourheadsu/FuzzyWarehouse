# robot.py
import pygame
import random
from collections import deque

# Colores
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)  # Color para FREE
ORANGE = (255, 165, 0)  # Color para PICKUP
RED = (255, 0, 0)  # Color para DELIVERING

# Estados del robot
FREE = "FREE"
PICKUP = "PICKUP"
DELIVERING = "DELIVERING"


class Robot:
    def __init__(self, grid_x, grid_y, radius, grid):
        # Posición en la cuadrícula (índices de matriz)
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Posición en píxeles (para dibujar)
        self.x = (grid_x + 0.5) * grid.cell_size
        self.y = (grid_y + 0.5) * grid.cell_size
        # Posiciones de destino (para animación)
        self.target_x = self.x
        self.target_y = self.y
        self.radius = radius
        self.grid = grid
        # Estado de la animación
        self.animating = False
        self.animation_speed = 5  # Velocidad de animación (píxeles por fotograma)
        # Pila de movimientos planificados y de recuperación
        self.path = []
        self.recovery_stack = []
        self.in_collision_avoidance = False
        # Estado del robot
        self.state = FREE
        # Ítem que lleva (o None)
        self.current_item = None
        # Marcar la posición inicial en la matriz
        self.grid.matrix[self.grid_y][self.grid_x] = "*"

    def draw(self, screen):
        # Dibujar el robot (círculo)
        pygame.draw.circle(screen, GRAY, (self.x, self.y), self.radius)

        # Determinar el color del sombrero según el estado
        hat_color = GREEN  # Por defecto FREE
        if self.state == PICKUP:
            hat_color = ORANGE
        elif self.state == DELIVERING:
            hat_color = RED

        # Dibujar el sombrero como un pequeño rectángulo encima del robot
        hat_width = self.radius * 1.2
        hat_height = self.radius * 0.5
        hat_x = self.x - hat_width / 2
        hat_y = self.y - self.radius - hat_height
        pygame.draw.rect(screen, hat_color, (hat_x, hat_y, hat_width, hat_height))

    # Métodos para cambiar el estado
    def set_state_free(self):
        self.state = FREE

    def set_state_pickup(self):
        self.state = PICKUP

    def set_state_delivering(self):
        self.state = DELIVERING

    def update(self):
        if self.animating:
            # Calcular dirección hacia el objetivo
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            # Comprobar si hemos llegado al objetivo
            if abs(dx) < self.animation_speed and abs(dy) < self.animation_speed:
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                # Normalizar y aplicar velocidad
                distance = max(1, (dx**2 + dy**2)**0.5)
                self.x += dx / distance * self.animation_speed
                self.y += dy / distance * self.animation_speed

    # ---------- Movimientos básicos ----------
    def _move_up(self):
        if self.animating:
            return False
        if self.grid_y > 0 and self.grid.matrix[self.grid_y - 1][self.grid_x] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_y -= 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_y = (self.grid_y + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_down(self):
        if self.animating:
            return False
        if self.grid_y < self.grid.rows - 1 and self.grid.matrix[self.grid_y + 1][self.grid_x] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_y += 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_y = (self.grid_y + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_left(self):
        if self.animating:
            return False
        if self.grid_x > 0 and self.grid.matrix[self.grid_y][self.grid_x - 1] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_x -= 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_x = (self.grid_x + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    def _move_right(self):
        if self.animating:
            return False
        if self.grid_x < self.grid.cols - 1 and self.grid.matrix[self.grid_y][self.grid_x + 1] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_x += 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_x = (self.grid_x + 0.5) * self.grid.cell_size
            self.animating = True
            return True
        return False

    # ---------- Movimiento aleatorio (fallback) ----------
    def move_randomly(self):
        if self.animating:
            return
        directions = [self._move_up, self._move_down, self._move_left, self._move_right]
        random.shuffle(directions)
        for direction in directions:
            if direction():
                break

    # ---------- Planificación de ruta (BFS) ----------
    def compute_path(self, dest_x, dest_y):
        start = (self.grid_x, self.grid_y)
        goal = (dest_x, dest_y)
        rows, cols = self.grid.rows, self.grid.cols
        matrix = self.grid.matrix
        visited = [[False]*cols for _ in range(rows)]
        prev = {}

        queue = deque([start])
        visited[self.grid_y][self.grid_x] = True
        moves = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for direction, (dx, dy) in moves.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                    # Permitimos llegar al destino incluso si ocupado (dropzone, etc.)
                    if (nx, ny) == goal or matrix[ny][nx] is None:
                        visited[ny][nx] = True
                        prev[(nx, ny)] = (x, y, direction)
                        queue.append((nx, ny))

        # Reconstruir el camino
        path = []
        current = goal
        if current not in prev and current != start:
            return []
        while current != start:
            x0, y0, dir = prev[current]
            path.append(dir)
            current = (x0, y0)
        path.reverse()
        return path

    def move_to(self, dest_x, dest_y):
        """
        Planifica y comienza a seguir la ruta hasta (dest_x, dest_y) en la cuadrícula.
        """
        self.path = self.compute_path(dest_x, dest_y)
        self.recovery_stack = []
        self.in_collision_avoidance = False

    # ---------- Ejecución de movimientos con evitación ----------
    def can_move(self, direction):
        if self.animating:
            return False
        deltas = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}
        dx, dy = deltas[direction]
        nx, ny = self.grid_x + dx, self.grid_y + dy
        if 0 <= nx < self.grid.cols and 0 <= ny < self.grid.rows:
            return self.grid.matrix[ny][nx] is None
        return False

    def call_move(self, direction):
        dispatcher = {
            'u': self._move_up,
            'd': self._move_down,
            'l': self._move_left,
            'r': self._move_right,
        }
        return dispatcher[direction]()

    def random_avoid_move(self):
        directions = list('udlr')
        random.shuffle(directions)
        opposites = {'u': 'd', 'd': 'u', 'l': 'r', 'r': 'l'}
        for d in directions:
            if self.can_move(d):
                if self.call_move(d):
                    # Guardar el movimiento inverso para regresar después
                    self.recovery_stack.append(opposites[d])
                break

    def perform_move(self):
        """
        Llama este method en lugar de move_randomly():
        - Sigue la ruta planificada
        - Si hay colisión, entra en modo de evitación
        - Realiza movimientos aleatorios hasta que se libere el siguiente paso
        - Regresa mediante recovery_stack y reanuda la ruta original
        """
        if self.animating:
            return

        # Modo de evitación de colisiones
        if self.in_collision_avoidance:
            if self.path:
                next_dir = self.path[0]
                if self.can_move(next_dir):
                    # Primero remontar movimientos aleatorios
                    if self.recovery_stack:
                        rev = self.recovery_stack.pop()
                        self.call_move(rev)
                    else:
                        self.in_collision_avoidance = False
                else:
                    self.random_avoid_move()
            else:
                # Si no hay ruta original, solo regresar
                if self.recovery_stack:
                    rev = self.recovery_stack.pop()
                    self.call_move(rev)
                else:
                    self.in_collision_avoidance = False
            return

        # Seguir camino planificado
        if self.path:
            d = self.path.pop(0)
            if not self.call_move(d):
                # Colisión: activar evitación
                self.in_collision_avoidance = True
                self.path.insert(0, d)
                self.random_avoid_move()
        else:
            # Sin ruta: fallback aleatorio
            self.move_randomly()
