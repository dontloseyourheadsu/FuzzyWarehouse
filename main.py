# main.py
import pygame
import sys
import random
from robot import Robot, FREE, PICKUP, DELIVERING
from itemgenerator import ItemGenerator
from obstaclegenerator import ObstacleGenerator
from dropzone import DropZone
from fuzzy_logic import classify_item

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CELL_SIZE = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Example")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)  # Color para los obstáculos
BLUE = (0, 0, 255)  # Color para las dropzones


class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size
        self.matrix = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def draw(self, screen):
        # Dibujar las líneas de la cuadrícula
        for x in range(0, self.width + 1, self.cell_size):
            pygame.draw.line(screen, BLACK, (x, 0), (x, self.height))
        for y in range(0, self.height + 1, self.cell_size):
            pygame.draw.line(screen, BLACK, (0, y), (self.width, y))

        # Dibujar los obstáculos
        for y in range(self.rows):
            for x in range(self.cols):
                if self.matrix[y][x] == ".":
                    pygame.draw.rect(screen, BROWN,
                                     (x * self.cell_size, y * self.cell_size,
                                      self.cell_size, self.cell_size))


def main():
    clock = pygame.time.Clock()
    grid = Grid(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE)

    # Generadores de ítems
    generators = []
    num_generators = 4
    for i in range(num_generators):
        gy = i * 3 + 2
        if gy < grid.rows:
            generators.append(ItemGenerator(0, gy, grid))

    # Dropzones Z1…Z5
    dropzones = []
    num_dropzones = 5
    right_col = grid.cols - 1
    spacing = grid.rows // (num_dropzones + 1)
    for i in range(num_dropzones):
        gy = (i + 1) * spacing
        if gy < grid.rows:
            name = f"Z{i + 1}"
            dropzones.append(DropZone(right_col, gy, grid, name=name))

    # Robots
    robots = []
    positions = set()
    while len(robots) < 4:
        rx = random.randint(2, grid.cols - 3)
        ry = random.randint(0, grid.rows - 1)
        if (rx, ry) not in positions and grid.matrix[ry][rx] is None:
            positions.add((rx, ry))
            robots.append(Robot(rx, ry, CELL_SIZE // 3, grid))

    # Obstáculos
    obstacle_generator = ObstacleGenerator(grid, obstacle_ratio=0.15)
    obstacle_generator.generate_obstacles()

    move_delay = 500
    item_generation_delay = 2000
    last_move_time = pygame.time.get_ticks()
    last_generation_time = pygame.time.get_ticks()

    # Aquí guardamos ítems a asignar: (generator, item)
    pending_items = []

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 1) Mover robots si toca
        if current_time - last_move_time > move_delay:
            if not any(r.animating for r in robots):
                for r in robots:
                    r.perform_move()
                last_move_time = current_time

        # 2) Generar ítems
        if current_time - last_generation_time > item_generation_delay:
            for gen in generators:
                item = gen.generate_item()
                if item:
                    pending_items.append((gen, item))
            last_generation_time = current_time

        # 3) Asignar ítems pendientes a robots FREE
        for gen, item in pending_items[:]:
            free_robots = [r for r in robots if r.state == FREE]
            if free_robots:
                r = free_robots[0]
                idx = robots.index(r)
                print(f"Notifying Robot {idx}: item at ({gen.grid_x},{gen.grid_y}) → Robot {idx} accepted.")
                r.current_item = item
                r.set_state_pickup()
                r.move_to(item.grid_x, item.grid_y)
                pending_items.remove((gen, item))
            else:
                print("No free robots available, waiting...")

        # 4) Actualizar animaciones
        for r in robots:
            r.update()

        # 5) Detectar llegada al pickup
        for r in robots:
            if r.state == PICKUP and not r.animating and not r.path:
                idx = robots.index(r)
                print(f"Robot {idx} picked up item at ({r.grid_x},{r.grid_y}).")
                zone = classify_item(r.current_item)
                print(f"Robot {idx} determined delivery zone: {zone}.")
                dz = next((dz for dz in dropzones if dz.name == zone), None)
                if dz:
                    print(f"Robot {idx} delivering to {zone} at ({dz.grid_x},{dz.grid_y}).")
                    r.set_state_delivering()
                    r.move_to(dz.grid_x, dz.grid_y)
                    # remover del generador original
                    origin = next((g for g in generators if g.current_item == r.current_item), None)
                    if origin:
                        origin.remove_item()
                else:
                    print(f"No dropzone found for zone {zone}.")

        # 6) Detectar llegada al dropzone y liberar robot
        for r in robots:
            if r.state == DELIVERING and not r.animating and not r.path:
                idx = robots.index(r)
                print(f"Robot {idx} delivered item to dropzone.")
                r.current_item = None
                r.set_state_free()

        # 7) Dibujar all
        screen.fill(WHITE)
        grid.draw(screen)
        for gen in generators:
            gen.draw(screen)
        for dz in dropzones:
            dz.draw(screen)
        for r in robots:
            r.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
