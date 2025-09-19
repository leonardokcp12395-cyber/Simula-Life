import pygame
import random
import math
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
        for _ in range(10):
            noise_color = tuple(max(0, c - random.randint(10, 20)) for c in base_color)
            rx, ry = random.randint(0, CELL_SIZE - 2), random.randint(0, CELL_SIZE - 2)
            surface.set_at((rx, ry), noise_color)
        terrain_surfaces[key] = surface
    assets['terrain'] = terrain_surfaces

    # 2. Generate Animated Creature Sprites for each Tribe
    for i in range(NUMBER_OF_TRIBES_PER_SPECIES):
        tribe_color = TRIBE_COLORS[i % len(TRIBE_COLORS)]

        # --- Herbivore Animation Frames (Breathing) ---
        herb_frames = []
        for frame in range(4): # 4 frames for the animation
            herb_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Body swells and shrinks
            body_height = 8 + math.sin(frame / 4 * 2 * math.pi) * 1
            body_rect = pygame.Rect(3, 5, 10, body_height)
            pygame.draw.ellipse(herb_sprite, tribe_color, body_rect)
            # Head
            head_color = tuple(min(255, c + 30) for c in tribe_color)
            pygame.draw.polygon(herb_sprite, head_color, [(8, 5), (5, 1), (11, 1)])
            herb_frames.append(herb_sprite)
        assets[f'herbivore_base_{i}'] = herb_frames

        # --- Carnivore Animation Frames (Jaw snap) ---
        carn_frames = []
        for frame in range(4):
            carn_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Body
            pygame.draw.rect(carn_sprite, tribe_color, pygame.Rect(2, 6, 12, 7), border_radius=2)
            # Jaw moves slightly
            jaw_y_offset = math.sin(frame / 4 * 2 * math.pi) * 1
            jaw_color = tuple(min(255, c + 30) for c in tribe_color)
            pygame.draw.polygon(carn_sprite, jaw_color, [(8, 6), (4, 3 + jaw_y_offset), (12, 3 + jaw_y_offset)])
            carn_frames.append(carn_sprite)
        assets[f'carnivore_base_{i}'] = carn_frames

    # 3. Generate Food Sprite
    food_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food_sprite, (60, 180, 60), (CELL_SIZE // 2, CELL_SIZE // 2), 4)
    assets['food'] = food_sprite

    # 4. Generate Nest Sprites
    herb_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(herb_nest_sprite, (139, 69, 19, 150), (CELL_SIZE // 2, CELL_SIZE // 2), 7)
    pygame.draw.circle(herb_nest_sprite, (0, 0, 0, 200), (CELL_SIZE // 2, CELL_SIZE // 2), 4)
    assets['herbivore_nest'] = herb_nest_sprite

    carn_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(carn_nest_sprite, (112, 128, 144, 180), (CELL_SIZE // 2, CELL_SIZE // 2), 8)
    pygame.draw.rect(carn_nest_sprite, (0, 0, 0, 220), (CELL_SIZE//2 - 4, CELL_SIZE//2 - 2, 8, 5))
    assets['carnivore_nest'] = carn_nest_sprite

    # 5. Generate Shadow Sprite
    shadow_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_sprite, (0, 0, 0, 100), (1, CELL_SIZE-4, CELL_SIZE-2, 4))
    assets['shadow'] = shadow_sprite

    return assets
