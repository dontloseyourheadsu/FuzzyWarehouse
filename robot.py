import pygame
import random
from collections import deque

# Colors
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)  # FREE
ORANGE = (255, 165, 0)  # PICKUP
RED = (255, 0, 0)  # DELIVERING
BLACK = (0, 0, 0)  # EYE

# States
FREE = "FREE"
PICKUP = "PICKUP"
DELIVERING = "DELIVERING"


class Robot:
    def __init__(self, grid_x, grid_y, radius, grid):
        # Grid position
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Pixel position for drawing
        self.x = (grid_x + 0.5) * grid.cell_size
        self.y = (grid_y + 0.5) * grid.cell_size
        self.target_x = self.x
        self.target_y = self.y
        self.radius = radius
        self.grid = grid

        # Animation
        self.animating = False
        self.animation_speed = 5

        # Path planning and recovery
        self.path = []
        self.recovery_stack = []  # Stores reverse moves to get back on path after collision avoidance
        self.in_collision_avoidance = False

        # State and cargo
        self.state = FREE
        self.carrying_item = None

        # Pickup/delivery target pointers
        self.pickup_target = None
        self.delivery_target = None

        # Eye properties
        self.eye_radius = radius * 0.25  # Eye is 1/4 the size of the robot
        self.eye_direction = 'r'  # Default looking right
        self.eye_x = self.x + self.radius * 0.7
        self.eye_y = self.y

        # Mark robot position in grid matrix
        self.grid.matrix[self.grid_y][self.grid_x] = "*"

    def draw(self, screen):
        # Draw robot body
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius)
        # Draw hat to indicate robot state
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

        # Draw the eye
        pygame.draw.circle(screen, BLACK, (int(self.eye_x), int(self.eye_y)), int(self.eye_radius))

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

        # Update eye position during animation
        self._update_eye_position()

    def _update_eye_position(self):
        """Update the eye position based on the current direction"""
        if self.eye_direction == 'r':  # Right
            self.eye_x = self.x + self.radius * 0.7
            self.eye_y = self.y
        elif self.eye_direction == 'l':  # Left
            self.eye_x = self.x - self.radius * 0.7
            self.eye_y = self.y
        elif self.eye_direction == 'u':  # Up
            self.eye_x = self.x
            self.eye_y = self.y - self.radius * 0.7
        elif self.eye_direction == 'd':  # Down
            self.eye_x = self.x
            self.eye_y = self.y + self.radius * 0.7

    # ---------- Basic Movements ----------
    def _move_up(self):
        if self.animating: return False
        if self.grid_y > 0 and self.grid.matrix[self.grid_y - 1][self.grid_x] is None:
            self.grid.matrix[self.grid_y][self.grid_x] = None
            self.grid_y -= 1
            self.grid.matrix[self.grid_y][self.grid_x] = "*"
            self.target_y = (self.grid_y + 0.5) * self.grid.cell_size
            self.animating = True
            self.eye_direction = 'u'  # Set eye direction to up
            self._update_eye_position()
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
            self.eye_direction = 'd'  # Set eye direction to down
            self._update_eye_position()
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
            self.eye_direction = 'l'  # Set eye direction to left
            self._update_eye_position()
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
            self.eye_direction = 'r'  # Set eye direction to right
            self._update_eye_position()
            return True
        return False

    def move_randomly(self):
        if self.animating: return
        directions = [self._move_up, self._move_down, self._move_left, self._move_right]
        random.shuffle(directions)
        for fn in directions:
            if fn():
                break

    # ---------- Path Planning (BFS) ----------
    def compute_path(self, dest_x, dest_y):
        start = (self.grid_x, self.grid_y)
        goal = (dest_x, dest_y)
        R, C = self.grid.rows, self.grid.cols
        mat = self.grid.matrix
        visited = [[False] * C for _ in range(R)]
        prev = {}  # Stores previous cell and direction used to reach each cell

        queue = deque([start])
        visited[self.grid_y][self.grid_x] = True
        moves = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}

        # BFS to find path
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

        # Reconstruct path from destination to start
        path = []
        cur = goal
        if cur not in prev and cur != start:
            return []  # No path found
        while cur != start:
            x0, y0, d = prev[cur]
            path.append(d)
            cur = (x0, y0)
        path.reverse()  # Reverse to get path from start to destination
        return path

    def move_to(self, dx, dy):
        self.path = self.compute_path(dx, dy)
        self.recovery_stack = []
        self.in_collision_avoidance = False

        # Set initial eye direction if there's a path
        if self.path and not self.animating:
            self.eye_direction = self.path[0]
            self._update_eye_position()

    # ---------- Collision Avoidance Helpers ----------
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
        opp = {'u': 'd', 'd': 'u', 'l': 'r', 'r': 'l'}  # Maps directions to their opposites
        for d in dirs:
            if self.can_move(d):
                self.eye_direction = d  # Update eye direction before moving
                self._update_eye_position()
                if self.call_move(d):
                    self.recovery_stack.append(opp[d])  # Add opposite move to recovery stack
                break

    # ---------- Movement Execution with Collision Avoidance ----------
    def perform_move(self):
        if self.animating:
            return

        # Collision avoidance mode - either avoiding obstacles or trying to get back on path
        if self.in_collision_avoidance:
            if self.path:
                nd = self.path[0]
                if self.can_move(nd):  # If original path is now clear
                    if self.recovery_stack:  # First backtrack to original position
                        backtrack_dir = self.recovery_stack.pop()
                        self.eye_direction = backtrack_dir  # Update eye direction
                        self._update_eye_position()
                        self.call_move(backtrack_dir)
                    else:  # Backtracking complete, resume normal path
                        self.in_collision_avoidance = False
                else:  # Path still blocked, continue random avoidance
                    self.random_avoid_move()
            else:  # No more path to follow, just get back to last position
                if self.recovery_stack:
                    backtrack_dir = self.recovery_stack.pop()
                    self.eye_direction = backtrack_dir  # Update eye direction
                    self._update_eye_position()
                    self.call_move(backtrack_dir)
                else:
                    self.in_collision_avoidance = False
            return

        # Normal path following
        if self.path:
            d = self.path.pop(0)
            self.eye_direction = d  # Update eye direction before attempting move
            self._update_eye_position()
            if not self.call_move(d):  # If move fails, enter collision avoidance mode
                self.in_collision_avoidance = True
                self.path.insert(0, d)  # Put direction back in path
                self.random_avoid_move()  # Try random direction to avoid obstacle
        else:
            self.move_randomly()  # No path to follow, move randomly