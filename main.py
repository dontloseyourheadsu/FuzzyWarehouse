import pygame
import sys
import random

from robot import Robot, FREE, PICKUP, DELIVERING
from itemgenerator import ItemGenerator
from obstaclegenerator import ObstacleGenerator
from dropzone import DropZone
from fuzzy_logic import classify_item, ItemAttributes

# Initialize pygame
pygame.init()
# Reduced window dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 640  # Reduced from 1200x800
GRID_WIDTH, GRID_HEIGHT = 640, 480  # Reduced from 800x600
INFO_PANEL_WIDTH = 160  # Reduced from 200
BOTTOM_PANEL_HEIGHT = 160  # Reduced from 200
CELL_SIZE = 40  # Reduced from 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fuzzy Warehouse Simulation")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)


class Grid:
    def __init__(self, w, h, cs):
        self.width, self.height, self.cell_size = w, h, cs
        self.cols = w // cs;
        self.rows = h // cs
        self.matrix = [[None] * self.cols for _ in range(self.rows)]

    def draw(self, s):
        for x in range(0, self.width + 1, self.cell_size):
            pygame.draw.line(s, BLACK, (x, 0), (x, self.height))
        for y in range(0, self.height + 1, self.cell_size):
            pygame.draw.line(s, BLACK, (0, y), (self.width, y))
        for y in range(self.rows):
            for x in range(self.cols):
                if self.matrix[y][x] == '.':
                    pygame.draw.rect(s, BROWN,
                                     (x * self.cell_size, y * self.cell_size,
                                      self.cell_size, self.cell_size))


def find_nearest_free(robot, tx, ty, grid):
    """Returns the free neighboring cell (udlr) of (tx,ty) closest to the robot."""
    cands = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = tx + dx, ty + dy
        if 0 <= nx < grid.cols and 0 <= ny < grid.rows and grid.matrix[ny][nx] is None:
            cands.append((nx, ny))
    if not cands:
        return None
    return min(cands, key=lambda p: abs(p[0] - robot.grid_x) + abs(p[1] - robot.grid_y))


def draw_info_panels(screen, generators, dropzones):
    """Draw information panels for generators and dropzones"""
    # Left panel (Generators)
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, INFO_PANEL_WIDTH, GRID_HEIGHT))
    pygame.draw.line(screen, BLACK, (INFO_PANEL_WIDTH, 0), (INFO_PANEL_WIDTH, GRID_HEIGHT), 2)

    # Right panel (Dropzones)
    pygame.draw.rect(screen, LIGHT_GRAY, (INFO_PANEL_WIDTH + GRID_WIDTH, 0, INFO_PANEL_WIDTH, GRID_HEIGHT))
    pygame.draw.line(screen, BLACK, (INFO_PANEL_WIDTH + GRID_WIDTH, 0),
                     (INFO_PANEL_WIDTH + GRID_WIDTH, GRID_HEIGHT), 2)

    # Draw panel titles with slightly smaller fonts
    font_title = pygame.font.SysFont('Arial', 19, bold=True)  # Reduced from 20
    font_regular = pygame.font.SysFont('Arial', 15)  # Reduced from 16
    font_small = pygame.font.SysFont('Arial', 13)  # Reduced from 14

    # Generators panel title
    title = font_title.render("Item Generators", True, BLACK)
    screen.blit(title, (10, 10))

    # Draw info for each generator
    for i, gen in enumerate(generators):
        y_pos = 50 + i * 100  # Reduced spacing from 120

        # Generator label
        gen_label = font_regular.render(f"Generator {i + 1}", True, BLACK)
        screen.blit(gen_label, (10, y_pos))

        # Draw separator line
        pygame.draw.line(screen, DARK_GRAY, (10, y_pos + 25), (INFO_PANEL_WIDTH - 10, y_pos + 25), 1)

        # Item info
        if gen.current_item:
            item_text = font_regular.render("Current Item:", True, BLACK)
            screen.blit(item_text, (10, y_pos + 35))

            # Item attributes
            size_text = font_small.render(f"Size: {gen.current_item.size}", True, BLACK)
            screen.blit(size_text, (20, y_pos + 55))  # Reduced from 60

            frag_text = font_small.render(f"Fragility: {gen.current_item.fragility}", True, BLACK)
            screen.blit(frag_text, (20, y_pos + 70))  # Reduced from 80

            prio_text = font_small.render(f"Priority: {gen.current_item.priority}", True, BLACK)
            screen.blit(prio_text, (20, y_pos + 85))  # Reduced from 100
        else:
            no_item = font_regular.render("No item", True, BLACK)
            screen.blit(no_item, (10, y_pos + 55))  # Adjusted

    # Dropzones panel title
    title = font_title.render("Delivery Zones", True, BLACK)
    screen.blit(title, (INFO_PANEL_WIDTH + GRID_WIDTH + 10, 10))

    # Draw info for each dropzone
    for i, zone in enumerate(dropzones):
        y_pos = 50 + i * 70  # Reduced from 80

        # Zone label
        zone_label = font_regular.render(f"Zone {zone.name}", True, BLACK)
        screen.blit(zone_label, (INFO_PANEL_WIDTH + GRID_WIDTH + 10, y_pos))

        # Draw separator line
        pygame.draw.line(screen, DARK_GRAY,
                         (INFO_PANEL_WIDTH + GRID_WIDTH + 10, y_pos + 25),
                         (SCREEN_WIDTH - 10, y_pos + 25), 1)

        # Items received
        items_text = font_regular.render(f"Items received: {zone.items_received}", True, BLACK)
        screen.blit(items_text, (INFO_PANEL_WIDTH + GRID_WIDTH + 10, y_pos + 40))


