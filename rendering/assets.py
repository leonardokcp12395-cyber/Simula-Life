import pygame
import random
import math
from settings import CELL_SIZE, TERRAINS, NUMBER_OF_TRIBES_PER_SPECIES, TRIBE_COLORS
from entities.archetypes import CREATURE_ARCHETYPES

def generate_visual_assets():
    """
    Generates and returns a dictionary with all visual assets for the simulation.
    Creature sprites are now generated dynamically, so this function only handles static assets.
    """
    assets = {}

    # 1. Generate Terrain Textures
    terrain_surfaces = {}
    for key, data in TERRAINS.items():
        base_color = data["color"]
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(base_color)
        for _ in range(10):
            noise_color = tuple(max(0, c - random.randint(10, 20)) for c in base_color)
            rx, ry = random.randint(0, CELL_SIZE - 2), random.randint(0, CELL_SIZE - 2)
            surface.set_at((rx, ry), noise_color)
        terrain_surfaces[key] = surface
    assets['terrain'] = terrain_surfaces

    # 2. Generate Nest Sprites (can be made data-driven later)
    assets['herbivore_nest'] = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(assets['herbivore_nest'], (139, 69, 19, 150), (CELL_SIZE // 2, CELL_SIZE // 2), 7)
    pygame.draw.circle(assets['herbivore_nest'], (0, 0, 0, 200), (CELL_SIZE // 2, CELL_SIZE // 2), 4)

    assets['carnivore_nest'] = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(assets['carnivore_nest'], (112, 128, 144, 180), (CELL_SIZE // 2, CELL_SIZE // 2), 8)
    pygame.draw.rect(assets['carnivore_nest'], (0, 0, 0, 220), (CELL_SIZE//2 - 4, CELL_SIZE//2 - 2, 8, 5))

    human_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.line(human_nest_sprite, (139, 69, 19), (4, 10), (12, 5), 2)
    pygame.draw.line(human_nest_sprite, (139, 69, 19), (4, 5), (12, 10), 2)
    pygame.draw.polygon(human_nest_sprite, (255, 165, 0), [(8,9), (6,6), (10,6)])
    assets['human_nest'] = human_nest_sprite

    # 3. Generate Food Sprite
    food_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food_sprite, (60, 180, 60), (CELL_SIZE // 2, CELL_SIZE // 2), 4)
    assets['food'] = food_sprite

    # 4. Generate Shadow Sprite
    shadow_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_sprite, (0, 0, 0, 100), (1, CELL_SIZE-4, CELL_SIZE-2, 4))
    assets['shadow'] = shadow_sprite

    return assets
