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
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CELL_SIZE = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Example")

WHITE = (255,255,255)
BLACK = (0,0,0)
BROWN = (139,69,19)

class Grid:
    def __init__(self, w,h,cs):
        self.width, self.height, self.cell_size = w,h,cs
        self.cols = w//cs; self.rows = h//cs
        self.matrix = [[None]*self.cols for _ in range(self.rows)]
    def draw(self, s):
        for x in range(0,self.width+1,self.cell_size):
            pygame.draw.line(s, BLACK, (x,0),(x,self.height))
        for y in range(0,self.height+1,self.cell_size):
            pygame.draw.line(s, BLACK, (0,y),(self.width,y))
        for y in range(self.rows):
            for x in range(self.cols):
                if self.matrix[y][x]=='.':
                    pygame.draw.rect(s, BROWN,
                                     (x*self.cell_size, y*self.cell_size,
                                      self.cell_size, self.cell_size))

def find_nearest_free(robot, tx, ty, grid):
    """Returns the free neighboring cell (udlr) of (tx,ty) closest to the robot."""
    cands = []
    for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]:
        nx,ny = tx+dx, ty+dy
        if 0 <= nx < grid.cols and 0 <= ny < grid.rows and grid.matrix[ny][nx] is None:
            cands.append((nx,ny))
    if not cands:
        return None
    return min(cands, key=lambda p: abs(p[0]-robot.grid_x)+abs(p[1]-robot.grid_y))

def main():
    clock = pygame.time.Clock()
    grid = Grid(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE)

    # Setup item generators along the left side
    generators = []
    for i in range(4):
        gy = i*3+2
        if gy < grid.rows:
            generators.append(ItemGenerator(0, gy, grid))

    # Setup delivery zones along the right side
    dropzones = []
    right = grid.cols - 1
    spacing = grid.rows // 6
    for i in range(5):
        gy = (i+1)*spacing
        if gy < grid.rows:
            dropzones.append(DropZone(right, gy, grid, name=f"Z{i+1}"))

    # Create robots at random positions
    robots = []
    used = set()
    while len(robots) < 4:
        gx = random.randint(2, grid.cols-3)
        gy = random.randint(0, grid.rows-1)
        if (gx,gy) not in used and grid.matrix[gy][gx] is None:
            used.add((gx,gy))
            robots.append(Robot(gx, gy, CELL_SIZE//3, grid))

    # Generate obstacles randomly throughout the grid
    ObstacleGenerator(grid, obstacle_ratio=0.15).generate_obstacles()

    move_delay = 500  # Milliseconds between robot moves
    item_delay = 2000  # Milliseconds between item generation attempts
    last_move = pygame.time.get_ticks()
    last_gen  = pygame.time.get_ticks()

    pending = []  # Generators with items waiting for a robot

    while True:
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

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
                dz   = next(z for z in dropzones if z.name == zone)
                r.set_state(DELIVERING)
                r.delivery_target = dz
                d2 = find_nearest_free(r, dz.grid_x, dz.grid_y, grid)
                if d2:
                    r.move_to(d2[0], d2[1])

            # If robot reached delivery zone neighbor → complete delivery
            if r.state == DELIVERING and not r.animating and not r.path:
                r.carrying_item = None
                r.pickup_target  = None
                r.delivery_target = None
                r.set_state(FREE)

        # Draw everything
        for r in robots: r.update()
        screen.fill(WHITE)
        grid.draw(screen)
        for g in generators: g.draw(screen)
        for z in dropzones:   z.draw(screen)
        for r in robots:      r.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
