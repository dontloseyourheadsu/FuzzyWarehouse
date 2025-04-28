import pygame

# Colores
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

class DropZone:
    def __init__(self, grid_x, grid_y, grid, name=""):
        # Posición en la cuadrícula
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Referencia a la cuadrícula
        self.grid = grid
        # Marcar la posición en la matriz
        self.grid.matrix[self.grid_y][self.grid_x] = "#"
        # Posición en píxeles para dibujar
        self.x = grid_x * grid.cell_size
        self.y = grid_y * grid.cell_size
        # Nombre de la dropzone
        self.name = name
        
    def draw(self, screen):
        # Dibujar un cuadrado azul para la zona de entrega
        pygame.draw.rect(screen, BLUE, 
                        (self.x, self.y, self.grid.cell_size, self.grid.cell_size))
        
        # Mostrar el nombre de la dropzone
        if self.name:
            font = pygame.font.SysFont('Arial', 14)
            text = font.render(self.name, True, WHITE)
            text_rect = text.get_rect(center=(self.x + self.grid.cell_size//2, 
                                            self.y + self.grid.cell_size//2))
            screen.blit(text, text_rect)