def draw_robot_panel(screen, robots, generators):
    """Draw information panel for robots at the bottom of the screen"""
    # Bottom panel background
    pygame.draw.rect(screen, LIGHT_GRAY, (0, GRID_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, GRID_HEIGHT), (SCREEN_WIDTH, GRID_HEIGHT), 2)

    # Fonts
    font_title = pygame.font.SysFont('Arial', 19, bold=True)  # Reduced from 20
    font_regular = pygame.font.SysFont('Arial', 15)  # Reduced from 16
    font_small = pygame.font.SysFont('Arial', 13)  # Reduced from 14

    # Panel title
    title = font_title.render("Robot Status", True, BLACK)
    screen.blit(title, (10, GRID_HEIGHT + 10))

    # Draw info for each robot
    robot_width = SCREEN_WIDTH // len(robots) if robots else SCREEN_WIDTH

    for i, robot in enumerate(robots):
        x_pos = i * robot_width
        y_pos = GRID_HEIGHT + 35  # Reduced from 40

        # Robot section border
        pygame.draw.line(screen, DARK_GRAY, (x_pos, GRID_HEIGHT), (x_pos, SCREEN_HEIGHT), 1)

        # Robot label
        robot_label = font_regular.render(f"Robot {i + 1}", True, BLACK)
        screen.blit(robot_label, (x_pos + 10, y_pos))

        # Status line (FREE/PICKUP/DELIVERING)
        state_text = font_regular.render(f"Status: {robot.state}", True, BLACK)
        screen.blit(state_text, (x_pos + 10, y_pos + 20))  # Reduced from 25

        # Target information
        target_text = "Target: "
        if robot.state == PICKUP and robot.pickup_target:
            # Find generator index
            gen_index = next((i + 1 for i, g in enumerate(generators)
                              if g == robot.pickup_target), "?")
            target_text += f"Generator {gen_index}"
        elif robot.state == DELIVERING and robot.delivery_target:
            target_text += f"Zone {robot.delivery_target.name}"
        else:
            target_text += "No target"

        target_render = font_regular.render(target_text, True, BLACK)
        screen.blit(target_render, (x_pos + 10, y_pos + 40))  # Reduced from 50

        # Item information if carrying one
        if robot.carrying_item:
            item_title = font_regular.render("Carrying Item:", True, BLACK)
            screen.blit(item_title, (x_pos + 10, y_pos + 60))  # Reduced from 75

            size_text = font_small.render(f"Size: {robot.carrying_item.size:.2f}", True, BLACK)
            screen.blit(size_text, (x_pos + 15, y_pos + 80))  # Reduced from 100

            frag_text = font_small.render(f"Fragility: {robot.carrying_item.fragility:.2f}", True, BLACK)
            screen.blit(frag_text, (x_pos + 15, y_pos + 95))  # Reduced from 120

            prio_text = font_small.render(f"Priority: {robot.carrying_item.priority:.2f}", True, BLACK)
            screen.blit(prio_text, (x_pos + 15, y_pos + 110))  # Reduced from 140
        else:
            no_item = font_regular.render("Not carrying an item", True, BLACK)
            screen.blit(no_item, (x_pos + 10, y_pos + 60))  # Adjusted


