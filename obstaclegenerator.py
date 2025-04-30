import random


class ObstacleGenerator:
    def __init__(self, grid, obstacle_ratio=0.2):
        self.grid = grid
        self.obstacle_ratio = obstacle_ratio
        self.obstacle_char = "."

    def generate_obstacles(self):
        """Generate obstacles in the grid up to the desired percentage while ensuring all paths remain valid"""
        # Find all generators and dropzones first
        generators = []
        dropzones = []

        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.matrix[y][x] == "-":  # Generator
                    generators.append((x, y))
                elif self.grid.matrix[y][x] == "#":  # Dropzone
                    dropzones.append((x, y))

        # Count free cells
        free_cells = []
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                # Only consider empty cells that aren't adjacent to generators or dropzones
                if self.grid.matrix[y][x] is None and not self._is_adjacent_to_special_cell(x, y, generators,
                                                                                            dropzones):
                    free_cells.append((x, y))

        # Calculate how many obstacles to place
        num_obstacles = int(len(free_cells) * self.obstacle_ratio)

        # Shuffle cells to select random positions
        random.shuffle(free_cells)

        # List of placed obstacles
        placed_obstacles = []

        # Place obstacles while checking that paths exist
        for i in range(min(num_obstacles, len(free_cells))):
            x, y = free_cells[i]

            # Temporarily place the obstacle
            self.grid.matrix[y][x] = self.obstacle_char
            placed_obstacles.append((x, y))

            # If there's no path from any generator to any dropzone, remove the last obstacle
            if not self._all_paths_exist(generators, dropzones):
                # Remove the last obstacle
                self.grid.matrix[y][x] = None
                placed_obstacles.pop()

        return placed_obstacles

    def _is_adjacent_to_special_cell(self, x, y, generators, dropzones):
        """Check if a cell is adjacent to generators or dropzones"""
        # Define adjacent cells (no diagonals)
        adjacent_cells = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)
        ]

        # Check if any adjacent cell is a generator or dropzone
        for adj_x, adj_y in adjacent_cells:
            # Skip if out of bounds
            if not (0 <= adj_x < self.grid.cols and 0 <= adj_y < self.grid.rows):
                continue

            # Check if it's a generator or dropzone
            if (adj_x, adj_y) in generators or (adj_x, adj_y) in dropzones:
                return True

        return False

    def _all_paths_exist(self, generators, dropzones):
        """Check if paths exist from all generators to all dropzones"""
        # Verify that from each generator we can reach at least one dropzone
        for gen_x, gen_y in generators:
            can_reach_any_dropzone = False
            for drop_x, drop_y in dropzones:
                if self._exists_path(gen_x, gen_y, drop_x, drop_y):
                    can_reach_any_dropzone = True
                    break

            if not can_reach_any_dropzone:
                return False

        # Verify that each dropzone can be reached from at least one generator
        for drop_x, drop_y in dropzones:
            can_be_reached = False
            for gen_x, gen_y in generators:
                if self._exists_path(gen_x, gen_y, drop_x, drop_y):
                    can_be_reached = True
                    break

            if not can_be_reached:
                return False

        return True

    def _exists_path(self, start_x, start_y, end_x, end_y):
        """Check if a path exists between two points using BFS"""
        queue = [(start_x, start_y)]
        visited = {(start_x, start_y)}

        while queue:
            x, y = queue.pop(0)

            if x == end_x and y == end_y:
                return True

            # Add unvisited neighbors (only cardinal directions, no diagonals)
            neighbors = [
                (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)
            ]

            for nx, ny in neighbors:
                # Check if in bounds and not visited
                if not (0 <= nx < self.grid.cols and 0 <= ny < self.grid.rows):
                    continue
                if (nx, ny) in visited:
                    continue

                # Check if the cell is traversable
                cell_content = self.grid.matrix[ny][nx]
                if (cell_content is None or  # Empty cell
                        cell_content == "-" or  # Generator
                        cell_content == "#" or  # Dropzone
                        cell_content == "*"):  # Special traversable cell
                    queue.append((nx, ny))
                    visited.add((nx, ny))

        return False

    def ensure_all_paths(self):
        """Remove obstacles if needed to ensure all paths exist"""
        # Find all generators and dropzones
        generators = []
        dropzones = []

        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.matrix[y][x] == "-":  # Generator
                    generators.append((x, y))
                elif self.grid.matrix[y][x] == "#":  # Dropzone
                    dropzones.append((x, y))

        # Find all obstacles
        obstacles = []
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.matrix[y][x] == self.obstacle_char:
                    obstacles.append((x, y))

        # If all paths exist, no need to remove obstacles
        if self._all_paths_exist(generators, dropzones):
            return []

        # Otherwise, try removing obstacles one by one until paths exist
        random.shuffle(obstacles)  # Randomize order of obstacles to remove
        removed_obstacles = []

        for obs_x, obs_y in obstacles:
            # Remove the obstacle
            self.grid.matrix[obs_y][obs_x] = None
            removed_obstacles.append((obs_x, obs_y))

            # Check if all paths exist now
            if self._all_paths_exist(generators, dropzones):
                break

        return removed_obstacles