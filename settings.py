import pygame

# --- Configurações da Janela e Grade ---
SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE = 1280, 720, 16
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE

# --- Parâmetros do Mundo e Terrenos ---
SCALE, OCTAVES, PERSISTENCE, LACUNARITY = 80.0, 6, 0.5, 2.0
TERRAINS = {
    "DEEP_WATER": {"color": (4, 43, 99), "movement_cost": 10.0, "energy_cost": 2.0},
    "SHALLOW_WATER": {"color": (36, 114, 184), "movement_cost": 4.0, "energy_cost": 1.5},
    "BEACH": {"color": (237, 201, 175), "movement_cost": 1.5, "energy_cost": 1.0},
    "GRASSLAND": {"color": (116, 184, 69), "movement_cost": 1.0, "energy_cost": 1.0},
    "FOREST": {"color": (57, 120, 52), "movement_cost": 2.5, "energy_cost": 1.0},
    "MOUNTAIN": {"color": (130, 130, 130), "movement_cost": 5.0, "energy_cost": 1.2},
    "SNOW": {"color": (255, 255, 255), "movement_cost": 6.0, "energy_cost": 1.5}
}

# --- Parâmetros de Tempo e Estação ---
DAY_LENGTH = 2400
SEASON_LENGTH = 4 * DAY_LENGTH

# --- Fontes ---
pygame.font.init()
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)

# --- Configurações das Tribos ---
NUMBER_OF_TRIBES_PER_SPECIES = 3
TRIBE_COLORS = [
    (255, 0, 0),    # Vermelho
    (0, 255, 0),    # Verde
    (255, 255, 0),  # Amarelo
    (0, 255, 255),  # Ciano
    (255, 0, 255),  # Magenta
]