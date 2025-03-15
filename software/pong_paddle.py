# pong_paddle.py - Paddle class for Pong game
import pygame
import math
from pong_utils import *

class Paddle:
    def __init__(self, x, y, width, height, direction, hit_distance):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.direction = direction  # 0=top, 1=right, 2=bottom, 3=left
        self.hit_active = False
        self.hit_timer = 0
        self.hit_distance = hit_distance  # Dynamic hit distance based on screen size
    
    def activate_hit(self):
        """Activate the hit state for the paddle"""
        self.hit_active = True
        self.hit_timer = 4  # Active for 10 frames
    
    def update(self):
        """Update paddle state"""
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit_active = False
    
    def hit(self):
        """Trigger hit animation"""
        self.hit_timer = PADDLE_HIT_DURATION
    
    def move(self, direction, amount, game_rect):
        """Move paddle left/right or up/down depending on orientation"""
        if self.direction in [0, 2]:  # Top or bottom (horizontal paddle)
            if direction == "left":
                self.x = max(game_rect.left, self.x - amount)
            elif direction == "right":
                self.x = min(game_rect.right - self.width, self.x + amount)
        else:  # Left or right (vertical paddle)
            if direction == "up":
                self.y = max(game_rect.top, self.y - amount)
            elif direction == "down":
                self.y = min(game_rect.bottom - self.height, self.y + amount)
    
    def get_rect(self):
        """Get the paddle rectangle with hit animation applied"""
        paddle_hit_offset = 0
        if self.hit_timer > 0:
            paddle_hit_offset = self.hit_distance * (self.hit_timer / PADDLE_HIT_DURATION)
        
        if self.direction == 0:  # Top - extend downward
            return pygame.Rect(self.x, self.y, self.width, self.height + paddle_hit_offset)
        elif self.direction == 1:  # Right - extend leftward
            return pygame.Rect(self.x - paddle_hit_offset, self.y, 
                             self.height + paddle_hit_offset, self.width)
        elif self.direction == 2:  # Bottom - extend upward
            return pygame.Rect(self.x, self.y - paddle_hit_offset, 
                             self.width, self.height + paddle_hit_offset)
        elif self.direction == 3:  # Left - extend rightward
            return pygame.Rect(self.x, self.y, 
                             self.height + paddle_hit_offset, self.width)
    
    def check_collision(self, ball):
        """Check if the ball collides with this paddle and handle the collision"""
        paddle_rect = self.get_rect()
        
        # Check if the ball's rect intersects with the paddle's rect
        if ball.check_collision(paddle_rect):
            # Get the center of the paddle
            if self.direction in [0, 2]:  # Top or bottom paddle
                paddle_center_x = self.x + self.width / 2
                # Calculate how far from the center the ball hit (normalized to [-1, 1])
                hit_position = (ball.x - paddle_center_x) / (self.width / 2)
                
                # Reflect the ball's y direction
                ball.dy = -ball.dy
                
                # Adjust x direction based on where the ball hit the paddle
                ball.dx = hit_position * 0.8  # Scale factor to control the angle
                
                # Normalize the direction vector
                length = math.sqrt(ball.dx**2 + ball.dy**2)
                if length > 0:
                    ball.dx /= length
                    ball.dy /= length
                    
                # Apply hit boost
                ball.apply_hit_boost()
                
                print(f"Collision with {'top' if self.direction == 0 else 'bottom'} paddle! New direction: ({ball.dx}, {ball.dy})")
                return self.hit_active
                
            else:  # Left or right paddle
                paddle_center_y = self.y + self.width / 2  # width is the vertical size for vertical paddles
                # Calculate how far from the center the ball hit (normalized to [-1, 1])
                hit_position = (ball.y - paddle_center_y) / (self.width / 2)
                
                # Reflect the ball's x direction
                ball.dx = -ball.dx
                
                # Adjust y direction based on where the ball hit the paddle
                ball.dy = hit_position * 0.8  # Scale factor to control the angle
                
                # Normalize the direction vector
                length = math.sqrt(ball.dx**2 + ball.dy**2)
                if length > 0:
                    ball.dx /= length
                    ball.dy /= length
                    
                # Apply hit boost
                ball.apply_hit_boost()
                
                print(f"Collision with {'left' if self.direction == 3 else 'right'} paddle! New direction: ({ball.dx}, {ball.dy})")
                return self.hit_active
        
        return None  # No collision
    
    def draw(self, screen, color):
        """Draw the paddle on the screen"""
        pygame.draw.rect(screen, color, self.get_rect())