import pygame
import sys
import os
import neat
import random
import math
import pickle

SAVE_FILE = "simulation_save.pkl"

def save_simulation(world, creatures, foods, time_info, neat_pop):
    """Saves the current simulation state to a file using pickle."""
    state = {
        'world': world,
        'creatures': creatures,
        'foods': foods,
        'time_info': time_info,
        'neat_population': neat_pop.population,
        'neat_species': neat_pop.species,
        'neat_generation': neat_pop.generation,
        'random_state': random.getstate(),
    }
    try:
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(state, f)
        print(f"--- Simulation state saved to {SAVE_FILE} ---")
    except Exception as e:
        print(f"Error saving simulation: {e}")

def load_simulation():
    """Loads a simulation state from a file."""
    try:
        with open(SAVE_FILE, 'rb') as f:
            state = pickle.load(f)
        print(f"--- Simulation state loaded from {SAVE_FILE} ---")
        return state
    except FileNotFoundError:
        print(f"Save file not found: {SAVE_FILE}")
        return None
    except Exception as e:
        print(f"Error loading simulation: {e}")
        return None

from settings import *
from entities.creature import Herbivore, Carnivore
from entities.food import Food
from core.world_management import generate_world, manage_environment
from rendering.assets import generate_visual_assets
from rendering.drawing import draw_world, draw_time_overlay, draw_inspector_panel, draw_main_ui, draw_god_mode_ui
from settings import NUMBER_OF_TRIBES_PER_SPECIES, TRIBE_COLORS

