# pong_paddle.py - Paddle class for Pong game
import pygame
from pong_utils import *

class Paddle:
    def __init__(self, x, y, width, height, direction):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.direction = direction  # 0=top, 1=right, 2=bottom, 3=left
        self.hit_timer = 0
    
    def update(self):
        """Update paddle state"""
        if self.hit_timer > 0:
            self.hit_timer -= 1
    
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
            paddle_hit_offset = PADDLE_HIT_DISTANCE * (self.hit_timer / PADDLE_HIT_DURATION)
        
        if self.direction == 0:  # Top
            return pygame.Rect(self.x, self.y - paddle_hit_offset, 
                             self.width, self.height + paddle_hit_offset)
        elif self.direction == 1:  # Right
            return pygame.Rect(self.x - paddle_hit_offset, self.y, 
                             self.height + paddle_hit_offset, self.width)
        elif self.direction == 2:  # Bottom
            return pygame.Rect(self.x, self.y, 
                             self.width, self.height + paddle_hit_offset)
        elif self.direction == 3:  # Left
            return pygame.Rect(self.x, self.y, 
                             self.height + paddle_hit_offset, self.width)
    
    def check_collision(self, ball):
        """Check if ball collides with paddle and handle bounce"""
        # Get paddle rect with hit animation
        paddle_rect = self.get_rect()
        
        # Expanded collision rect for better detection
        expanded_rect = paddle_rect.inflate(ball.radius*2, ball.radius*2)
        
        # Check if the ball's next position intersects with the paddle
        next_ball_x = ball.x + ball.dx
        next_ball_y = ball.y + ball.dy
        
        if expanded_rect.collidepoint(next_ball_x, next_ball_y):
            # Calculate bounce based on paddle direction
            if self.direction == 0:  # Top paddle
                # Horizontal position determines angle
                relative_x = (ball.x - self.x) / self.width
                angle = math.pi * (0.25 + 0.5 * relative_x)
                ball.dx = math.cos(angle) * ball.speed
                ball.dy = abs(math.sin(angle) * ball.speed)  # Always bounce downward
                
                # If paddle is hitting, add extra velocity
                if self.hit_timer > 0:
                    ball.dy *= 1.5
            
            elif self.direction == 2:  # Bottom paddle
                # Horizontal position determines angle
                relative_x = (ball.x - self.x) / self.width
                angle = math.pi * (0.25 + 0.5 * relative_x)
                ball.dx = math.cos(angle) * ball.speed
                ball.dy = -abs(math.sin(angle) * ball.speed)  # Always bounce upward
                
                # If paddle is hitting, add extra velocity
                if self.hit_timer > 0:
                    ball.dy *= 1.5
            
            elif self.direction == 1:  # Right paddle
                # Vertical position determines angle
                relative_y = (ball.y - self.y) / self.width  # width is actually the paddle's height for vertical paddles
                angle = math.pi * (0.75 + 0.5 * relative_y)
                ball.dx = -abs(math.cos(angle) * ball.speed)  # Always bounce leftward
                ball.dy = math.sin(angle) * ball.speed
                
                # If paddle is hitting, add extra velocity
                if self.hit_timer > 0:
                    ball.dx *= 1.5
            
            elif self.direction == 3:  # Left paddle
                # Vertical position determines angle
                relative_y = (ball.y - self.y) / self.width  # width is actually the paddle's height for vertical paddles
                angle = math.pi * (0.75 + 0.5 * relative_y)
                ball.dx = abs(math.cos(angle) * ball.speed)  # Always bounce rightward
                ball.dy = math.sin(angle) * ball.speed
                
                # If paddle is hitting, add extra velocity
                if self.hit_timer > 0:
                    ball.dx *= 1.5
            
            # Move ball in new direction
            ball.x += ball.dx
            ball.y += ball.dy
            
            return True
        
        return False
    
    def draw(self, screen, color):
        """Draw the paddle on the screen"""
        pygame.draw.rect(screen, color, self.get_rect())