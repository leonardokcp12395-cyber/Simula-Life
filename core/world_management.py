import noise
import random
from settings import GRID_WIDTH, GRID_HEIGHT, SCALE, OCTAVES, PERSISTENCE, LACUNARITY, TERRAINS, DAY_LENGTH, SEASON_LENGTH
from entities.food import Food

def generate_world(seed):
    """
    Generates a procedural world map using Perlin noise.
    The world is a 2D grid where each cell is a dictionary containing terrain info.
    """
    world_map = [[{} for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Generate a noise value using Perlin noise
            noise_val = noise.pnoise2(x / SCALE,
                                      y / SCALE,
                                      octaves=OCTAVES,
                                      persistence=PERSISTENCE,
                                      lacunarity=LACUNARITY,
                                      repeatx=GRID_WIDTH,
                                      repeaty=GRID_HEIGHT,
                                      base=seed)

            # Map noise value to terrain type
            terrain_type = "DEEP_WATER" # Default
            if noise_val > -0.5:
                terrain_type = "SHALLOW_WATER"
            if noise_val > -0.3:
                terrain_type = "BEACH"
            if noise_val > -0.2:
                terrain_type = "GRASSLAND"
            if noise_val > 0.25:
                terrain_type = "FOREST"
            if noise_val > 0.6:
                terrain_type = "MOUNTAIN"
            if noise_val > 0.75:
                terrain_type = "SNOW"

            world_map[x][y] = {
                "type": terrain_type,
                "properties": TERRAINS[terrain_type]
            }

    return world_map

def manage_environment(time_info, foods, world, assets):
    """
    Manages the simulation's time, seasons, and dynamic events like food spawning.
    """
    # 1. Update Time and Seasons
    time_info['world_time'] = (time_info['world_time'] + 1) % DAY_LENGTH
    time_info['season_timer'] += 1

    seasons = ["Primavera", "Verão", "Outono", "Inverno"]
    if time_info['season_timer'] > SEASON_LENGTH:
        time_info['season_timer'] = 0
        current_season_index = seasons.index(time_info['current_season'])
        time_info['current_season'] = seasons[(current_season_index + 1) % 4]

    # 2. Spawn Food based on Season
    season = time_info['current_season']
    if season == "Primavera":
        spawn_chance = 0.03
    elif season == "Verão":
        spawn_chance = 0.05
    elif season == "Outono":
        spawn_chance = 0.015
    else: # Inverno
        spawn_chance = 0.005

    if random.random() < spawn_chance:
        # Find a valid location to spawn food (not in water or on mountains)
        valid_spawns = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                terrain_type = world[x][y]['type']
                if terrain_type in ["GRASSLAND", "FOREST", "BEACH"]:
                    valid_spawns.append((x * 16 + 8, y * 16 + 8)) # Spawn in center of cell

        if valid_spawns:
            pos = random.choice(valid_spawns)
            foods.append(Food(world, assets, pos))

    return time_info
