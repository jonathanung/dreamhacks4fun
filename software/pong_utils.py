# pong_utils.py - Utility functions and constants for Pong game
import pygame
import math

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLORS = [
    (255, 50, 50),   # Red - Player 1 (Top)
    (50, 255, 50),   # Green - Player 2 (Right)
    (50, 50, 255),   # Blue - Player 3 (Bottom)
    (255, 255, 50),  # Yellow - Player 4 (Left)
]
WALL_COLOR = (100, 100, 100)

# Game settings - will be calculated based on screen size
GAME_MARGIN_PERCENT = 0.06  # 6% of screen size
PADDLE_WIDTH_PERCENT = 0.12  # 12% of game area width
PADDLE_HEIGHT_PERCENT = 0.02  # 2% of game area height
BALL_RADIUS_PERCENT = 0.015  # 1.5% of game area width
PADDLE_SPEED_PERCENT = 0.01  # 1% of game area width
PADDLE_HIT_DISTANCE_PERCENT = 0.03  # 3% of game area width

# Fixed settings
PLAYER_STARTING_LIVES = 3
BALL_RESET_DURATION = 60
BALL_SPEED_INCREMENT = 0.2
BALL_MAX_SPEED = 15
COUNTDOWN_DURATION = 5
FEVER_DURATION = 10
FEVER_ORB_MIN_SPAWN_TIME = 10
FEVER_ORB_MAX_SPAWN_TIME = 30
PADDLE_HIT_DURATION = 10  # Duration of paddle hit animation in frames

def calculate_game_dimensions(screen_width, screen_height):
    """Calculate game dimensions based on screen size"""
    # Calculate margin size
    margin = int(min(screen_width, screen_height) * GAME_MARGIN_PERCENT)
    
    # Calculate game area size
    game_size = min(screen_width, screen_height) - (2 * margin)
    
    # Calculate paddle dimensions
    paddle_width = int(game_size * PADDLE_WIDTH_PERCENT)
    paddle_height = int(game_size * PADDLE_HEIGHT_PERCENT)
    
    # Calculate ball radius
    ball_radius = int(game_size * BALL_RADIUS_PERCENT)
    
    # Calculate speeds
    paddle_speed = int(game_size * PADDLE_SPEED_PERCENT)
    ball_speed = paddle_speed * 0.7  # Ball slightly slower than paddle
    
    # Calculate hit distance
    paddle_hit_distance = int(game_size * PADDLE_HIT_DISTANCE_PERCENT)
    
    # Calculate fever orb size
    fever_orb_radius = ball_radius * 2
    
    return {
        'margin': margin,
        'game_size': game_size,
        'paddle_width': paddle_width,
        'paddle_height': paddle_height,
        'ball_radius': ball_radius,
        'paddle_speed': paddle_speed,
        'ball_speed': ball_speed,
        'paddle_hit_distance': paddle_hit_distance,
        'fever_orb_radius': fever_orb_radius
    }

def get_square_game_rect(screen_width, screen_height):
    """
    Calculate a square game area centered on the screen.
    This ensures the game is fair with equal distances on all sides.
    """
    # Get dimensions based on screen size
    dims = calculate_game_dimensions(screen_width, screen_height)
    margin = dims['margin']
    game_size = dims['game_size']
    
    # Calculate centered position
    left = (screen_width - game_size) // 2
    top = (screen_height - game_size) // 2
    
    return pygame.Rect(left, top, game_size, game_size)

def create_paddles(screen_width, screen_height):
    """Create all four paddles for the game in a square layout"""
    # Get dimensions based on screen size
    dims = calculate_game_dimensions(screen_width, screen_height)
    game_rect = get_square_game_rect(screen_width, screen_height)
    
    paddle_width = dims['paddle_width']
    paddle_height = dims['paddle_height']
    paddle_hit_distance = dims['paddle_hit_distance']
    
    # Calculate paddle positions based on the square
    center_x = game_rect.centerx
    center_y = game_rect.centery
    
    from pong_paddle import Paddle
    
    paddles = [
        # Top paddle (horizontal)
        Paddle(center_x - paddle_width//2, game_rect.top + paddle_height, 
              paddle_width, paddle_height, 0, paddle_hit_distance),
        
        # Right paddle (vertical)
        Paddle(game_rect.right - paddle_height*2, center_y - paddle_width//2, 
              paddle_width, paddle_height, 1, paddle_hit_distance),
        
        # Bottom paddle (horizontal)
        Paddle(center_x - paddle_width//2, game_rect.bottom - paddle_height*2, 
              paddle_width, paddle_height, 2, paddle_hit_distance),
        
        # Left paddle (vertical)
        Paddle(game_rect.left + paddle_height, center_y - paddle_width//2, 
              paddle_width, paddle_height, 3, paddle_hit_distance),
    ]
    
    return paddles

