import pygame
import random
import neat
import math
import copy
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
                      DAY_LENGTH, TERRAINS)

class Creature:
    def __init__(self, world_map, assets, genome, config, archetype, tribe_id, tribe_color, nest_pos=None):
        self.world_map = world_map
        self.assets = assets
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.archetype = archetype
        self.tribe_id = tribe_id
        self.tribe_color = tribe_color
        self.name = self.archetype['name']
        self.diet = self.archetype['diet']
        self.prey_archetypes = self.archetype['prey_archetypes']
        self.predator_archetypes = self.archetype['predator_archetypes']
        attrs = self.archetype['base_attributes']
        self.max_speed = attrs['max_speed']
        self.vision_radius = attrs['vision_radius']
        self.max_energy = attrs['max_energy']
        self.energy_per_food = attrs.get('energy_per_plant', attrs.get('energy_per_kill', 300))
        self.reproduction_urge_threshold = attrs['reproduction_urge_threshold']
        self.lifespan = attrs['lifespan']
        self.nest_sprite = assets[self.archetype['nest_sprite_key']]
        if nest_pos: self.nest_x, self.nest_y = nest_pos
        else: self.nest_x, self.nest_y = self._find_spawn_point()
        self.x, self.y = self.nest_x, self.nest_y
        self.angle = random.uniform(0, 2 * math.pi)
        self.energy = self.max_energy
        self.age = 0
        self.reproduction_urge = 0.0
        self.night_vision_gene = random.random() < 0.2
        self.state = 'exploring'
        self.flee_timer = 0
        self.tiredness = 0.0
        self.target = None
        self.animation_timer = 0
        self.animation_frame_index = 0
        self.visual_dna = {
            'body_size_mod': random.uniform(0.9, 1.1),
            'pattern_type': random.choice(['none', 'stripes', 'spots']),
            'pattern_color': tuple(max(0, min(255, c + random.randint(-20, 20))) for c in self.tribe_color)
        }

    def update(self, all_creatures, foods, time_info):
        effective_vision, time_of_day_norm, is_night = self._update_common_state(time_info)
        self._manage_state()

        if self.state in ['sleeping', 'going_to_sleep']:
            self.handle_sleeping_states()
            return
        if self.state == 'fleeing':
            self.flee_timer -= 1
            if self.flee_timer <= 0: self.state = 'exploring'

        visible_creatures = [c for c in all_creatures if c != self and math.hypot(self.x - c.x, self.y - c.y) < effective_vision]
        flockmates = [c for c in visible_creatures if c.tribe_id == self.tribe_id and c.name == self.name]

        panicked_mate = next((mate for mate in flockmates if mate.state == 'fleeing'), None)
        sensed_threat = min([c for c in visible_creatures if c.name in self.predator_archetypes], key=lambda c: math.hypot(self.x - c.x, self.y - c.y), default=None)

        if self.state != 'fleeing' and (sensed_threat or panicked_mate):
            self.state = 'fleeing'
            self.flee_timer = 150

        if panicked_mate and not sensed_threat:
             sensed_threat = {'x': self.x - math.cos(panicked_mate.angle) * 100, 'y': self.y - math.sin(panicked_mate.angle) * 100}

        separation_vec, alignment_vec, cohesion_vec, center_of_mass = self.calculate_boids_vectors(flockmates)

        sensed_food_plant = min([f for f in foods if math.hypot(self.x - f.x, self.y - f.y) < effective_vision], key=lambda f: math.hypot(self.x - f.x, self.y - f.y), default=None) if self.diet['plants'] else None
        sensed_prey = self.find_best_prey(visible_creatures) if self.diet['meat'] else None

        sensed_food = sensed_prey or sensed_food_plant
        if sensed_prey and sensed_food_plant:
            sensed_food = sensed_prey if math.hypot(self.x-sensed_prey.x, self.y-sensed_prey.y) < math.hypot(self.x-sensed_food_plant.x, self.y-sensed_food_plant.y) else sensed_food_plant
        self.target = sensed_food or sensed_threat

        sensed_mate = min([c for c in flockmates if c.reproduction_urge > 0.9], key=lambda c: math.hypot(self.x-c.x, self.y-c.y), default=None) if self.reproduction_urge > 0.9 else None
        sensed_rival = min([c for c in visible_creatures if c.tribe_id != self.tribe_id], key=lambda r: math.hypot(self.x-r.x, self.y-r.y), default=None)

        food_dx, food_dy = self.get_vector_to(sensed_food, effective_vision)
        pred_dx, pred_dy = self.get_vector_to(sensed_threat, effective_vision)
        mate_dx, mate_dy = self.get_vector_to(sensed_mate, effective_vision)
        rival_dx, rival_dy = self.get_vector_to(sensed_rival, effective_vision)
        nest_dx, nest_dy = self.get_vector_to({'x': self.nest_x, 'y': self.nest_y}, 10000)
        num_tribemates = len(flockmates)
        tribemate_center_dx, tribemate_center_dy = self.get_vector_to(center_of_mass, effective_vision) if flockmates else (0,0)

        inputs = (
            food_dx, food_dy, pred_dx, pred_dy, mate_dx, mate_dy,
            num_tribemates / 10.0, tribemate_center_dx, tribemate_center_dy,
            rival_dx, rival_dy, nest_dx, nest_dy,
            time_of_day_norm, self.tiredness / 150.0,
            cohesion_vec.x, cohesion_vec.y, alignment_vec.x, alignment_vec.y, separation_vec.x, separation_vec.y,
            1.0 if self.state == 'fleeing' else 0.0
        )

        outputs = self.net.activate(inputs)
        if self.state == 'exploring' and outputs[2] > 0.5:
            self.state = 'going_to_sleep'
        self._move(outputs)

    def find_best_prey(self, visible_creatures):
        possible_prey = [c for c in visible_creatures if c.name in self.prey_archetypes]
        if not possible_prey: return None
        prey_scores = {}
        for prey in possible_prey:
            prey_flockmates = [m for m in visible_creatures if m.tribe_id == prey.tribe_id and m.name == prey.name]
            dist_to_predator = math.hypot(self.x - prey.x, self.y - prey.y)
            isolation_score = 10000
            if prey_flockmates:
                prey_center = pygame.Vector2(sum(m.x for m in prey_flockmates) / len(prey_flockmates), sum(m.y for m in prey_flockmates) / len(prey_flockmates))
                isolation_score = math.hypot(prey.x - prey_center.x, prey.y - prey_center.y)
            prey_scores[prey] = isolation_score - dist_to_predator * 0.5
        return max(prey_scores, key=prey_scores.get) if prey_scores else None

    def calculate_boids_vectors(self, flockmates):
        if not flockmates: return pygame.Vector2(0,0), pygame.Vector2(0,0), pygame.Vector2(0,0), None
        center_of_mass = pygame.Vector2(sum(c.x for c in flockmates) / len(flockmates), sum(c.y for c in flockmates) / len(flockmates))
        cohesion_vec = (center_of_mass - pygame.Vector2(self.x, self.y)).normalize() if center_of_mass.distance_to(pygame.Vector2(self.x, self.y)) > 0 else pygame.Vector2(0,0)
        avg_heading = pygame.Vector2(sum(math.cos(c.angle) for c in flockmates), sum(math.sin(c.angle) for c in flockmates))
        if avg_heading.length() > 0: avg_heading.normalize_ip()
        separation_vec = pygame.Vector2(0,0)
        for mate in flockmates:
            if math.hypot(self.x - mate.x, self.y - mate.y) < CELL_SIZE * 2.5:
                separation_vec += (pygame.Vector2(self.x, self.y) - pygame.Vector2(mate.x, mate.y))
        if separation_vec.length() > 0: separation_vec.normalize_ip()
        return separation_vec, avg_heading, cohesion_vec, center_of_mass

    def handle_sleeping_states(self):
        if self.state == 'going_to_sleep':
            self.target = pygame.Rect(self.nest_x, self.nest_y, 1, 1)
            nest_dx, nest_dy = self.get_vector_to({'x': self.nest_x, 'y': self.nest_y}, 10000)
            angle_to_nest = math.atan2(nest_dy, nest_dx)
            angle_diff = (angle_to_nest - self.angle + math.pi) % (2 * math.pi) - math.pi
            outputs = [angle_diff, 1.0, -1.0]
            self._move(outputs)
        elif self.state == 'sleeping': self.target = None

    def _find_spawn_point(self):
        while True:
            grid_x, grid_y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if self.world_map[grid_x][grid_y]["type"] not in ["DEEP_WATER", "SHALLOW_WATER", "MOUNTAIN"]:
                return (grid_x * CELL_SIZE + CELL_SIZE // 2, grid_y * CELL_SIZE + CELL_SIZE // 2)
    def get_vector_to(self, target_pos, max_dist):
        if not target_pos: return 0, 0
        target_x = target_pos.x if hasattr(target_pos, 'x') else target_pos.get('x',0)
        target_y = target_pos.y if hasattr(target_pos, 'y') else target_pos.get('y',0)
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > max_dist or dist == 0: return 0, 0
        return dx / dist, dy / dist
    def is_dead(self):
        return self.energy <= 0 or self.age > self.lifespan
    def reproduce(self, partner, config):
        child_genome = copy.deepcopy(self.genome)
        self.energy -= self.max_energy * 0.4
        partner.energy -= self.max_energy * 0.4
        self.reproduction_urge, partner.reproduction_urge = 0, 0
        return Creature(self.world_map, self.assets, child_genome, config, self.archetype, self.tribe_id, self.tribe_color, nest_pos=(self.nest_x, self.nest_y))
    def _update_common_state(self, time_info):
        self.age += 1
        self.energy -= 0.25
        if self.state != 'sleeping': self.tiredness += 0.1
        if self.energy > self.reproduction_urge_threshold and self.age > 1000: self.reproduction_urge = min(1.0, self.reproduction_urge + 0.005)
        time_of_day_norm = time_info['world_time'] / DAY_LENGTH
        is_night = 0.25 < time_of_day_norm < 0.75
        effective_vision = self.vision_radius * (0.3 if is_night and not self.night_vision_gene else 1.0)
        return effective_vision, time_of_day_norm, is_night
    def _manage_state(self):
        if self.state == 'going_to_sleep' and math.hypot(self.x - self.nest_x, self.y - self.nest_y) < CELL_SIZE:
            self.state = 'sleeping'
            self.angle = random.uniform(0, 2 * math.pi)
        if self.state == 'sleeping':
            self.tiredness = max(0, self.tiredness - 1.5)
            self.energy = min(self.max_energy, self.energy + 2.0)
            if self.tiredness <= 0 and self.energy > self.max_energy * 0.95:
                self.state = 'exploring'
    def _move(self, outputs):
        move_angle_offset = outputs[0] * math.pi / 2
        speed_multiplier = (outputs[1] + 1) / 2
        self.angle += move_angle_offset
        speed = self.max_speed * speed_multiplier
        dx, dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        if not (0 <= self.x + dx < SCREEN_WIDTH and 0 <= self.y + dy < SCREEN_HEIGHT):
            self.angle += math.pi
        else:
            self.x, self.y = self.x + dx, self.y + dy
        grid_x, grid_y = int(self.x // CELL_SIZE), int(self.y // CELL_SIZE)
        self.energy -= (speed * 0.1) * self.world_map[grid_x][grid_y]['properties']['energy_cost']
