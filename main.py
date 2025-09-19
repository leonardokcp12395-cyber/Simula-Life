import pygame
import sys
import os
import neat
import random
import math
import pickle

from settings import *
from entities.archetypes import CREATURE_ARCHETYPES
from entities.creature import Creature
from entities.food import Food
from core.world_management import generate_world, manage_environment
from rendering.assets import generate_visual_assets
from rendering.drawing import (draw_world, draw_time_overlay, draw_inspector_panel,
                               draw_main_ui, draw_god_mode_ui, draw_statistics_panel)

SAVE_FILE = "simulation_save.pkl"

def save_simulation(world, creatures, foods, time_info, neat_pop, history):
    state = {
        'world': world, 'creatures': creatures, 'foods': foods, 'time_info': time_info,
        'neat_population': neat_pop.population, 'neat_species': neat_pop.species,
        'neat_generation': neat_pop.generation, 'random_state': random.getstate(),
        'population_history': history,
    }
    try:
        with open(SAVE_FILE, 'wb') as f: pickle.dump(state, f)
        print(f"--- Simulation state saved to {SAVE_FILE} ---")
    except Exception as e: print(f"Error saving simulation: {e}")

def load_simulation():
    try:
        with open(SAVE_FILE, 'rb') as f: state = pickle.load(f)
        print(f"--- Simulation state loaded from {SAVE_FILE} ---")
        return state
    except FileNotFoundError:
        print(f"Save file not found: {SAVE_FILE}"); return None
    except Exception as e:
        print(f"Error loading simulation: {e}"); return None