def handle_player_input(paddles, players_alive, keys, game_started, paddle_speed=None):
    """Handle keyboard input for player movement"""
    # Define the game rectangle for boundary checking
    screen_width, screen_height = pygame.display.get_surface().get_size()
    game_rect = get_square_game_rect(screen_width, screen_height)
    
    # Use calculated paddle speed if not provided
    if paddle_speed is None:
        dims = calculate_game_dimensions(screen_width, screen_height)
        paddle_speed = dims['paddle_speed']
    
    # Player 1 (Top) controls - W/A/S/D
    if players_alive[0]:
        if keys[pygame.K_a]:
            paddles[0].move("left", paddle_speed, game_rect)
        if keys[pygame.K_d]:
            paddles[0].move("right", paddle_speed, game_rect)
        if keys[pygame.K_s] and game_started and paddles[0].hit_timer == 0:
            paddles[0].hit()
    
    # Player 2 (Right) controls - Arrow keys
    if players_alive[1]:
        if keys[pygame.K_UP]:
            paddles[1].move("up", paddle_speed, game_rect)
        if keys[pygame.K_DOWN]:
            paddles[1].move("down", paddle_speed, game_rect)
        if keys[pygame.K_LEFT] and game_started and paddles[1].hit_timer == 0:
            paddles[1].hit()
    
    # Player 3 (Bottom) controls - I/J/K/L
    if players_alive[2]:
        if keys[pygame.K_j]:
            paddles[2].move("left", paddle_speed, game_rect)
        if keys[pygame.K_l]:
            paddles[2].move("right", paddle_speed, game_rect)
        if keys[pygame.K_i] and game_started and paddles[2].hit_timer == 0:
            paddles[2].hit()
    
    # Player 4 (Left) controls - Numpad
    if players_alive[3]:
        if keys[pygame.K_KP8]:
            paddles[3].move("up", paddle_speed, game_rect)
        if keys[pygame.K_KP5]:
            paddles[3].move("down", paddle_speed, game_rect)
        if keys[pygame.K_KP6] and game_started and paddles[3].hit_timer == 0:
            paddles[3].hit()

def handle_external_events(paddles, players_alive, external_events, game_started, paddle_speed=None):
    """Handle external events for player movement"""
    # Define the game rectangle for boundary checking
    screen_width, screen_height = pygame.display.get_surface().get_size()
    game_rect = get_square_game_rect(screen_width, screen_height)
    
    # Use calculated paddle speed if not provided
    if paddle_speed is None:
        dims = calculate_game_dimensions(screen_width, screen_height)
        paddle_speed = dims['paddle_speed']
    
    for event in external_events:
        action = event.get('action')
        player = event.get('player', 0)  # Default to player 1
        
        if 0 <= player < 4 and players_alive[player]:
            if action == 'left' or action == 'up':
                if player == 0 or player == 2:  # Top/Bottom players
                    paddles[player].move("left", paddle_speed, game_rect)
                else:  # Left/Right players
                    paddles[player].move("up", paddle_speed, game_rect)
            elif action == 'right' or action == 'down':
                if player == 0 or player == 2:  # Top/Bottom players
                    paddles[player].move("right", paddle_speed, game_rect)
                else:  # Left/Right players
                    paddles[player].move("down", paddle_speed, game_rect)
            elif action == 'hit' and game_started and paddles[player].hit_timer == 0:
                paddles[player].hit()

def draw_walls(screen, players_alive, game_rect):
    """Draw walls for eliminated players"""
    if not players_alive[0]:  # Top wall
        pygame.draw.rect(screen, WALL_COLOR, 
                       (game_rect.left, game_rect.top, game_rect.width, 10))
    if not players_alive[1]:  # Right wall
        pygame.draw.rect(screen, WALL_COLOR, 
                       (game_rect.right - 10, game_rect.top, 10, game_rect.height))
    if not players_alive[2]:  # Bottom wall
        pygame.draw.rect(screen, WALL_COLOR, 
                       (game_rect.left, game_rect.bottom - 10, game_rect.width, 10))
    if not players_alive[3]:  # Left wall
        pygame.draw.rect(screen, WALL_COLOR, 
                       (game_rect.left, game_rect.top, 10, game_rect.height))

