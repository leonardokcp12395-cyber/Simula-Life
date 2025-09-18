import pygame
import random
from settings import CELL_SIZE, TERRAINS, NUMBER_OF_TRIBES_PER_SPECIES, TRIBE_COLORS

def generate_visual_assets():
    """Generates and returns a dictionary with all visual assets for the simulation."""
    assets = {}

    # 1. Generate Terrain Textures
    terrain_surfaces = {}
    for key, data in TERRAINS.items():
        base_color = data["color"]
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(base_color)
        # Add some simple noise to the terrain to make it less flat
        for _ in range(10):
            noise_color = tuple(max(0, c - random.randint(10, 20)) for c in base_color)
            rx, ry = random.randint(0, CELL_SIZE - 2), random.randint(0, CELL_SIZE - 2)
            surface.set_at((rx, ry), noise_color)
        terrain_surfaces[key] = surface
    assets['terrain'] = terrain_surfaces

    # 2. Generate Creature Sprites for each Tribe
    for i in range(NUMBER_OF_TRIBES_PER_SPECIES):
        tribe_color = TRIBE_COLORS[i % len(TRIBE_COLORS)]

        # Herbivore Sprite (upward-facing triangle)
        herb_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(herb_sprite, tribe_color, [
            (CELL_SIZE // 2, 2),
            (2, CELL_SIZE - 2),
            (CELL_SIZE - 2, CELL_SIZE - 2)
        ])
        assets[f'herbivore_base_{i}'] = herb_sprite

        # Carnivore Sprite (diamond shape)
        carn_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(carn_sprite, tribe_color, [
            (CELL_SIZE // 2, 2),
            (CELL_SIZE - 2, CELL_SIZE // 2),
            (CELL_SIZE // 2, CELL_SIZE - 2),
            (2, CELL_SIZE // 2)
        ])
        assets[f'carnivore_base_{i}'] = carn_sprite

    # 3. Generate Food Sprite
    food_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food_sprite, (60, 180, 60), (CELL_SIZE // 2, CELL_SIZE // 2), 4) # Green circle for food
    assets['food'] = food_sprite

    # 4. Generate Nest Sprites
    # Herbivore Nest (a simple burrow)
    herb_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(herb_nest_sprite, (139, 69, 19, 150), (CELL_SIZE // 2, CELL_SIZE // 2), 7) # Brown, semi-transparent base
    pygame.draw.circle(herb_nest_sprite, (0, 0, 0, 200), (CELL_SIZE // 2, CELL_SIZE // 2), 4) # Dark hole
    assets['herbivore_nest'] = herb_nest_sprite

    # Carnivore Nest (a rocky den)
    carn_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(carn_nest_sprite, (112, 128, 144, 180), (CELL_SIZE // 2, CELL_SIZE // 2), 8) # Grey rock base
    pygame.draw.rect(carn_nest_sprite, (0, 0, 0, 220), (CELL_SIZE//2 - 4, CELL_SIZE//2 - 2, 8, 5)) # Dark entrance
    assets['carnivore_nest'] = carn_nest_sprite

    # 5. Generate Shadow Sprite
    shadow_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_sprite, (0, 0, 0, 100), (1, CELL_SIZE-4, CELL_SIZE-2, 4))
    assets['shadow'] = shadow_sprite

    return assets
