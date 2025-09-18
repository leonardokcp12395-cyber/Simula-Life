import pygame
import random
import neat
import math
import copy
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, DAY_LENGTH

# (imports no topo permanecem os mesmos)

class Creature:
    def __init__(self, world_map, assets, genome, config, tribe_id, tribe_color, nest_pos=None):
        # ... (inicialização como antes) ...
        self.tribe_id = tribe_id
        self.tribe_color = tribe_color
        # ... (o resto do __init__ permanece igual)

    def draw(self, screen, is_selected):
        # ... (a lógica de desenhar o ninho e a criatura permanece a mesma,
        # mas agora o sprite da criatura já terá a cor da tribo)
    
    # ... (outras funções como _update_memory, get_info, etc., permanecem as mesmas)

class Herbivore(Creature):
    def __init__(self, world_map, assets, genome, config, tribe_id, tribe_color, nest_pos=None):
        super().__init__(world_map, assets, genome, config, tribe_id, tribe_color, nest_pos)
        self.base_sprite = assets[f'herbivore_base_{tribe_id}'] # Sprite específico da tribo
        self.nest_sprite = assets['herbivore_nest']

    def update(self, foods, carnivores, herbivores, time_info):
        # ... (cálculo de effective_vision como antes) ...

        # 1. Sentir
        # ... (encontrar comida, predador como antes)
        
        # (MODIFICADO) Distinguir entre companheiros e rivais
        tribemates = [h for h in herbivores if h != self and h.tribe_id == self.tribe_id and math.hypot(self.x-h.x, self.y-h.y) < effective_vision]
        rivals = [h for h in herbivores if h.tribe_id != self.tribe_id and math.hypot(self.x-h.x, self.y-h.y) < effective_vision]

        sensed_mate = min([tm for tm in tribemates if tm.reproduction_urge > 0.5], key=lambda tm: math.hypot(self.x-tm.x, self.y-tm.y), default=None) if self.reproduction_urge > 0.5 else None
        sensed_rival = min(rivals, key=lambda r: math.hypot(self.x-r.x, self.y-r.y), default=None)
        
        # ... (lógica de memória como antes) ...

        # 3. Preparar Inputs
        # ... (food_dx, food_dy, pred_dx, pred_dy, mate_dx, mate_dy como antes) ...
        
        num_tribemates = len(tribemates)
        tribemate_center_dx, tribemate_center_dy = 0,0
        if num_tribemates > 0:
            avg_x = sum(a.x for a in tribemates) / num_tribemates
            avg_y = sum(a.y for a in tribemates) / num_tribemates
            tribemate_center_dx, tribemate_center_dy = self.get_vector_to({'x': avg_x, 'y': avg_y}, effective_vision)

        rival_dx, rival_dy = self.get_vector_to(sensed_rival.__dict__ if sensed_rival else None, effective_vision)
        
        # ... (memória e ninho como antes) ...
        
        inputs = (food_dx, food_dy, pred_dx, pred_dy, mate_dx, mate_dy, 
                  num_tribemates / 10.0, tribemate_center_dx, tribemate_center_dy,
                  rival_dx, rival_dy, # Novos inputs
                  mem_food_dx, mem_food_dy, nest_dx, nest_dy, time_of_day_norm)
        
        # ... (resto do update como antes) ...

class Carnivore(Creature):
    # (Fazer modificações semelhantes para a classe Carnivore,
    # onde eles procuram outros carnívoros como 'tribemates' e 'rivals')

