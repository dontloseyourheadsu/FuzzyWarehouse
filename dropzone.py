import pygame

# Color definitions (RGB)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


class DropZone:
    def __init__(self, grid_x, grid_y, grid, name=""):
        """
        Initializes a drop zone at a specific position on the grid.

        Parameters:
        - grid_x: horizontal position on the grid
        - grid_y: vertical position on the grid
        - grid: reference to the grid object (assumed to have matrix and cell_size attributes)
        - name: optional name for the drop zone
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid = grid

        # Mark the drop zone's position in the grid with a special symbol (e.g., "#")
        self.grid.matrix[self.grid_y][self.grid_x] = "#"

        # Calculate pixel coordinates for drawing
        self.x = grid_x * grid.cell_size
        self.y = grid_y * grid.cell_size

        # Store the optional name of the drop zone
        self.name = name
        
        # Counter for items received
        self.items_received = 0

    def add_item(self):
        """Increment the counter for received items"""
        self.items_received += 1

    def draw(self, screen):
        """
        Draws the drop zone and its name (if available) on the screen.

        Parameters:
        - screen: the Pygame surface to draw on
        """
        # Draw a blue square to represent the drop zone
        pygame.draw.rect(screen, BLUE,
                         (self.x, self.y, self.grid.cell_size, self.grid.cell_size))

        # If a name exists for the drop zone, display it in the center
        if self.name:
            font = pygame.font.SysFont('Arial', 14)  # Create a font for the text
            text = font.render(self.name, True, WHITE)  # Render the name in white
            text_rect = text.get_rect(center=(self.x + self.grid.cell_size // 2,
                                              self.y + self.grid.cell_size // 2))  # Center the text
            screen.blit(text, text_rect)  # Draw the name on the screen
