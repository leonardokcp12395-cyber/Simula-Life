import pygame
import random
from settings import CELL_SIZE, TERRAINS

def generate_visual_assets():
    """Gera e retorna dicionários com todos os assets visuais."""
    assets = {}
    
    # Gerar texturas do terreno
    terrain_surfaces = {}
    for key, data in TERRAINS.items():
        base_color = data["color"]
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(base_color)
        for _ in range(10):
            noise_color = tuple(max(0, c - random.randint(10, 20)) for c in base_color)
            rx, ry = random.randint(0, CELL_SIZE-1), random.randint(0, CELL_SIZE-1)
            surface.set_at((rx, ry), noise_color)
        terrain_surfaces[key] = surface
    assets['terrain'] = terrain_surfaces

    # Gerar sprites
        def create_pawn_sprite(body_color, tribe_color):
        sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Corpo principal
        body_rect = pygame.Rect(CELL_SIZE//2 - 3, CELL_SIZE//2 - 4, 6, 8)
        pygame.draw.rect(sprite, body_color, body_rect, border_radius=2)
        # Detalhe da cor da tribo (como uma ombreira)
        tribe_detail_rect = pygame.Rect(CELL_SIZE//2 - 3, CELL_SIZE//2 - 4, 3, 3)
        pygame.draw.rect(sprite, tribe_color, tribe_detail_rect, border_top_left_radius=2)
        return sprite
    
    # A geração dos sprites base agora é feita em main.py,
    # por isso pode remover as linhas HERBIVORE_SPRITE = ... e CARNIVORE_SPRITE = ...
    # O resto da função permanece igual.

        
    assets['herbivore_base'] = create_pawn_sprite((100, 100, 255))
    assets['carnivore_base'] = create_pawn_sprite((255, 100, 100))

    food_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food_sprite, (34, 139, 34), (CELL_SIZE // 2, CELL_SIZE // 2 + 2), 4)
    pygame.draw.circle(food_sprite, (255, 0, 0), (CELL_SIZE // 2 - 2, CELL_SIZE // 2), 2)
    pygame.draw.circle(food_sprite, (255, 0, 0), (CELL_SIZE // 2 + 2, CELL_SIZE // 2 + 1), 2)
    assets['food'] = food_sprite

    shadow_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_sprite, (0, 0, 0, 100), (1, CELL_SIZE-4, CELL_SIZE-2, 4))
    assets['shadow'] = shadow_sprite
    
   # ... depois de gerar os outros sprites ...
    
    # Gerar sprite do ninho de herbívoro (toca)
    herb_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(herb_nest_sprite, (139, 69, 19), (CELL_SIZE // 2, CELL_SIZE // 2), 7) # Terra
    pygame.draw.circle(herb_nest_sprite, (0, 0, 0), (CELL_SIZE // 2, CELL_SIZE // 2), 4) # Buraco
    assets['herbivore_nest'] = herb_nest_sprite

    # Gerar sprite do ninho de carnívoro (den)
    carn_nest_sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(carn_nest_sprite, (112, 128, 144), (CELL_SIZE // 2, CELL_SIZE // 2), 7) # Rocha
    pygame.draw.rect(carn_nest_sprite, (0, 0, 0), (CELL_SIZE//2 - 4, CELL_SIZE//2 - 2, 8, 5)) # Entrada
    assets['carnivore_nest'] = carn_nest_sprite

    return assets