def draw_player_status(screen, players_alive, font, screen_width, screen_height):
    """Draw player status indicators"""
    for i, alive in enumerate(players_alive):
        status = "Alive" if alive else "Dead"
        color = PLAYER_COLORS[i] if alive else WALL_COLOR
        text = font.render(f"Player {i+1}: {status}", True, color)
        
        if i == 0:  # Top
            screen.blit(text, (10, 10))
        elif i == 1:  # Right
            screen.blit(text, (screen_width - text.get_width() - 10, 10))
        elif i == 2:  # Bottom
            screen.blit(text, (10, screen_height - text.get_height() - 10))
        elif i == 3:  # Left
            screen.blit(text, (screen_width - text.get_width() - 10, 
                             screen_height - text.get_height() - 10))

def draw_countdown(screen, current_time, countdown_start, font, large_font, screen_width, screen_height):
    """Draw countdown before game starts"""
    center_x, center_y = screen_width // 2, screen_height // 2
    
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
    screen.blit(overlay, (0, 0))
    
    # Calculate remaining time
    remaining = COUNTDOWN_DURATION - (current_time - countdown_start)
    if remaining <= 0:
        countdown_text = "GO!"
    else:
        countdown_text = str(int(remaining) + 1)
    
    # Draw countdown text
    text_surface = large_font.render(countdown_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    screen.blit(text_surface, text_rect)
    
    # Draw "Get Ready" text
    ready_text = font.render("Get Ready!", True, WHITE)
    ready_rect = ready_text.get_rect(center=(center_x, center_y - 80))
    screen.blit(ready_text, ready_rect)
    
    # Draw player controls
    controls = [
        "Player 1 (Top): A/D to move, S to hit",
        "Player 2 (Right): Up/Down to move, Left to hit",
        "Player 3 (Bottom): J/L to move, I to hit",
        "Player 4 (Left): Numpad 8/5 to move, 6 to hit"
    ]
    
    for i, control in enumerate(controls):
        if i < len(PLAYER_COLORS) and i < 4:
            # Only show controls for active players
            control_text = font.render(control, True, PLAYER_COLORS[i])
            control_rect = control_text.get_rect(center=(center_x, center_y + 80 + i * 30))
            screen.blit(control_text, control_rect)

def get_player_color(player_index):
    """Get a player's color by index, with bounds checking"""
    if 0 <= player_index < len(PLAYER_COLORS):
        return PLAYER_COLORS[player_index]
    return (200, 200, 200)  # Default gray for invalid indices

def draw_player_status_with_lives(screen, players_alive, player_lives, font, screen_width, screen_height):
    """Draw player status indicators with remaining lives"""
    for i, alive in enumerate(players_alive):
        if alive:
            status = f"Lives: {player_lives[i]}"
            color = PLAYER_COLORS[i]
        else:
            status = "ELIMINATED"
            color = WALL_COLOR
        
        text = font.render(f"Player {i+1}: {status}", True, color)
        
        if i == 0:  # Top
            screen.blit(text, (10, 10))
        elif i == 1:  # Right
            screen.blit(text, (screen_width - text.get_width() - 10, 10))
        elif i == 2:  # Bottom
            screen.blit(text, (10, screen_height - text.get_height() - 10))
        elif i == 3:  # Left
            screen.blit(text, (screen_width - text.get_width() - 10, 
                             screen_height - text.get_height() - 10))

def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB"""
    if s == 0.0:
        return (v, v, v)
    
    i = int(h * 6)
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    
    i %= 6
    if i == 0:
        return (int(v * 255), int(t * 255), int(p * 255))
    elif i == 1:
        return (int(q * 255), int(v * 255), int(p * 255))
    elif i == 2:
        return (int(p * 255), int(v * 255), int(t * 255))
    elif i == 3:
        return (int(p * 255), int(q * 255), int(v * 255))
    elif i == 4:
        return (int(t * 255), int(p * 255), int(v * 255))
    elif i == 5:
        return (int(v * 255), int(p * 255), int(q * 255))