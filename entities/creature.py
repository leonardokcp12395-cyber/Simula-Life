import pygame
import random
import neat
import math
import copy
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
                      DAY_LENGTH, TERRAINS)

class Creature:
    def __init__(self, world_map, assets, genome, config, tribe_id, tribe_color, nest_pos=None):
        self.world_map = world_map
        self.assets = assets
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

        self.tribe_id = tribe_id
        self.tribe_color = tribe_color

        if nest_pos:
            self.nest_x, self.nest_y = nest_pos
        else:
            self.nest_x, self.nest_y = self._find_spawn_point()

        self.x, self.y = self.nest_x, self.nest_y
        self.angle = random.uniform(0, 2 * math.pi)

        # Core Attributes
        self.energy = 1000
        self.age = 0
        self.reproduction_urge = 0.0

        # Evolved Attributes (can be expanded)
        self.max_speed = 2.5
        self.vision_radius = 200
        self.night_vision_gene = random.random() < 0.2

        # State & Memory
        self.short_term_memory = {'food': None, 'threat': None}
        self.target = None

    def _find_spawn_point(self):
        while True:
            grid_x = random.randint(0, GRID_WIDTH - 1)
            grid_y = random.randint(0, GRID_HEIGHT - 1)
            if self.world_map[grid_x][grid_y]["type"] not in ["DEEP_WATER", "SHALLOW_WATER", "MOUNTAIN"]:
                return (grid_x * CELL_SIZE + CELL_SIZE // 2, grid_y * CELL_SIZE + CELL_SIZE // 2)

    def get_vector_to(self, target_pos, max_dist):
        if not target_pos:
            return 0, 0

        # Handle both dict and object targets
        target_x = target_pos['x'] if isinstance(target_pos, dict) else target_pos.x
        target_y = target_pos['y'] if isinstance(target_pos, dict) else target_pos.y

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > max_dist or dist == 0:
            return 0, 0

        return dx / dist, dy / dist

    def is_dead(self):
        return self.energy <= 0 or self.age > 15000 # Increased lifespan

    def reproduce(self, partner, config):
        child_genome = copy.deepcopy(self.genome)

        self.energy -= 400
        partner.energy -= 400
        self.reproduction_urge = 0
        partner.reproduction_urge = 0

        return self.__class__(self.world_map, self.assets, child_genome, config, self.tribe_id, self.tribe_color, nest_pos=(self.nest_x, self.nest_y))

    def _update_common_state(self, time_info):
        self.age += 1
        self.energy -= 0.25 # Base energy decay

        if self.energy > 800 and self.age > 1000:
            self.reproduction_urge = min(1.0, self.reproduction_urge + 0.005)

        time_of_day_norm = time_info['world_time'] / DAY_LENGTH
        is_night = 0.25 < time_of_day_norm < 0.75

        effective_vision = self.vision_radius
        if is_night and not self.night_vision_gene:
            effective_vision *= 0.3

        return effective_vision, time_of_day_norm

    def _move(self, outputs):
        move_angle_offset = outputs[0] * math.pi / 2 # More subtle turning
        speed_multiplier = (outputs[1] + 1) / 2

        self.angle += move_angle_offset
        speed = self.max_speed * speed_multiplier

        dx = math.cos(self.angle) * speed
        dy = math.sin(self.angle) * speed

        # Check for world boundaries before moving
        if not (0 <= self.x + dx < SCREEN_WIDTH and 0 <= self.y + dy < SCREEN_HEIGHT):
            self.angle += math.pi # Turn around if about to hit a wall
        else:
            self.x += dx
            self.y += dy

        grid_x, grid_y = int(self.x // CELL_SIZE), int(self.y // CELL_SIZE)
        terrain_cost = self.world_map[grid_x][grid_y]['properties']['energy_cost']
        self.energy -= (speed * 0.1) * terrain_cost

    def draw(self, screen, is_selected):
        nest_rect = self.nest_sprite.get_rect(center=(self.nest_x, self.nest_y))
        screen.blit(self.nest_sprite, nest_rect)

        rotated_sprite = pygame.transform.rotate(self.base_sprite, -math.degrees(self.angle) + 90)
        rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))

        shadow_rect = self.assets['shadow'].get_rect(center=(int(self.x+2), int(self.y+2)))
        screen.blit(self.assets['shadow'], shadow_rect)
        screen.blit(rotated_sprite, rect)

        if is_selected:
            pygame.draw.circle(screen, self.tribe_color, (int(self.x), int(self.y)), self.vision_radius, 1)
            pygame.draw.line(screen, (255, 255, 255, 100), (self.x, self.y), (self.nest_x, self.nest_y), 1)
            if self.target:
                pygame.draw.line(screen, (255, 0, 0, 150), (self.x, self.y), (self.target.x, self.target.y), 2)


