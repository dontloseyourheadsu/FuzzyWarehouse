import pygame
import random

# Color definitions (RGB)
GREEN = (0, 255, 0)


class Item:
    def __init__(self, grid_x, grid_y, grid):
        """
        Initializes an item at a specific position on the grid with random attributes.

        Parameters:
        - grid_x: horizontal position on the grid
        - grid_y: vertical position on the grid
        - grid: reference to the grid object (assumed to have cell_size attribute)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid = grid

        # Define the radius of the item (a small green dot)
        self.radius = grid.cell_size // 6

        # Calculate pixel coordinates for drawing (centered within the grid cell)
        self.x = (grid_x + 0.5) * grid.cell_size
        self.y = (grid_y + 0.5) * grid.cell_size

        # Randomly generate item attributes between 0 and 1
        self.size = round(random.random(), 2)  # Size of the item (0 to 1)
        self.fragility = round(random.random(), 2)  # Fragility of the item (0 to 1)
        self.priority = round(random.random(), 2)  # Priority of the item (0 to 1)

    def draw(self, screen):
        """
        Draws the item as a small green circle on the screen.

        Parameters:
        - screen: the Pygame surface to draw on
        """
        # Draw the item as a small green circle at its calculated position
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)