def run(config_file):
    # --- State Variables ---
    is_paused = False
    simulation_speed = 1
    current_tool = None
    selected_creature = None
    show_stats_panel = False

    # --- NEAT Setup ---
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    # --- Pygame Init ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulador de Ecossistema Digital")
    clock = pygame.time.Clock()

    assets = generate_visual_assets()
    world = generate_world(random.randint(0, 1000))

    # --- Initial Population ---
    creatures = []
    initial_genomes = list(p.population.values())
    archetype_list = list(CREATURE_ARCHETYPES.keys())
    for i, genome in enumerate(initial_genomes):
        genome.fitness = 0
        tribe_id = i % NUMBER_OF_TRIBES_PER_SPECIES
        tribe_color = TRIBE_COLORS[tribe_id]

        archetype_name = archetype_list[i % len(archetype_list)]
        archetype = CREATURE_ARCHETYPES[archetype_name]
        creatures.append(Creature(world, assets, genome, config, archetype, tribe_id, tribe_color))

    foods = [Food(world, assets) for _ in range(150)]
    time_info = {'world_time': 0, 'season_timer': 0, 'current_season': "Primavera"}
    generation_timer = 0
    population_history = []

    # --- Main Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: is_paused = not is_paused
                if event.key == pygame.K_g: show_stats_panel = not show_stats_panel
                if event.key == pygame.K_F5: save_simulation(world, creatures, foods, time_info, p, population_history)
                if event.key == pygame.K_F9:
                    state = load_simulation()
                    if state:
                        world, creatures, foods, time_info, population_history = state['world'], state['creatures'], state['foods'], state['time_info'], state.get('population_history', [])
                        p.population, p.species, p.generation = state['neat_population'], state['neat_species'], state['neat_generation']
                        random.setstate(state['random_state'])
                        for c in creatures: c.net = neat.nn.FeedForwardNetwork.create(c.genome, config)
                        print("--- Simulation state fully restored. ---")

                if event.key == pygame.K_RIGHT: simulation_speed = min(5, simulation_speed + 1)
                if event.key == pygame.K_LEFT: simulation_speed = max(1, simulation_speed - 1)
                if event.key == pygame.K_f: current_tool = "spawn_food"
                if event.key == pygame.K_h: current_tool = "spawn_herbivore"
                if event.key == pygame.K_c: current_tool = "spawn_carnivore"
                if event.key == pygame.K_j: current_tool = "spawn_human"
                if event.key == pygame.K_k: current_tool = "spawn_feline"
                if event.key == pygame.K_x: current_tool = "smite"
                if event.key == pygame.K_ESCAPE: current_tool = None; selected_creature = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 3: current_tool = None
                elif current_tool:
                    genome = random.choice(list(p.population.values()))
                    tribe_id = random.randint(0, NUMBER_OF_TRIBES_PER_SPECIES - 1)
                    tribe_color = TRIBE_COLORS[tribe_id]

                    archetype_map = {
                        "spawn_herbivore": "herbivore_generic",
                        "spawn_carnivore": "carnivore_generic",
                        "spawn_human": "human",
                        "spawn_feline": "feline"
                    }
                    if current_tool == "spawn_food": foods.append(Food(world, assets, pos))
                    elif current_tool in archetype_map:
                        archetype = CREATURE_ARCHETYPES[archetype_map[current_tool]]
                        creatures.append(Creature(world, assets, genome, config, archetype, tribe_id, tribe_color, nest_pos=pos))
                    elif current_tool == "smite":
                        for c in creatures[:]:
                            if math.hypot(pos[0]-c.x, pos[1]-c.y) < CELL_SIZE:
                                creatures.remove(c)
                elif creatures:
                    selected_creature = min(creatures, key=lambda c: math.hypot(pos[0]-c.x, pos[1]-c.y), default=None)

        # --- Update Logic & Interactions ---
        if not is_paused:
            for _ in range(simulation_speed):
                time_info = manage_environment(time_info, foods, world, assets)
                generation_timer += 1
                new_creatures = []

                for creature in creatures: creature.update(creatures, foods, time_info)

                for creature in creatures[:]:
                    if creature.is_dead(): creatures.remove(creature); continue
                    if creature.diet['plants']:
                        for food in foods[:]:
                            if math.hypot(creature.x - food.x, creature.y - food.y) < CELL_SIZE:
                                creature.energy = min(creature.max_energy, creature.energy + creature.energy_per_food); foods.remove(food); creature.genome.fitness += 5; break
                    if creature.diet['meat']:
                        for prey in creatures[:]:
                            if creature != prey and prey.name in creature.prey_archetypes and math.hypot(creature.x - prey.x, creature.y - prey.y) < CELL_SIZE:
                                creature.energy = min(creature.max_energy, creature.energy + creature.energy_per_food); creatures.remove(prey); creature.genome.fitness += 25; break
                    if creature.reproduction_urge > 1.0:
                        for partner in creatures:
                            if creature != partner and creature.name == partner.name and partner.reproduction_urge > 1.0 and math.hypot(creature.x - partner.x, creature.y - partner.y) < CELL_SIZE:
                                new_creatures.append(creature.reproduce(partner, config)); creature.genome.fitness += 20; partner.genome.fitness += 20; break

                creatures.extend(new_creatures)
                for c in creatures: c.genome.fitness = c.age

                if time_info['world_time'] == 0:
                    counts = {archetype['name']: 0 for archetype in CREATURE_ARCHETYPES.values()}
                    for c in creatures: counts[c.name] += 1
                    population_history.append(counts)

                if generation_timer > SEASON_LENGTH * 2:
                    print("\n--- EVOLVING BRAINS ---")
                    p.run(lambda genomes, cfg: [setattr(g, 'fitness', c.genome.fitness) for _, c in enumerate(creatures) for g_id, g in genomes if c.genome.key == g_id], 1)
                    genomes = list(p.population.values());
                    for c in creatures: c.genome = random.choice(genomes); c.net = neat.nn.FeedForwardNetwork.create(c.genome, config)
                    generation_timer = 0

        # --- Drawing ---
        draw_world(screen, world, assets['terrain'])
        draw_time_overlay(screen, time_info['world_time'])
        for f in foods: f.draw(screen)
        for c in creatures: c.draw(screen, c == selected_creature)

        creature_counts = {archetype['name']: len([c for c in creatures if c.name == archetype['name']]) for archetype in CREATURE_ARCHETYPES.values()}

        draw_main_ui(screen, time_info, creature_counts, simulation_speed)
        draw_inspector_panel(screen, selected_creature)
        draw_god_mode_ui(screen, current_tool)
        if show_stats_panel: draw_statistics_panel(screen, population_history)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
