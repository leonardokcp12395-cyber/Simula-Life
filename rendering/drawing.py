import pygame
import math
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, FONT_SMALL, FONT_MEDIUM,
                      DAY_LENGTH, SEASON_LENGTH)

def draw_world(screen, world_data, terrain_assets):
    """Draws the world terrain onto the screen."""
    for x in range(len(world_data)):
        for y in range(len(world_data[x])):
            terrain_type = world_data[x][y]['type']
            asset = terrain_assets[terrain_type]
            screen.blit(asset, (x * CELL_SIZE, y * CELL_SIZE))

def draw_time_overlay(screen, world_time):
    """Draws a transparent overlay to simulate day and night."""
    time_of_day_norm = world_time / DAY_LENGTH

    alpha = 0
    if 0.25 < time_of_day_norm < 0.75: # Night time
        # Use a sine wave for smooth transition in and out of night
        mid_point = 0.5
        dist_from_mid = abs(time_of_day_norm - mid_point)
        # Scale the 0.25 distance to pi (for a half sine wave)
        alpha_norm = 1 - (dist_from_mid / 0.25)
        alpha = int(math.sin(alpha_norm * math.pi) * 120) # Max alpha of 120

    if alpha > 0:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, alpha))
        screen.blit(overlay, (0, 0))

def draw_main_ui(screen, time_info, creature_counts, simulation_speed):
    """Draws the main UI panel at the top of the screen."""
    # Draw a semi-transparent background for the UI
    ui_panel = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
    ui_panel.fill((20, 20, 40, 180))
    screen.blit(ui_panel, (0, 0))

    # Calculate time
    total_days = time_info['season_timer'] // DAY_LENGTH
    hour = int((time_info['world_time'] / DAY_LENGTH) * 24)

    # Prepare text
    time_text = FONT_MEDIUM.render(f"Season: {time_info['current_season']} | Day: {total_days} | {hour:02d}:00", True, (255, 255, 255))
    herb_text = FONT_MEDIUM.render(f"Herbivores: {creature_counts['herbivores']}", True, (100, 255, 100))
    carn_text = FONT_MEDIUM.render(f"Carnivores: {creature_counts['carnivores']}", True, (255, 100, 100))
    speed_text = FONT_MEDIUM.render(f"Speed: {simulation_speed}x", True, (200, 200, 255))

    # Blit text
    screen.blit(time_text, (10, 10))
    screen.blit(herb_text, (450, 10))
    screen.blit(carn_text, (650, 10))
    screen.blit(speed_text, (SCREEN_WIDTH - 120, 10))

def draw_inspector_panel(screen, creature):
    """Draws the inspector panel for a selected creature."""
    if not creature:
        return

    panel_width, panel_height = 240, 200
    panel_x, panel_y = SCREEN_WIDTH - panel_width - 10, 50

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 20, 40, 220))

    # Title
    title = FONT_MEDIUM.render(f"{creature.__class__.__name__} (Tribe {creature.tribe_id})", True, creature.tribe_color)
    panel.blit(title, (10, 10))

    # Stats
    energy_text = FONT_SMALL.render(f"Energy: {int(creature.energy)}", True, (255, 255, 255))
    age_text = FONT_SMALL.render(f"Age: {creature.age // 100}", True, (255, 255, 255))
    speed_text = FONT_SMALL.render(f"Max Speed: {creature.max_speed:.2f}", True, (255, 255, 255))
    vision_text = FONT_SMALL.render(f"Vision: {creature.vision_radius}", True, (255, 255, 255))
    night_vision_text = FONT_SMALL.render(f"Night Vision: {'Yes' if creature.night_vision_gene else 'No'}", True, (255, 255, 255))
    urge_text = FONT_SMALL.render(f"Repro Urge: {creature.reproduction_urge:.2f}", True, (255, 255, 255))

    panel.blit(energy_text, (15, 45))
    panel.blit(age_text, (15, 65))
    panel.blit(speed_text, (15, 85))
    panel.blit(vision_text, (15, 105))
    panel.blit(night_vision_text, (15, 125))
    panel.blit(urge_text, (15, 145))

    screen.blit(panel, (panel_x, panel_y))

def draw_god_mode_ui(screen, current_tool):
    """Draws the UI for the current God Mode tool."""
    if not current_tool:
        return

    tool_text_map = {
        "spawn_food": "Tool: Spawn Food (F)",
        "spawn_herbivore": "Tool: Spawn Herbivore (H)",
        "spawn_carnivore": "Tool: Spawn Carnivore (C)",
        "smite": "Tool: Smite (X)"
    }

    text = FONT_MEDIUM.render(tool_text_map.get(current_tool, "Tool: Unknown"), True, (255, 220, 100))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

    # Background for readability
    bg_rect = text_rect.inflate(20, 10)
    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surface.fill((20, 20, 40, 180))

    screen.blit(bg_surface, bg_rect)
    screen.blit(text, text_rect)

def draw_statistics_panel(screen, history):
    """Draws a panel with a line graph of population history."""
    if not history:
        return

    panel_width, panel_height = 400, 250
    panel_x, panel_y = 10, SCREEN_HEIGHT - panel_height - 10

    # Draw panel background
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 20, 40, 220))

    # Title
    title = FONT_MEDIUM.render("Population Over Time", True, (255, 255, 255))
    panel.blit(title, (10, 5))

    # Graph area
    graph_rect = pygame.Rect(40, 40, panel_width - 50, panel_height - 50)
    pygame.draw.rect(panel, (10, 10, 20), graph_rect) # Graph background

    # Find max population for y-axis scaling
    max_pop = 1
    for data in history:
        max_pop = max(max_pop, data['herbivores'], data['carnivores'])

    # Prepare data points
    herb_points = []
    carn_points = []
    for i, data in enumerate(history):
        x = graph_rect.x + (i / max(1, len(history) - 1)) * graph_rect.width

        y_herb = graph_rect.y + graph_rect.height - (data['herbivores'] / max_pop) * graph_rect.height
        herb_points.append((x, y_herb))

        y_carn = graph_rect.y + graph_rect.height - (data['carnivores'] / max_pop) * graph_rect.height
        carn_points.append((x, y_carn))

    # Draw lines
    if len(herb_points) > 1:
        pygame.draw.lines(panel, (100, 255, 100), False, herb_points, 2)
    if len(carn_points) > 1:
        pygame.draw.lines(panel, (255, 100, 100), False, carn_points, 2)

    # Draw axes and labels
    pygame.draw.line(panel, (255, 255, 255), (graph_rect.left, graph_rect.bottom), (graph_rect.right, graph_rect.bottom), 1) # X-axis
    pygame.draw.line(panel, (255, 255, 255), (graph_rect.left, graph_rect.bottom), (graph_rect.left, graph_rect.top), 1) # Y-axis
    y_axis_label = FONT_SMALL.render(str(max_pop), True, (255, 255, 255))
    panel.blit(y_axis_label, (graph_rect.left - 30, graph_rect.top - 5))
    x_axis_label = FONT_SMALL.render(f"{len(history)} days", True, (255, 255, 255))
    panel.blit(x_axis_label, (graph_rect.right - 40, graph_rect.bottom + 5))

    screen.blit(panel, (panel_x, panel_y))
