import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

class Food:
    def __init__(self, world_map, assets, pos=None):
        self.world_map = world_map
        if pos:
            self.x, self.y = pos
        else:
            self.x, self.y = self._find_spawn_point()

        self.energy = 250
        self.sprite = assets['food']
        self.shadow = assets['shadow']
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    def _find_spawn_point(self):
        """Finds a valid random spawn point on the map."""
        while True:
            # Choose a random grid cell
            grid_x = random.randint(0, GRID_WIDTH - 1)
            grid_y = random.randint(0, GRID_HEIGHT - 1)

            # Check if the terrain is valid for spawning
            if self.world_map[grid_x][grid_y]["type"] in ["GRASSLAND", "FOREST", "BEACH"]:
                # Return the pixel coordinates for the center of the cell
                return (grid_x * CELL_SIZE + CELL_SIZE // 2, grid_y * CELL_SIZE + CELL_SIZE // 2)

    def draw(self, screen):
        """Draws the food item on the screen."""
        self.rect.center = (int(self.x), int(self.y))
        screen.blit(self.shadow, self.rect)
        screen.blit(self.sprite, self.rect)
