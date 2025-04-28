import pygame
import random
from item import Item

# Colores
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class ItemGenerator:
    def __init__(self, grid_x, grid_y, grid):
        # Posición en la cuadrícula
        self.grid_x = grid_x
        self.grid_y = grid_y
        # Referencia a la cuadrícula
        self.grid = grid
        # Marcar la posición en la matriz
        self.grid.matrix[self.grid_y][self.grid_x] = "-"
        # Capacidad del generador
        self.capacity = 1
        # Ítem actual generado
        self.current_item = None
        # Posición en píxeles para dibujar
        self.x = grid_x * grid.cell_size
        self.y = grid_y * grid.cell_size

    def draw(self, screen):
        # Dibujar un cuadrado negro para el generador
        pygame.draw.rect(screen, BLACK,
                         (self.x, self.y, self.grid.cell_size, self.grid.cell_size))

        # Si hay un ítem generado, dibujarlo
        if self.current_item:
            self.current_item.draw(screen)

    def generate_item(self):
        """
        Intenta generar un ítem con probabilidad 10%.
        Si lo genera, retorna la instancia; si no, retorna None.
        """
        if self.current_item is None and random.random() < 0.1:
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
        # Eliminar el ítem actual
        if self.current_item:
            self.current_item = None
            return True
        return False
