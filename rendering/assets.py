import pygame
import random
import math
from settings import CELL_SIZE, TERRAINS, NUMBER_OF_TRIBES_PER_SPECIES, TRIBE_COLORS
from entities.archetypes import CREATURE_ARCHETYPES

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

    # 2. Generate Animated Creature Sprites for each Archetype and Tribe
    for archetype_key, archetype_data in CREATURE_ARCHETYPES.items():
        sprite_key = archetype_data['sprite_key']

        for i in range(NUMBER_OF_TRIBES_PER_SPECIES):
            tribe_color = TRIBE_COLORS[i % len(TRIBE_COLORS)]

            animation_frames = []
            for frame in range(4): # 4 frames for the animation
                sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

                if sprite_key == 'herbivore_base':
                    body_height = 8 + math.sin(frame / 4 * 2 * math.pi) * 1
                    body_rect = pygame.Rect(3, 5, 10, body_height)
                    pygame.draw.ellipse(sprite, tribe_color, body_rect)
                    head_color = tuple(min(255, c + 30) for c in tribe_color)
                    pygame.draw.polygon(sprite, head_color, [(8, 5), (5, 1), (11, 1)])

                elif sprite_key == 'carnivore_base':
                    pygame.draw.rect(sprite, tribe_color, pygame.Rect(2, 6, 12, 7), border_radius=2)
                    jaw_y_offset = math.sin(frame / 4 * 2 * math.pi) * 1
                    jaw_color = tuple(min(255, c + 30) for c in tribe_color)
                    pygame.draw.polygon(sprite, jaw_color, [(8, 6), (4, 3 + jaw_y_offset), (12, 3 + jaw_y_offset)])

                elif sprite_key == 'human_base':
                    # Body
                    body_y_offset = math.sin(frame / 4 * 2 * math.pi) * 0.5
                    pygame.draw.rect(sprite, tribe_color, pygame.Rect(5, 4 + body_y_offset, 6, 9), border_radius=1)
                    # Head
                    head_color = tuple(min(255, c + 40) for c in tribe_color)
                    pygame.draw.circle(sprite, head_color, (8, 4), 3)

                elif sprite_key == 'feline_base':
                    # Body
                    body_y_offset = math.sin(frame / 4 * 2 * math.pi) * 0.5
                    pygame.draw.ellipse(sprite, tribe_color, pygame.Rect(2, 5 + body_y_offset, 12, 6))
                    # Head
                    head_color = tuple(min(255, c + 30) for c in tribe_color)
                    pygame.draw.circle(sprite, head_color, (10, 8), 3)
                    # Tail
                    tail_angle = math.sin(frame / 4 * 2 * math.pi) * 0.2
                    pygame.draw.line(sprite, tribe_color, (3, 8), (0, 10 + tail_angle), 2)


                animation_frames.append(sprite)

            assets[f'{sprite_key}_{i}'] = animation_frames

    # 3. Generate Food Sprite
    food_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food_sprite, (60, 180, 60), (CELL_SIZE // 2, CELL_SIZE // 2), 4)
    assets['food'] = food_sprite

    # 4. Generate Nest Sprites (can be made data-driven later)
    herb_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(herb_nest_sprite, (139, 69, 19, 150), (CELL_SIZE // 2, CELL_SIZE // 2), 7)
    pygame.draw.circle(herb_nest_sprite, (0, 0, 0, 200), (CELL_SIZE // 2, CELL_SIZE // 2), 4)
    assets['herbivore_nest'] = herb_nest_sprite

    carn_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(carn_nest_sprite, (112, 128, 144, 180), (CELL_SIZE // 2, CELL_SIZE // 2), 8)
    pygame.draw.rect(carn_nest_sprite, (0, 0, 0, 220), (CELL_SIZE//2 - 4, CELL_SIZE//2 - 2, 8, 5))
    assets['carnivore_nest'] = carn_nest_sprite

    # Human Nest (campfire)
    human_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    # Logs
    pygame.draw.line(human_nest_sprite, (139, 69, 19), (4, 10), (12, 5), 2)
    pygame.draw.line(human_nest_sprite, (139, 69, 19), (4, 5), (12, 10), 2)
    # Fire
    pygame.draw.polygon(human_nest_sprite, (255, 165, 0), [(8,9), (6,6), (10,6)])
    assets['human_nest'] = human_nest_sprite

    # 5. Generate Shadow Sprite
    shadow_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_sprite, (0, 0, 0, 100), (1, CELL_SIZE-4, CELL_SIZE-2, 4))
    assets['shadow'] = shadow_sprite

    return assets