def main():
    clock = pygame.time.Clock()

    # Offset the grid to account for the left info panel
    grid_offset_x = INFO_PANEL_WIDTH
    grid = Grid(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)

    # Setup item generators along the left side
    generators = []
    for i in range(4):
        gy = i * 3 + 2
        if gy < grid.rows:
            generators.append(ItemGenerator(0, gy, grid))

    # Setup delivery zones along the right side
    dropzones = []
    right = grid.cols - 1
    spacing = grid.rows // 6
    for i in range(5):
        gy = (i + 1) * spacing
        if gy < grid.rows:
            dropzones.append(DropZone(right, gy, grid, name=f"Z{i + 1}"))

    # Create robots at random positions
    robots = []
    used = set()
    while len(robots) < 4:
        gx = random.randint(2, grid.cols - 3)
        gy = random.randint(0, grid.rows - 1)
        if (gx, gy) not in used and grid.matrix[gy][gx] is None:
            used.add((gx, gy))
            robots.append(Robot(gx, gy, CELL_SIZE // 3, grid))

    # Generate obstacles randomly throughout the grid
    ObstacleGenerator(grid, obstacle_ratio=0.15).generate_obstacles()

    move_delay = 500  # Milliseconds between robot moves
    item_delay = 2000  # Milliseconds between item generation attempts
    last_move = pygame.time.get_ticks()
    last_gen = pygame.time.get_ticks()

    pending = []  # Generators with items waiting for a robot

    while True:
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

        # Generate new items
        if now - last_gen > item_delay:
            for gen in generators:
                if gen.generate_item():
                    pending.append(gen)
            last_gen = now

        # Assign pickup tasks to free robots
        for gen in pending[:]:
            free_r = next((r for r in robots if r.state == FREE), None)
            if free_r:
                # Mark robot as carrying an item with attributes
                it = gen.current_item
                free_r.carrying_item = ItemAttributes(it.size, it.fragility, it.priority)
                free_r.set_state(PICKUP)
                free_r.pickup_target = gen
                # Find available adjacent cell to the generator
                dest = find_nearest_free(free_r, gen.grid_x, gen.grid_y, grid)
                if dest:
                    free_r.move_to(dest[0], dest[1])
                    pending.remove(gen)

        # Move robots at regular intervals if not currently animating
        if now - last_move > move_delay:
            if not any(r.animating for r in robots):
                for r in robots:
                    r.perform_move()
                last_move = now

        # Check for pickup and delivery completions
        for r in robots:
            # If robot reached generator neighbor → perform pickup
            if r.state == PICKUP and not r.animating and not r.path:
                gen = r.pickup_target
                gen.remove_item()
                # Use fuzzy logic to decide which zone to deliver to
                zone = classify_item(r.carrying_item)
                dz = next(z for z in dropzones if z.name == zone)
                r.set_state(DELIVERING)
                r.delivery_target = dz
                d2 = find_nearest_free(r, dz.grid_x, dz.grid_y, grid)
                if d2:
                    r.move_to(d2[0], d2[1])

            # If robot reached delivery zone neighbor → complete delivery
            if r.state == DELIVERING and not r.animating and not r.path:
                # Add item to the dropzone counter
                r.delivery_target.add_item()
                r.carrying_item = None
                r.pickup_target = None
                r.delivery_target = None
                r.set_state(FREE)

        # Draw everything
        for r in robots: r.update()
        screen.fill(WHITE)

        # Draw info panels
        draw_info_panels(screen, generators, dropzones)

        # Draw grid with offset for the left panel
        pygame.Surface.subsurface(screen, (INFO_PANEL_WIDTH, 0, GRID_WIDTH, GRID_HEIGHT)).fill(WHITE)
        grid.draw(pygame.Surface.subsurface(screen, (INFO_PANEL_WIDTH, 0, GRID_WIDTH, GRID_HEIGHT)))

        # Draw game elements with offset
        for g in generators:
            g.draw(pygame.Surface.subsurface(screen, (INFO_PANEL_WIDTH, 0, GRID_WIDTH, GRID_HEIGHT)))
        for z in dropzones:
            z.draw(pygame.Surface.subsurface(screen, (INFO_PANEL_WIDTH, 0, GRID_WIDTH, GRID_HEIGHT)))
        for r in robots:
            r.draw(pygame.Surface.subsurface(screen, (INFO_PANEL_WIDTH, 0, GRID_WIDTH, GRID_HEIGHT)))

        # Draw the robot info panel at the bottom
        draw_robot_panel(screen, robots, generators)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()