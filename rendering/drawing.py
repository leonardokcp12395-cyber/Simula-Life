import pygame
import math
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, FONT_SMALL, FONT_MEDIUM,
                      DAY_LENGTH, SEASON_LENGTH)
from entities.creature import Creature # Import Creature for type hinting and access

def draw_creature(screen, creature: Creature, is_selected: bool):
    """Draws a single creature procedurally with unique DNA and animations."""

    # --- 1. Setup and DNA unpacking ---
    dna = creature.visual_dna
    body_size = dna['body_size_mod']
    pattern = dna['pattern_type']
    pattern_color = dna['pattern_color']

    # Create a temporary surface for the creature sprite to handle rotation
    sprite_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
    center = CELL_SIZE # Center of the larger surface

    # --- 2. Animation Logic ---
    is_moving = creature.state == 'exploring' or creature.state == 'going_to_sleep'
    creature.animation_timer += 1

    # Walk animation
    leg_angle = 0
    if is_moving:
        leg_angle = math.sin(creature.animation_timer * 0.5) * 30 # Swing angle of 30 degrees

    # --- 3. Draw Body Parts ---
    # Legs (drawn first to be behind the body)
    leg_length = 6 * body_size
    leg_pos1 = (center + math.cos(math.radians(225)) * leg_length, center + math.sin(math.radians(225)) * leg_length)
    leg_pos2 = (center + math.cos(math.radians(315)) * leg_length, center + math.sin(math.radians(315)) * leg_length)
    pygame.draw.line(sprite_surface, creature.tribe_color, (center, center), leg_pos1, 2)
    pygame.draw.line(sprite_surface, creature.tribe_color, (center, center), leg_pos2, 2)

    # Body
    body_width = 6 * body_size
    body_height = 10 * body_size
    body_rect = pygame.Rect(center - body_width/2, center - body_height/3, body_width, body_height)
    pygame.draw.ellipse(sprite_surface, creature.tribe_color, body_rect)

    # Head
    head_radius = 3 * body_size
    head_pos = (center, center - body_height/2)
    pygame.draw.circle(sprite_surface, tuple(min(255, c+30) for c in creature.tribe_color), head_pos, head_radius)

    # --- 4. Draw Patterns ---
    if pattern == 'spots':
        for i in range(3):
            spot_x = center + (i-1) * (body_width/3)
            spot_y = center
            pygame.draw.circle(sprite_surface, pattern_color, (spot_x, spot_y), 1)
    elif pattern == 'stripes':
        for i in range(3):
            y_pos = center - body_height/4 + (i * body_height/6)
            pygame.draw.line(sprite_surface, pattern_color, (center - body_width/3, y_pos), (center + body_width/3, y_pos), 1)

    # --- 5. Rotation and Blitting ---
    rotated_sprite = pygame.transform.rotate(sprite_surface, -math.degrees(creature.angle) + 90)
    rect = rotated_sprite.get_rect(center=(int(creature.x), int(creature.y)))

    # Draw shadow and final sprite
    shadow_rect = creature.assets['shadow'].get_rect(center=(int(creature.x+2), int(creature.y+2)))
    screen.blit(creature.assets['shadow'], shadow_rect)
    screen.blit(rotated_sprite, rect)

    # --- 6. Draw UI selection details ---
    if is_selected:
        pygame.draw.circle(screen, creature.tribe_color, (int(creature.x), int(creature.y)), creature.vision_radius, 1)
        pygame.draw.line(screen, (255, 255, 255, 100), (creature.x, creature.y), (creature.nest_x, creature.nest_y), 1)
        if creature.target:
            target_x = creature.target.x if hasattr(creature.target, 'x') else creature.target['x']
            target_y = creature.target.y if hasattr(creature.target, 'y') else creature.target['y']
            pygame.draw.line(screen, (255, 0, 0, 150), (creature.x, creature.y), (target_x, target_y), 2)


# --- (Other drawing functions remain the same) ---
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
    if 0.25 < time_of_day_norm < 0.75:
        mid_point = 0.5
        dist_from_mid = abs(time_of_day_norm - mid_point)
        alpha_norm = 1 - (dist_from_mid / 0.25)
        alpha = int(math.sin(alpha_norm * math.pi) * 120)
    if alpha > 0:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, alpha))
        screen.blit(overlay, (0, 0))

