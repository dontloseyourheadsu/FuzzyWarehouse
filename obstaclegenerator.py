import random

class ObstacleGenerator:
    def __init__(self, grid, obstacle_ratio=0.2):
        self.grid = grid
        self.obstacle_ratio = obstacle_ratio
        self.obstacle_char = "."
    
    def generate_obstacles(self):
        """Genera obstáculos en la cuadrícula hasta alcanzar el porcentaje deseado"""
        # Contar celdas libres
        free_cells = []
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.matrix[y][x] is None:
                    free_cells.append((x, y))
        
        # Calcular cuántos obstáculos colocar
        num_obstacles = int(len(free_cells) * self.obstacle_ratio)
        
        # Mezclamos las celdas para seleccionar posiciones aleatorias
        random.shuffle(free_cells)
        
        # Lista de obstáculos colocados
        placed_obstacles = []
        
        # Colocamos obstáculos mientras comprobamos que exista un camino
        for i in range(min(num_obstacles, len(free_cells))):
            x, y = free_cells[i]
            
            # Colocamos temporalmente el obstáculo
            self.grid.matrix[y][x] = self.obstacle_char
            placed_obstacles.append((x, y))
            
            # Si no hay caminos desde generadores a todas las dropzones, quitamos el último obstáculo
            if not self._all_paths_exist():
                # Quitar el último obstáculo
                self.grid.matrix[y][x] = None
                placed_obstacles.pop()
        
        return placed_obstacles
    
    def _all_paths_exist(self):
        """Comprueba si existen caminos desde todos los generadores a todas las dropzones"""
        # Encontrar todas las posiciones de generadores y dropzones
        generators = []
        dropzones = []
        
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.matrix[y][x] == "-":  # Generador
                    generators.append((x, y))
                elif self.grid.matrix[y][x] == "#":  # Dropzone
                    dropzones.append((x, y))
        
        # Verificar que desde cada generador se pueda llegar a todas las dropzones
        for gen_x, gen_y in generators:
            for drop_x, drop_y in dropzones:
                if not self._exists_path(gen_x, gen_y, drop_x, drop_y):
                    return False
        
        return True
    
    def _exists_path(self, start_x, start_y, end_x, end_y):
        """Comprueba si existe un camino entre dos puntos usando BFS"""
        queue = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        
        while queue:
            x, y = queue.pop(0)
            
            if x == end_x and y == end_y:
                return True
            
            # Añadir vecinos no visitados
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1)
            ]
            
            for nx, ny in neighbors:
                if (0 <= nx < self.grid.cols and 0 <= ny < self.grid.rows and 
                    (nx, ny) not in visited and 
                    (self.grid.matrix[ny][nx] is None or 
                     self.grid.matrix[ny][nx] == "-" or 
                     self.grid.matrix[ny][nx] == "#" or
                     self.grid.matrix[ny][nx] == "*")):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
        
        return False
    
    def _exists_path_left_to_right(self):
        """Comprueba si existe al menos un camino desde la izquierda hasta la derecha"""
        # Encontrar celdas de entrada (columna izquierda)
        start_cells = []
        for y in range(self.grid.rows):
            if self.grid.matrix[y][0] is None or self.grid.matrix[y][0] == "-":
                start_cells.append((0, y))
        
        # BFS para comprobar si hay un camino
        if not start_cells:
            return False
        
        queue = start_cells
        visited = set(start_cells)
        
        while queue:
            x, y = queue.pop(0)
            
            # Si llegamos a la columna derecha, hay un camino
            if x == self.grid.cols - 1:
                return True
            
            # Añadir vecinos no visitados
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1)
            ]
            
            for nx, ny in neighbors:
                if (0 <= nx < self.grid.cols and 0 <= ny < self.grid.rows and 
                    (nx, ny) not in visited and 
                    (self.grid.matrix[ny][nx] is None or self.grid.matrix[ny][nx] == "-")):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
        
        return False