class Herbivore(Creature):
    def __init__(self, world_map, assets, genome, config, tribe_id, tribe_color, nest_pos=None):
        super().__init__(world_map, assets, genome, config, tribe_id, tribe_color, nest_pos)
        self.base_sprite = assets[f'herbivore_base_{tribe_id}']
        self.nest_sprite = assets['herbivore_nest']

    def update(self, foods, carnivores, herbivores, time_info):
        effective_vision, time_of_day_norm = self._update_common_state(time_info)

        sensed_food = min([f for f in foods if math.hypot(self.x - f.x, self.y - f.y) < effective_vision], key=lambda f: math.hypot(self.x - f.x, self.y - f.y), default=None)
        sensed_threat = min([c for c in carnivores if math.hypot(self.x - c.x, self.y - c.y) < effective_vision], key=lambda c: math.hypot(self.x - c.x, self.y - c.y), default=None)

        self.target = sensed_food if sensed_food else sensed_threat

        tribemates = [h for h in herbivores if h != self and h.tribe_id == self.tribe_id and math.hypot(self.x-h.x, self.y-h.y) < effective_vision]
        rivals = [h for h in herbivores if h.tribe_id != self.tribe_id and math.hypot(self.x-h.x, self.y-h.y) < effective_vision]
        sensed_mate = min([tm for tm in tribemates if tm.reproduction_urge > 0.9], key=lambda tm: math.hypot(self.x-tm.x, self.y-tm.y), default=None) if self.reproduction_urge > 0.9 else None
        sensed_rival = min(rivals, key=lambda r: math.hypot(self.x-r.x, self.y-r.y), default=None)

        if sensed_food: self.short_term_memory['food'] = {'x': sensed_food.x, 'y': sensed_food.y}
        if sensed_threat: self.short_term_memory['threat'] = {'x': sensed_threat.x, 'y': sensed_threat.y}

        food_dx, food_dy = self.get_vector_to(sensed_food, effective_vision)
        pred_dx, pred_dy = self.get_vector_to(sensed_threat, effective_vision)
        mate_dx, mate_dy = self.get_vector_to(sensed_mate, effective_vision)

        num_tribemates = len(tribemates)
        tribemate_center_dx, tribemate_center_dy = 0, 0
        if num_tribemates > 0:
            avg_x = sum(a.x for a in tribemates) / num_tribemates
            avg_y = sum(a.y for a in tribemates) / num_tribemates
            tribemate_center_dx, tribemate_center_dy = self.get_vector_to({'x': avg_x, 'y': avg_y}, effective_vision)

        rival_dx, rival_dy = self.get_vector_to(sensed_rival, effective_vision)
        mem_food_dx, mem_food_dy = self.get_vector_to(self.short_term_memory.get('food'), effective_vision)
        nest_dx, nest_dy = self.get_vector_to({'x': self.nest_x, 'y': self.nest_y}, 10000)

        inputs = (food_dx, food_dy, pred_dx, pred_dy, mate_dx, mate_dy,
                  num_tribemates / 10.0, tribemate_center_dx, tribemate_center_dy,
                  rival_dx, rival_dy, mem_food_dx, mem_food_dy, nest_dx, nest_dy, time_of_day_norm)

        outputs = self.net.activate(inputs)
        self._move(outputs)


class Carnivore(Creature):
    def __init__(self, world_map, assets, genome, config, tribe_id, tribe_color, nest_pos=None):
        super().__init__(world_map, assets, genome, config, tribe_id, tribe_color, nest_pos)
        self.base_sprite = assets[f'carnivore_base_{tribe_id}']
        self.nest_sprite = assets['carnivore_nest']

    def update(self, herbivores, carnivores, time_info):
        effective_vision, time_of_day_norm = self._update_common_state(time_info)

        sensed_prey = min([h for h in herbivores if math.hypot(self.x - h.x, self.y - h.y) < effective_vision], key=lambda h: math.hypot(self.x - h.x, self.y - h.y), default=None)
        self.target = sensed_prey

        tribemates = [c for c in carnivores if c != self and c.tribe_id == self.tribe_id and math.hypot(self.x-c.x, self.y-c.y) < effective_vision]
        rivals = [c for c in carnivores if c.tribe_id != self.tribe_id and math.hypot(self.x-c.x, self.y-c.y) < effective_vision]
        sensed_mate = min([tm for tm in tribemates if tm.reproduction_urge > 0.9], key=lambda tm: math.hypot(self.x-tm.x, self.y-tm.y), default=None) if self.reproduction_urge > 0.9 else None
        sensed_rival = min(rivals, key=lambda r: math.hypot(self.x-r.x, self.y-r.y), default=None)

        if sensed_prey: self.short_term_memory['food'] = {'x': sensed_prey.x, 'y': sensed_prey.y}

        prey_dx, prey_dy = self.get_vector_to(sensed_prey, effective_vision)
        pred_dx, pred_dy = 0, 0
        mate_dx, mate_dy = self.get_vector_to(sensed_mate, effective_vision)

        num_tribemates = len(tribemates)
        tribemate_center_dx, tribemate_center_dy = 0, 0
        if num_tribemates > 0:
            avg_x = sum(a.x for a in tribemates) / num_tribemates
            avg_y = sum(a.y for a in tribemates) / num_tribemates
            tribemate_center_dx, tribemate_center_dy = self.get_vector_to({'x': avg_x, 'y': avg_y}, effective_vision)

        rival_dx, rival_dy = self.get_vector_to(sensed_rival, effective_vision)
        mem_prey_dx, mem_prey_dy = self.get_vector_to(self.short_term_memory.get('food'), effective_vision)
        nest_dx, nest_dy = self.get_vector_to({'x': self.nest_x, 'y': self.nest_y}, 10000)

        inputs = (prey_dx, prey_dy, pred_dx, pred_dy, mate_dx, mate_dy,
                  num_tribemates / 10.0, tribemate_center_dx, tribemate_center_dy,
                  rival_dx, rival_dy, mem_prey_dx, mem_prey_dy, nest_dx, nest_dy, time_of_day_norm)

        outputs = self.net.activate(inputs)
        self._move(outputs)