def draw_main_ui(screen, time_info, creature_counts, simulation_speed):
    """Draws the main UI panel at the top of the screen."""
    ui_panel = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
    ui_panel.fill((20, 20, 40, 180))
    screen.blit(ui_panel, (0, 0))
    total_days = time_info['season_timer'] // DAY_LENGTH
    hour = int((time_info['world_time'] / DAY_LENGTH) * 24)
    time_text = FONT_MEDIUM.render(f"Season: {time_info['current_season']} | Day: {total_days} | {hour:02d}:00", True, (255, 255, 255))
    speed_text = FONT_MEDIUM.render(f"Speed: {simulation_speed}x", True, (200, 200, 255))
    screen.blit(time_text, (10, 10))
    screen.blit(speed_text, (SCREEN_WIDTH - 120, 10))
    x_offset = 450
    for name, count in creature_counts.items():
        text = FONT_MEDIUM.render(f"{name}: {count}", True, (200, 200, 200))
        screen.blit(text, (x_offset, 10))
        x_offset += text.get_width() + 20

def draw_inspector_panel(screen, creature):
    """Draws the inspector panel for a selected creature."""
    if not creature: return
    panel_width, panel_height = 240, 200
    panel_x, panel_y = SCREEN_WIDTH - panel_width - 10, 50
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 20, 40, 220))
    title = FONT_MEDIUM.render(f"{creature.name} (Tribe {creature.tribe_id})", True, creature.tribe_color)
    panel.blit(title, (10, 10))
    energy_text = FONT_SMALL.render(f"Energy: {int(creature.energy)}", True, (255, 255, 255))
    age_text = FONT_SMALL.render(f"Age: {creature.age // 100}", True, (255, 255, 255))
    panel.blit(energy_text, (15, 45)); panel.blit(age_text, (15, 65))
    screen.blit(panel, (panel_x, panel_y))

def draw_god_mode_ui(screen, current_tool):
    """Draws the UI for the current God Mode tool."""
    if not current_tool: return
    tool_text_map = {
        "spawn_herbivore": "Tool: Spawn Herbivore (H)", "spawn_carnivore": "Tool: Spawn Carnivore (C)",
        "spawn_human": "Tool: Spawn Human (J)", "spawn_feline": "Tool: Spawn Feline (K)",
        "smite": "Tool: Smite (X)", "spawn_food": "Tool: Spawn Food (F)"
    }
    text = FONT_MEDIUM.render(tool_text_map.get(current_tool, "Tool: Unknown"), True, (255, 220, 100))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
    bg_rect = text_rect.inflate(20, 10)
    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surface.fill((20, 20, 40, 180))
    screen.blit(bg_surface, bg_rect); screen.blit(text, text_rect)

def draw_statistics_panel(screen, history):
    """Draws a panel with a line graph of population history."""
    if not history: return
    panel_width, panel_height = 400, 250
    panel_x, panel_y = 10, SCREEN_HEIGHT - panel_height - 10
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((20, 20, 40, 220))
    title = FONT_MEDIUM.render("Population Over Time", True, (255, 255, 255))
    panel.blit(title, (10, 5))
    graph_rect = pygame.Rect(40, 40, panel_width - 50, panel_height - 50)
    pygame.draw.rect(panel, (10, 10, 20), graph_rect)
    max_pop = max(max(d.values()) for d in history) if history else 1
    if max_pop == 0: max_pop = 1
    archetype_names = list(history[0].keys()) if history else []
    colors = [(100, 255, 100), (255, 100, 100), (100, 100, 255), (255, 255, 100)]
    for j, name in enumerate(archetype_names):
        points = []
        for i, data in enumerate(history):
            x = graph_rect.x + (i / max(1, len(history) - 1)) * graph_rect.width
            y = graph_rect.y + graph_rect.height - (data.get(name, 0) / max_pop) * graph_rect.height
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(panel, colors[j % len(colors)], False, points, 2)
    pygame.draw.line(panel, (255, 255, 255), (graph_rect.left, graph_rect.bottom), (graph_rect.right, graph_rect.bottom), 1)
    pygame.draw.line(panel, (255, 255, 255), (graph_rect.left, graph_rect.bottom), (graph_rect.left, graph_rect.top), 1)
    y_axis_label = FONT_SMALL.render(str(max_pop), True, (255, 255, 255))
    panel.blit(y_axis_label, (graph_rect.left - 30, graph_rect.top - 5))
    x_axis_label = FONT_SMALL.render(f"{len(history)} days", True, (255, 255, 255))
    panel.blit(x_axis_label, (graph_rect.right - 40, graph_rect.bottom + 5))
    screen.blit(panel, (panel_x, panel_y))
