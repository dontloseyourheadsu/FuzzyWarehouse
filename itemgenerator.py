import pygame
import random
from item import Item  # Import the Item class from another module

# Color definitions (RGB)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class ItemGenerator:
    def __init__(self, grid_x, grid_y, grid):
        """
        Initializes the item generator on a grid.

        Parameters:
        - grid_x: horizontal position on the grid
        - grid_y: vertical position on the grid
        - grid: reference to the grid object (assumed to have matrix and cell_size)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid = grid

        # Mark the generator's position in the grid with a special symbol (e.g., "-")
        self.grid.matrix[self.grid_y][self.grid_x] = "-"

        self.capacity = 1  # Capacity: how many items it can hold at once
        self.current_item = None  # Initially, no item is generated

        # Pixel coordinates for drawing
        self.x = grid_x * grid.cell_size
        self.y = grid_y * grid.cell_size

    def draw(self, screen):
        """
        Draws the generator and the item (if present) on the screen.

        Parameters:
        - screen: the Pygame surface to draw on
        """
        # Draw a black square representing the generator
        pygame.draw.rect(screen, BLACK,
                         (self.x, self.y, self.grid.cell_size, self.grid.cell_size))

        # If an item exists, draw it too
        if self.current_item:
            self.current_item.draw(screen)

    def generate_item(self):
        """
        Attempts to generate a new item with a 10% probability.
        Only generates if there is no current item.

        Returns:
        - The newly generated Item instance if successful
        - None if generation didn't occur
        """
        if self.current_item is None and random.random() < 0.1:
            # Create a new item at the generator's position
            self.current_item = Item(self.grid_x, self.grid_y, self.grid)
            print(
                f"Generated new item at ({self.grid_x},{self.grid_y}) "
                f"[size={self.current_item.size}, "
                f"fragility={self.current_item.fragility}, "
                f"priority={self.current_item.priority}]"
            )
            return self.current_item
        return None

    def remove_item(self):
        """
        Removes the currently held item (if any).

        Returns:
        - True if an item was removed
        - False if there was no item
        """
        if self.current_item:
            self.current_item = None
            return True
        return False
