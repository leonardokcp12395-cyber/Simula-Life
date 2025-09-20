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
                               draw_main_ui, draw_god_mode_ui, draw_statistics_panel, draw_creature)

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
        # ... (event handling code remains the same) ...

        # --- Update Logic & Interactions ---
        # ... (update logic remains the same) ...

        # --- Drawing ---
        draw_world(screen, world, assets['terrain'])
        draw_time_overlay(screen, time_info['world_time'])

        for f in foods: f.draw(screen)
        for c in creatures:
            draw_creature(screen, c, c == selected_creature) # Use the new procedural drawing function

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
