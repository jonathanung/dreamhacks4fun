# minigame1.py - 4 Player Pong
import pygame
import math
import random
import time

def run_minigame1(screen, external_events=None):
    # Initialize game variables
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 100)
    
    # Screen dimensions
    WIDTH, HEIGHT = screen.get_size()
    CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
    
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
    
    # Game area
    GAME_MARGIN = 50
    GAME_WIDTH = WIDTH - (2 * GAME_MARGIN)
    GAME_HEIGHT = HEIGHT - (2 * GAME_MARGIN)
    GAME_RECT = pygame.Rect(GAME_MARGIN, GAME_MARGIN, GAME_WIDTH, GAME_HEIGHT)
    
    # Paddle settings
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 15
    PADDLE_SPEED = 8
    PADDLE_HIT_DURATION = 10  # frames
    PADDLE_HIT_DISTANCE = 20  # pixels
    
    # Ball settings
    BALL_RADIUS = 10
    BALL_SPEED = 5
    
    # Player states - [x, y, width, height, direction, hit_timer]
    # Direction: 0=top, 1=right, 2=bottom, 3=left
    players_alive = [True, True, True, True]
    paddles = [
        # Top paddle (horizontal)
        [CENTER_X - PADDLE_WIDTH//2, GAME_MARGIN + 10, PADDLE_WIDTH, PADDLE_HEIGHT, 0, 0],
        
        # Right paddle (vertical)
        [GAME_MARGIN + GAME_WIDTH - PADDLE_HEIGHT - 10, CENTER_Y - PADDLE_WIDTH//2, PADDLE_HEIGHT, PADDLE_WIDTH, 1, 0],
        
        # Bottom paddle (horizontal)
        [CENTER_X - PADDLE_WIDTH//2, GAME_MARGIN + GAME_HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT, 2, 0],
        
        # Left paddle (vertical)
        [GAME_MARGIN + 10, CENTER_Y - PADDLE_WIDTH//2, PADDLE_HEIGHT, PADDLE_WIDTH, 3, 0],
    ]
    
    # Ball state
    ball_x = CENTER_X
    ball_y = CENTER_Y
    # Random initial direction
    angle = random.uniform(0, 2 * math.pi)
    ball_dx = math.cos(angle) * BALL_SPEED
    ball_dy = math.sin(angle) * BALL_SPEED
    
    # Game state
    game_started = False
    countdown_start = time.time()
    countdown_duration = 5  # seconds
    
    # Game loop
    while running:
        current_time = time.time()
        
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Process keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        
        # Check if countdown is complete
        if not game_started and current_time - countdown_start >= countdown_duration:
            game_started = True
        
        # Player 1 (Top) controls - W/A/S/D
        if players_alive[0]:
            if keys[pygame.K_a]:
                paddles[0][0] = max(GAME_MARGIN, paddles[0][0] - PADDLE_SPEED)
            if keys[pygame.K_d]:
                paddles[0][0] = min(GAME_MARGIN + GAME_WIDTH - paddles[0][2], paddles[0][0] + PADDLE_SPEED)
            if keys[pygame.K_s] and paddles[0][5] == 0 and game_started:
                paddles[0][5] = PADDLE_HIT_DURATION
        
        # Player 2 (Right) controls - Arrow keys
        if players_alive[1]:
            if keys[pygame.K_UP]:
                paddles[1][1] = max(GAME_MARGIN, paddles[1][1] - PADDLE_SPEED)
            if keys[pygame.K_DOWN]:
                paddles[1][1] = min(GAME_MARGIN + GAME_HEIGHT - paddles[1][3], paddles[1][1] + PADDLE_SPEED)
            if keys[pygame.K_LEFT] and paddles[1][5] == 0 and game_started:
                paddles[1][5] = PADDLE_HIT_DURATION
        
        # Player 3 (Bottom) controls - I/J/K/L
        if players_alive[2]:
            if keys[pygame.K_j]:
                paddles[2][0] = max(GAME_MARGIN, paddles[2][0] - PADDLE_SPEED)
            if keys[pygame.K_l]:
                paddles[2][0] = min(GAME_MARGIN + GAME_WIDTH - paddles[2][2], paddles[2][0] + PADDLE_SPEED)
            if keys[pygame.K_i] and paddles[2][5] == 0 and game_started:
                paddles[2][5] = PADDLE_HIT_DURATION
        
        # Player 4 (Left) controls - Numpad
        if players_alive[3]:
            if keys[pygame.K_KP8]:
                paddles[3][1] = max(GAME_MARGIN, paddles[3][1] - PADDLE_SPEED)
            if keys[pygame.K_KP5]:
                paddles[3][1] = min(GAME_MARGIN + GAME_HEIGHT - paddles[3][3], paddles[3][1] + PADDLE_SPEED)
            if keys[pygame.K_KP6] and paddles[3][5] == 0 and game_started:
                paddles[3][5] = PADDLE_HIT_DURATION
        
        # Process external events
        if external_events:
            for event in external_events:
                action = event.get('action')
                player = event.get('player', 0)  # Default to player 1
                
                if 0 <= player < 4 and players_alive[player]:
                    if action == 'left' or action == 'up':
                        if player == 0 or player == 2:  # Top/Bottom players
                            paddles[player][0] = max(GAME_MARGIN, paddles[player][0] - PADDLE_SPEED)
                        else:  # Left/Right players
                            paddles[player][1] = max(GAME_MARGIN, paddles[player][1] - PADDLE_SPEED)
                    elif action == 'right' or action == 'down':
                        if player == 0 or player == 2:  # Top/Bottom players
                            paddles[player][0] = min(GAME_MARGIN + GAME_WIDTH - paddles[player][2], 
                                                    paddles[player][0] + PADDLE_SPEED)
                        else:  # Left/Right players
                            paddles[player][1] = min(GAME_MARGIN + GAME_HEIGHT - paddles[player][3], 
                                                    paddles[player][1] + PADDLE_SPEED)
                    elif action == 'hit' and paddles[player][5] == 0 and game_started:
                        paddles[player][5] = PADDLE_HIT_DURATION
        
        # Update paddle hit animations
        for i in range(4):
            if paddles[i][5] > 0:
                paddles[i][5] -= 1
        
        # Update ball position only if game has started
        if game_started:
            next_ball_x = ball_x + ball_dx
            next_ball_y = ball_y + ball_dy
            
            # Check for collisions with paddles
            collision_occurred = False
            
            for i, (x, y, width, height, direction, hit_timer) in enumerate(paddles):
                if not players_alive[i]:
                    continue
                
                # Adjust paddle position if it's hitting
                paddle_hit_offset = 0
                if hit_timer > 0:
                    paddle_hit_offset = PADDLE_HIT_DISTANCE * (hit_timer / PADDLE_HIT_DURATION)
                
                # Create paddle rect based on direction
                paddle_rect = None
                if direction == 0:  # Top - horizontal paddle
                    paddle_rect = pygame.Rect(x, y - paddle_hit_offset, width, height + paddle_hit_offset)
                elif direction == 1:  # Right - vertical paddle
                    paddle_rect = pygame.Rect(x - paddle_hit_offset, y, height + paddle_hit_offset, width)
                elif direction == 2:  # Bottom - horizontal paddle
                    paddle_rect = pygame.Rect(x, y, width, height + paddle_hit_offset)
                elif direction == 3:  # Left - vertical paddle
                    paddle_rect = pygame.Rect(x, y, height + paddle_hit_offset, width)
                
                # Expanded collision rect for better detection
                expanded_rect = paddle_rect.inflate(BALL_RADIUS*2, BALL_RADIUS*2)
                
                # Check if the ball's path intersects with the paddle
                if expanded_rect.collidepoint(next_ball_x, next_ball_y):
                    collision_occurred = True
                    
                    # Calculate bounce based on paddle direction
                    if direction == 0:  # Top paddle
                        # Horizontal position determines angle
                        relative_x = (ball_x - x) / width
                        angle = math.pi * (0.25 + 0.5 * relative_x)
                        ball_dx = math.cos(angle) * BALL_SPEED
                        ball_dy = abs(math.sin(angle) * BALL_SPEED)  # Always bounce downward
                        
                        # If paddle is hitting, add extra velocity
                        if hit_timer > 0:
                            ball_dy *= 1.5
                    
                    elif direction == 2:  # Bottom paddle
                        # Horizontal position determines angle
                        relative_x = (ball_x - x) / width
                        angle = math.pi * (0.25 + 0.5 * relative_x)
                        ball_dx = math.cos(angle) * BALL_SPEED
                        ball_dy = -abs(math.sin(angle) * BALL_SPEED)  # Always bounce upward
                        
                        # If paddle is hitting, add extra velocity
                        if hit_timer > 0:
                            ball_dy *= 1.5
                    
                    elif direction == 1:  # Right paddle
                        # Vertical position determines angle
                        relative_y = (ball_y - y) / width  # width is actually the paddle's height for vertical paddles
                        angle = math.pi * (0.75 + 0.5 * relative_y)
                        ball_dx = -abs(math.cos(angle) * BALL_SPEED)  # Always bounce leftward
                        ball_dy = math.sin(angle) * BALL_SPEED
                        
                        # If paddle is hitting, add extra velocity
                        if hit_timer > 0:
                            ball_dx *= 1.5
                    
                    elif direction == 3:  # Left paddle
                        # Vertical position determines angle
                        relative_y = (ball_y - y) / width  # width is actually the paddle's height for vertical paddles
                        angle = math.pi * (0.75 + 0.5 * relative_y)
                        ball_dx = abs(math.cos(angle) * BALL_SPEED)  # Always bounce rightward
                        ball_dy = math.sin(angle) * BALL_SPEED
                        
                        # If paddle is hitting, add extra velocity
                        if hit_timer > 0:
                            ball_dx *= 1.5
                    
                    break  # Only handle one collision per frame
            
            # If no collision with paddles, update ball position
            if not collision_occurred:
                ball_x = next_ball_x
                ball_y = next_ball_y
            else:
                # If collision occurred, move ball in new direction
                ball_x += ball_dx
                ball_y += ball_dy
            
            # Check for collisions with walls and eliminate players
            if ball_x - BALL_RADIUS < GAME_MARGIN:  # Left wall
                if players_alive[3]:
                    players_alive[3] = False
                    # Bounce off newly created wall
                    ball_dx = abs(ball_dx)
                else:
                    ball_dx = abs(ball_dx)
            
            if ball_x + BALL_RADIUS > GAME_MARGIN + GAME_WIDTH:  # Right wall
                if players_alive[1]:
                    players_alive[1] = False
                    # Bounce off newly created wall
                    ball_dx = -abs(ball_dx)
                else:
                    ball_dx = -abs(ball_dx)
            
            if ball_y - BALL_RADIUS < GAME_MARGIN:  # Top wall
                if players_alive[0]:
                    players_alive[0] = False
                    # Bounce off newly created wall
                    ball_dy = abs(ball_dy)
                else:
                    ball_dy = abs(ball_dy)
            
            if ball_y + BALL_RADIUS > GAME_MARGIN + GAME_HEIGHT:  # Bottom wall
                if players_alive[2]:
                    players_alive[2] = False
                    # Bounce off newly created wall
                    ball_dy = -abs(ball_dy)
                else:
                    ball_dy = -abs(ball_dy)
            
            # Keep ball in bounds
            ball_x = max(GAME_MARGIN + BALL_RADIUS, min(GAME_MARGIN + GAME_WIDTH - BALL_RADIUS, ball_x))
            ball_y = max(GAME_MARGIN + BALL_RADIUS, min(GAME_MARGIN + GAME_HEIGHT - BALL_RADIUS, ball_y))
            
            # Check for game over (only one player left)
            alive_count = sum(players_alive)
            if alive_count <= 1:
                # Find the winner
                winner = -1
                for i, alive in enumerate(players_alive):
                    if alive:
                        winner = i
                
                # Display winner message
                screen.fill(BLACK)
                if winner >= 0:
                    winner_text = f"Player {winner + 1} Wins!"
                    text_surface = font.render(winner_text, True, PLAYER_COLORS[winner])
                else:
                    text_surface = font.render("Draw!", True, WHITE)
                
                text_rect = text_surface.get_rect(center=(CENTER_X, CENTER_Y))
                screen.blit(text_surface, text_rect)
                
                # Display return message
                return_text = font.render("Press ESC to return to menu", True, WHITE)
                return_rect = return_text.get_rect(center=(CENTER_X, CENTER_Y + 50))
                screen.blit(return_text, return_rect)
                
                pygame.display.flip()
                
                # Wait for ESC
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
                    clock.tick(60)
                
                continue
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw game area
        pygame.draw.rect(screen, WHITE, GAME_RECT, 2)
        
        # Draw paddles
        for i, (x, y, width, height, direction, hit_timer) in enumerate(paddles):
            if not players_alive[i]:
                continue
                
            # Adjust paddle position if it's hitting
            paddle_hit_offset = 0
            if hit_timer > 0:
                paddle_hit_offset = PADDLE_HIT_DISTANCE * (hit_timer / PADDLE_HIT_DURATION)
            
            # Create paddle rect based on direction
            paddle_rect = None
            if direction == 0:  # Top - horizontal paddle
                paddle_rect = pygame.Rect(x, y - paddle_hit_offset, width, height + paddle_hit_offset)
            elif direction == 1:  # Right - vertical paddle
                # Swap width and height for vertical orientation
                paddle_rect = pygame.Rect(x - paddle_hit_offset, y, height + paddle_hit_offset, width)
            elif direction == 2:  # Bottom - horizontal paddle
                paddle_rect = pygame.Rect(x, y, width, height + paddle_hit_offset)
            elif direction == 3:  # Left - vertical paddle
                # Swap width and height for vertical orientation
                paddle_rect = pygame.Rect(x, y, height + paddle_hit_offset, width)
            
            pygame.draw.rect(screen, PLAYER_COLORS[i], paddle_rect)
        
        # Draw walls for eliminated players
        if not players_alive[0]:  # Top wall
            pygame.draw.rect(screen, WALL_COLOR, (GAME_MARGIN, GAME_MARGIN, GAME_WIDTH, 10))
        if not players_alive[1]:  # Right wall
            pygame.draw.rect(screen, WALL_COLOR, (GAME_MARGIN + GAME_WIDTH - 10, GAME_MARGIN, 10, GAME_HEIGHT))
        if not players_alive[2]:  # Bottom wall
            pygame.draw.rect(screen, WALL_COLOR, (GAME_MARGIN, GAME_MARGIN + GAME_HEIGHT - 10, GAME_WIDTH, 10))
        if not players_alive[3]:  # Left wall
            pygame.draw.rect(screen, WALL_COLOR, (GAME_MARGIN, GAME_MARGIN, 10, GAME_HEIGHT))
        
        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), BALL_RADIUS)
        
        # Draw player status
        for i, alive in enumerate(players_alive):
            status = "Alive" if alive else "Dead"
            color = PLAYER_COLORS[i] if alive else WALL_COLOR
            text = font.render(f"Player {i+1}: {status}", True, color)
            
            if i == 0:  # Top
                screen.blit(text, (10, 10))
            elif i == 1:  # Right
                screen.blit(text, (WIDTH - text.get_width() - 10, 10))
            elif i == 2:  # Bottom
                screen.blit(text, (10, HEIGHT - text.get_height() - 10))
            elif i == 3:  # Left
                screen.blit(text, (WIDTH - text.get_width() - 10, HEIGHT - text.get_height() - 10))
        
        # Draw controls info
        controls_text = font.render("ESC: Return to Menu", True, WHITE)
        screen.blit(controls_text, (CENTER_X - controls_text.get_width()//2, 10))
        
        # Draw countdown if game hasn't started
        if not game_started:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            screen.blit(overlay, (0, 0))
            
            # Calculate remaining time
            remaining = countdown_duration - (current_time - countdown_start)
            if remaining <= 0:
                countdown_text = "GO!"
            else:
                countdown_text = str(int(remaining) + 1)
            
            # Draw countdown text
            text_surface = large_font.render(countdown_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(CENTER_X, CENTER_Y))
            screen.blit(text_surface, text_rect)
            
            # Draw "Get Ready" text
            ready_text = font.render("Get Ready!", True, WHITE)
            ready_rect = ready_text.get_rect(center=(CENTER_X, CENTER_Y - 80))
            screen.blit(ready_text, ready_rect)
            
            # Draw player controls
            controls = [
                "Player 1 (Top): A/D to move, S to hit",
                "Player 2 (Right): Up/Down to move, Left to hit",
                "Player 3 (Bottom): J/L to move, I to hit",
                "Player 4 (Left): Numpad 8/5 to move, 6 to hit"
            ]
            
            for i, control in enumerate(controls):
                control_text = font.render(control, True, PLAYER_COLORS[i])
                control_rect = control_text.get_rect(center=(CENTER_X, CENTER_Y + 80 + i * 30))
                screen.blit(control_text, control_rect)
        
        pygame.display.flip()
        clock.tick(60)
