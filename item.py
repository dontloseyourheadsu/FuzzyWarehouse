import pygame
import random

# Colores
GREEN = (0, 255, 0)

class Item:
    def __init__(self, grid_x, grid_y, grid):
        # Posición en la cuadrícula
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Referencia a la cuadrícula
        self.grid = grid
        # Radio del ítem (pequeño punto verde)
        self.radius = grid.cell_size // 6
        # Posición en píxeles para dibujar
        self.x = (grid_x + 0.5) * grid.cell_size
        self.y = (grid_y + 0.5) * grid.cell_size
        
        # Nuevos atributos del ítem con valores aleatorios entre 0 y 1
        self.size = round(random.random(), 2)       # Tamaño del ítem
        self.fragility = round(random.random(), 2)  # Fragilidad del ítem
        self.priority = round(random.random(), 2)   # Prioridad del ítem
        
    def draw(self, screen):
        # Dibujar un pequeño círculo verde
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)
