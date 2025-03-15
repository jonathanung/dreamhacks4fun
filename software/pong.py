# pong.py - Main file for 4-player Pong game
import pygame
import math
import random
import time
from pong_paddle import Paddle
from pong_ball import Ball
from pong_utils import *

def run_pong(screen, player_count=4, external_events=None):
    """
    Run the Pong game with the specified number of players
    
    Args:
        screen: Pygame surface to draw on
        player_count: Number of players (1-4)
        external_events: External events from event controller
    """
    # Check for valid player count
    if player_count < 1 or player_count > 4:
        player_count = 4  # Default to 4 players
    
    # If only 1 player, show error and return to menu
    if player_count == 1:
        show_error_screen(screen, "Pong requires at least 2 players")
        return
    
    # Initialize game variables
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 100)
    
    # Screen dimensions
    WIDTH, HEIGHT = screen.get_size()
    CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
    
    # Game area
    GAME_RECT = pygame.Rect(GAME_MARGIN, GAME_MARGIN, 
                          WIDTH - (2 * GAME_MARGIN), 
                          HEIGHT - (2 * GAME_MARGIN))
    
    # Determine which players will be active based on player count
    players_alive = [True, True, True, True]  # Start with all players
    
    if player_count == 2:
        # For 2 players, place them on opposite sides (top and bottom)
        players_alive = [True, False, True, False]
    elif player_count == 3:
        # For 3 players, randomly choose which side to disable
        disabled_side = random.randint(0, 3)
        players_alive[disabled_side] = False
    
    # Initialize paddles
    paddles = create_paddles(WIDTH, HEIGHT)
    
    # Initialize ball
    ball = Ball(CENTER_X, CENTER_Y, BALL_RADIUS, BALL_SPEED)
    
    # Game state
    game_started = False
    countdown_start = time.time()
    
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
        if not game_started and current_time - countdown_start >= COUNTDOWN_DURATION:
            game_started = True
        
        # Handle player movement (keyboard and external events)
        handle_player_input(paddles, players_alive, keys, game_started)
        if external_events:
            handle_external_events(paddles, players_alive, external_events, game_started)
        
        # Update paddle hit animations
        for paddle in paddles:
            paddle.update()
        
        # Update ball position only if game has started
        if game_started:
            collision = False
            
            # Check for collisions with paddles
            for i, paddle in enumerate(paddles):
                if not players_alive[i]:
                    continue
                
                if paddle.check_collision(ball):
                    collision = True
                    break
            
            # If no collision, update ball position
            if not collision:
                ball.update()
            
            # Check for wall collisions and eliminate players
            eliminated_player = ball.check_boundaries(GAME_RECT, players_alive)
            
            # Check for game over (only one player left)
            alive_count = sum(players_alive)
            if alive_count <= 1:
                # Show winner screen
                show_winner_screen(screen, players_alive, font, WIDTH, HEIGHT)
                running = False
                continue
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw game area
        pygame.draw.rect(screen, WHITE, GAME_RECT, 2)
        
        # Draw paddles
        for i, paddle in enumerate(paddles):
            if players_alive[i]:
                paddle.draw(screen, PLAYER_COLORS[i])
        
        # Draw walls for eliminated players
        draw_walls(screen, players_alive, GAME_RECT)
        
        # Draw ball
        ball.draw(screen, WHITE)
        
        # Draw player status
        draw_player_status(screen, players_alive, font, WIDTH, HEIGHT)
        
        # Draw controls info
        controls_text = font.render("ESC: Return to Menu", True, WHITE)
        screen.blit(controls_text, (CENTER_X - controls_text.get_width()//2, 10))
        
        # Draw countdown if game hasn't started
        if not game_started:
            draw_countdown(screen, current_time, countdown_start, font, large_font, WIDTH, HEIGHT)
        
        pygame.display.flip()
        clock.tick(60)

def show_error_screen(screen, message):
    """Show error message and wait for user to press ESC"""
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 50)
    
    WIDTH, HEIGHT = screen.get_size()
    CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        screen.fill(BLACK)
        
        # Draw error message
        error_text = large_font.render(message, True, (255, 50, 50))
        error_rect = error_text.get_rect(center=(CENTER_X, CENTER_Y))
        screen.blit(error_text, error_rect)
        
        # Draw return instruction
        return_text = font.render("Press ESC to return to menu", True, WHITE)
        return_rect = return_text.get_rect(center=(CENTER_X, CENTER_Y + 70))
        screen.blit(return_text, return_rect)
        
        pygame.display.flip()

def show_winner_screen(screen, players_alive, font, WIDTH, HEIGHT):
    """Show the winner and wait for user to press ESC"""
    large_font = pygame.font.Font(None, 50)
    CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
    
    # Find the winner
    winner = -1
    for i, alive in enumerate(players_alive):
        if alive:
            winner = i
    
    # Display winner message
    screen.fill(BLACK)
    if winner >= 0:
        winner_text = f"Player {winner + 1} Wins!"
        text_surface = large_font.render(winner_text, True, PLAYER_COLORS[winner])
    else:
        text_surface = large_font.render("Draw!", True, WHITE)
    
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