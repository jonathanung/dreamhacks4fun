# pong_ball.py - Ball class for Pong game
import pygame
import math
import random
from pong_utils import *

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        
        # Random initial direction
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
    
    def update(self):
        """Update ball position"""
        self.x += self.dx
        self.y += self.dy
    
    def check_boundaries(self, game_rect, players_alive):
        """
        Check for collisions with game boundaries and eliminate players
        Returns the index of eliminated player if applicable, or None
        """
        eliminated_player = None
        
        # Left wall
        if self.x - self.radius < game_rect.left:
            if players_alive[3]:  # Player 4 (Left)
                players_alive[3] = False
                eliminated_player = 3
            self.dx = abs(self.dx)  # Bounce right
        
        # Right wall
        if self.x + self.radius > game_rect.right:
            if players_alive[1]:  # Player 2 (Right)
                players_alive[1] = False
                eliminated_player = 1
            self.dx = -abs(self.dx)  # Bounce left
        
        # Top wall
        if self.y - self.radius < game_rect.top:
            if players_alive[0]:  # Player 1 (Top)
                players_alive[0] = False
                eliminated_player = 0
            self.dy = abs(self.dy)  # Bounce down
        
        # Bottom wall
        if self.y + self.radius > game_rect.bottom:
            if players_alive[2]:  # Player 3 (Bottom)
                players_alive[2] = False
                eliminated_player = 2
            self.dy = -abs(self.dy)  # Bounce up
        
        # Keep ball in bounds
        self.x = max(game_rect.left + self.radius, min(game_rect.right - self.radius, self.x))
        self.y = max(game_rect.top + self.radius, min(game_rect.bottom - self.radius, self.y))
        
        return eliminated_player
    
    def draw(self, screen, color):
        """Draw the ball on the screen"""
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)