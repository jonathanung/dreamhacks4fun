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

# Game settings
GAME_MARGIN = 50
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
PADDLE_HIT_DURATION = 10  # frames
PADDLE_HIT_DISTANCE = 20  # pixels
BALL_RADIUS = 10
BALL_SPEED = 5
COUNTDOWN_DURATION = 5  # seconds

def create_paddles(screen_width, screen_height):
    """Create all four paddles for the game"""
    center_x = screen_width // 2
    center_y = screen_height // 2
    game_width = screen_width - (2 * GAME_MARGIN)
    game_height = screen_height - (2 * GAME_MARGIN)
    
    from pong_paddle import Paddle
    
    paddles = [
        # Top paddle (horizontal)
        Paddle(center_x - PADDLE_WIDTH//2, GAME_MARGIN + 10, 
              PADDLE_WIDTH, PADDLE_HEIGHT, 0),
        
        # Right paddle (vertical)
        Paddle(GAME_MARGIN + game_width - PADDLE_HEIGHT - 10, 
              center_y - PADDLE_WIDTH//2, PADDLE_WIDTH, PADDLE_HEIGHT, 1),
        
        # Bottom paddle (horizontal)
        Paddle(center_x - PADDLE_WIDTH//2, 
              GAME_MARGIN + game_height - PADDLE_HEIGHT - 10, 
              PADDLE_WIDTH, PADDLE_HEIGHT, 2),
        
        # Left paddle (vertical)
        Paddle(GAME_MARGIN + 10, center_y - PADDLE_WIDTH//2, 
              PADDLE_WIDTH, PADDLE_HEIGHT, 3),
    ]
    
    return paddles

def handle_player_input(paddles, players_alive, keys, game_started):
    """Handle keyboard input for player movement"""
    # Define the game rectangle for boundary checking
    screen_width, screen_height = pygame.display.get_surface().get_size()
    game_rect = pygame.Rect(GAME_MARGIN, GAME_MARGIN, 
                          screen_width - (2 * GAME_MARGIN), 
                          screen_height - (2 * GAME_MARGIN))
    
    # Player 1 (Top) controls - W/A/S/D
    if players_alive[0]:
        if keys[pygame.K_a]:
            paddles[0].move("left", PADDLE_SPEED, game_rect)
        if keys[pygame.K_d]:
            paddles[0].move("right", PADDLE_SPEED, game_rect)
        if keys[pygame.K_s] and game_started and paddles[0].hit_timer == 0:
            paddles[0].hit()
    
    # Player 2 (Right) controls - Arrow keys
    if players_alive[1]:
        if keys[pygame.K_UP]:
            paddles[1].move("up", PADDLE_SPEED, game_rect)
        if keys[pygame.K_DOWN]:
            paddles[1].move("down", PADDLE_SPEED, game_rect)
        if keys[pygame.K_LEFT] and game_started and paddles[1].hit_timer == 0:
            paddles[1].hit()
    
    # Player 3 (Bottom) controls - I/J/K/L
    if players_alive[2]:
        if keys[pygame.K_j]:
            paddles[2].move("left", PADDLE_SPEED, game_rect)
        if keys[pygame.K_l]:
            paddles[2].move("right", PADDLE_SPEED, game_rect)
        if keys[pygame.K_i] and game_started and paddles[2].hit_timer == 0:
            paddles[2].hit()
    
    # Player 4 (Left) controls - Numpad
    if players_alive[3]:
        if keys[pygame.K_KP8]:
            paddles[3].move("up", PADDLE_SPEED, game_rect)
        if keys[pygame.K_KP5]:
            paddles[3].move("down", PADDLE_SPEED, game_rect)
        if keys[pygame.K_KP6] and game_started and paddles[3].hit_timer == 0:
            paddles[3].hit()

def handle_external_events(paddles, players_alive, external_events, game_started):
    """Handle external events for player movement"""
    # Define the game rectangle for boundary checking
    screen_width, screen_height = pygame.display.get_surface().get_size()
    game_rect = pygame.Rect(GAME_MARGIN, GAME_MARGIN, 
                          screen_width - (2 * GAME_MARGIN), 
                          screen_height - (2 * GAME_MARGIN))
    
    for event in external_events:
        action = event.get('action')
        player = event.get('player', 0)  # Default to player 1
        
        if 0 <= player < 4 and players_alive[player]:
            if action == 'left' or action == 'up':
                if player == 0 or player == 2:  # Top/Bottom players
                    paddles[player].move("left", PADDLE_SPEED, game_rect)
                else:  # Left/Right players
                    paddles[player].move("up", PADDLE_SPEED, game_rect)
            elif action == 'right' or action == 'down':
                if player == 0 or player == 2:  # Top/Bottom players
                    paddles[player].move("right", PADDLE_SPEED, game_rect)
                else:  # Left/Right players
                    paddles[player].move("down", PADDLE_SPEED, game_rect)
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