def run(config_file):
    # --- Variáveis de Estado ---
    is_paused = False
    simulation_speed = 1
    current_tool = None
    selected_creature = None
    
    # --- Configuração do NEAT ---
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    # --- Inicialização ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulador de Ecossistema Digital")
    clock = pygame.time.Clock()
    
    assets = generate_visual_assets()
    world = generate_world(random.randint(0, 1000))
    
    # --- População Inicial ---
    creatures = []
    initial_genomes = list(p.population.values())
    for i, genome in enumerate(initial_genomes):
        genome.fitness = 0
        # Assign tribe based on index
        tribe_id = i % NUMBER_OF_TRIBES_PER_SPECIES
        tribe_color = TRIBE_COLORS[tribe_id]

        if i % 4 != 0: # 75% Herbívoros
            creatures.append(Herbivore(world, assets, genome, config, tribe_id, tribe_color))
        else: # 25% Carnívoros
            creatures.append(Carnivore(world, assets, genome, config, tribe_id, tribe_color))

    foods = [Food(world, assets) for _ in range(120)]
    time_info = {'world_time': 0, 'season_timer': 0, 'current_season': "Primavera"}
    generation_timer = 0
    
    # --- Loop Principal ---
    running = True
    while running:
        # --- Gestão de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: is_paused = not is_paused
                if event.key == pygame.K_F5:
                    save_simulation(world, creatures, foods, time_info, p)
                if event.key == pygame.K_F9:
                    state = load_simulation()
                    if state:
                        world, creatures, foods, time_info = state['world'], state['creatures'], state['foods'], state['time_info']
                        p.population, p.species, p.generation = state['neat_population'], state['neat_species'], state['neat_generation']
                        random.setstate(state['random_state'])
                        # Re-create networks from genomes to be safe
                        for c in creatures:
                            c.net = neat.nn.FeedForwardNetwork.create(c.genome, config)
                        print("--- Simulation state fully restored. ---")

                if event.key == pygame.K_RIGHT: simulation_speed = min(5, simulation_speed + 1)
                if event.key == pygame.K_LEFT: simulation_speed = max(1, simulation_speed - 1)
                if event.key == pygame.K_f: current_tool = "spawn_food"
                if event.key == pygame.K_h: current_tool = "spawn_herbivore"
                if event.key == pygame.K_c: current_tool = "spawn_carnivore"
                if event.key == pygame.K_x: current_tool = "smite"
                if event.key == pygame.K_ESCAPE: current_tool = None; selected_creature = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 3: current_tool = None 
                elif current_tool:
                    genome = random.choice(list(p.population.values()))
                    if current_tool == "spawn_food": foods.append(Food(world, assets, pos))
                    elif current_tool == "spawn_herbivore":
                        tribe_id = random.randint(0, NUMBER_OF_TRIBES_PER_SPECIES - 1)
                        tribe_color = TRIBE_COLORS[tribe_id]
                        creatures.append(Herbivore(world, assets, genome, config, tribe_id, tribe_color, nest_pos=pos))
                    elif current_tool == "spawn_carnivore":
                        tribe_id = random.randint(0, NUMBER_OF_TRIBES_PER_SPECIES - 1)
                        tribe_color = TRIBE_COLORS[tribe_id]
                        creatures.append(Carnivore(world, assets, genome, config, tribe_id, tribe_color, nest_pos=pos))
                    elif current_tool == "smite":
                        for c in creatures[:]:
                            if math.hypot(pos[0]-c.x, pos[1]-c.y) < CELL_SIZE:
                                creatures.remove(c)
                elif creatures:
                    selected_creature = min(creatures, key=lambda c: math.hypot(pos[0]-c.x, pos[1]-c.y), default=None)

        # --- Lógica de Update ---
        if not is_paused:
            for _ in range(simulation_speed):
                time_info = manage_environment(time_info, foods, world, assets)
                generation_timer += 1
                
                herbivores = [c for c in creatures if isinstance(c, Herbivore)]
                carnivores = [c for c in creatures if isinstance(c, Carnivore)]
                new_creatures = []
                
                for h in herbivores: h.update(foods, carnivores, herbivores, time_info)
                for c in carnivores: c.update(herbivores, carnivores, time_info)

                # --- Interações ---
                for h in herbivores[:]:
                    # Comer
                    for f in foods[:]:
                        if math.hypot(h.x - f.x, h.y - f.y) < CELL_SIZE:
                            h.energy = min(h.energy + f.energy, 1200)
                            foods.remove(f)
                            h.genome.fitness += 5
                            break
                    # Reprodução
                    if h.reproduction_urge > 1.0:
                        for partner in herbivores:
                            if h != partner and partner.reproduction_urge > 1.0 and math.hypot(h.x - partner.x, h.y - partner.y) < CELL_SIZE:
                                new_creatures.append(h.reproduce(partner, config))
                                h.genome.fitness += 20
                                partner.genome.fitness += 20
                                break
                
                for c in carnivores[:]:
                    # Caçar
                    for h in herbivores[:]:
                        if math.hypot(c.x - h.x, c.y - h.y) < CELL_SIZE:
                            c.energy = min(c.energy + 500, 1500)
                            creatures.remove(h)
                            c.genome.fitness += 25
                            break
                
                creatures.extend(new_creatures)
                for c in creatures: c.genome.fitness = c.age
                creatures = [c for c in creatures if not c.is_dead()]

                # --- Evolução NEAT Contínua ---
                if generation_timer > SEASON_LENGTH * 2: # Evoluir a cada 2 estações
                    print("\n--- A AVALIAR GERAÇÃO E A EVOLUIR CÉREBROS ---")
                    p.run(lambda genomes, cfg: [setattr(g, 'fitness', c.genome.fitness) for c_id, c in enumerate(creatures) for g_id, g in genomes if c.genome.key == g_id], 1)
                    
                    # Substituir cérebros antigos por novos, mantendo a população
                    genomes = list(p.population.values())
                    for c in creatures:
                        c.genome = random.choice(genomes)
                        c.net = neat.nn.FeedForwardNetwork.create(c.genome, config)
                    generation_timer = 0


        # --- Desenho ---
        draw_world(screen, world, assets['terrain'])
        draw_time_overlay(screen, time_info['world_time'])
        
        for f in foods: f.draw(screen)
        for c in creatures: c.draw(screen, c == selected_creature)
        
        creature_counts = {'herbivores': len([c for c in creatures if isinstance(c, Herbivore)]),
                           'carnivores': len([c for c in creatures if isinstance(c, Carnivore)])}
        
        draw_main_ui(screen, time_info, creature_counts, simulation_speed)
        draw_inspector_panel(screen, selected_creature)
        draw_god_mode_ui(screen, current_tool)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
