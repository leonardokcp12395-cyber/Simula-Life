import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE

class Food:
    def __init__(self, world_map, assets, pos=None):
        self.world_map = world_map
        if pos: self.x, self.y = pos
        else: self.x, self.y = self._find_spawn_point()
        self.energy = 250
        self.sprite = assets['food']
        self.shadow = assets['shadow']
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    def _find_spawn_point(self):
        while True:
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)
            grid_x, grid_y = int(x // CELL_SIZE), int(y // CELL_SIZE)
            if self.world_map[grid_y][grid_x]["type"] in ["GRASSLAND", "FOREST"]:
                return x, y

    def draw(self, screen):
        self.rect.center = (int(self.x), int(self.y))
        screen.blit(self.shadow, self.rect)
        screen.blit(self.sprite, self.rect)
