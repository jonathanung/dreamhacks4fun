# pong_paddle.py - Paddle class for Pong game
import pygame
import math
import time
import random
from pong_utils import *

# Constants for movement
PADDLE_MOVE_SPEED = 10.0  # Fixed paddle movement speed
MOVEMENT_TIMEOUT = 999999.0  # Effectively never timeout (stop only on explicit stop commands)
MIN_MOVEMENT_TIME = 0.0   # No minimum movement time - respond immediately to commands

# Import PADDLE_HIT_DURATION from pong_utils or define it here if not imported
try:
    from pong_utils import PADDLE_HIT_DURATION
except ImportError:
    # Fallback if not imported
    PADDLE_HIT_DURATION = 10  # Duration in frames

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
        
        # Movement flags
        self.is_moving_left = False
        self.is_moving_right = False
        self.is_moving_up = False
        self.is_moving_down = False
        
        # Timestamps for last movement commands
        self.last_left_time = 0
        self.last_right_time = 0
        self.last_up_time = 0
        self.last_down_time = 0
        
        # Last time a movement was started (for MIN_MOVEMENT_TIME)
        self.movement_start_times = {
            "left": 0,
            "right": 0,
            "up": 0,
            "down": 0
        }
    
    def activate_hit(self):
        """Activate the hit state for the paddle"""
        self.hit_active = True
        self.hit_timer = 4  # Active for 10 frames
    
    def update(self):
        """Update paddle state and apply movement"""
        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit_active = False
        
        current_time = time.time()
        
        # Check for timeout and stop movement if needed
        if self.is_moving_left and (current_time - self.last_left_time > MOVEMENT_TIMEOUT):
            self.is_moving_left = False
            
        if self.is_moving_right and (current_time - self.last_right_time > MOVEMENT_TIMEOUT):
            self.is_moving_right = False
            
        if self.is_moving_up and (current_time - self.last_up_time > MOVEMENT_TIMEOUT):
            self.is_moving_up = False
            
        if self.is_moving_down and (current_time - self.last_down_time > MOVEMENT_TIMEOUT):
            self.is_moving_down = False
        
        # Debug print movement state occasionally
        if random.random() < 0.05:  # 5% chance each frame
            print(f"\n>>> PADDLE DEBUG: Paddle {self.direction} movement state: left={self.is_moving_left}, right={self.is_moving_right}, up={self.is_moving_up}, down={self.is_moving_down}")
            print(f">>> PADDLE DEBUG: Paddle {self.direction} position: x={self.x}, y={self.y}")
        
        # Apply movement based on current flags
        old_x, old_y = self.x, self.y
        
        if self.direction in [0, 2]:  # Top or bottom (horizontal paddle)
            if self.is_moving_left:
                self.x -= PADDLE_MOVE_SPEED
            if self.is_moving_right:
                self.x += PADDLE_MOVE_SPEED
        else:  # Left or right (vertical paddle)
            if self.is_moving_up:
                self.y -= PADDLE_MOVE_SPEED
            if self.is_moving_down:
                self.y += PADDLE_MOVE_SPEED
            
        # Report if paddle actually moved
        if old_x != self.x or old_y != self.y:
            print(f"\n>>> PADDLE DEBUG: Paddle {self.direction} MOVED from ({old_x}, {old_y}) to ({self.x}, {self.y})")
    
    def hit(self):
        """Trigger hit animation"""
        self.hit_timer = PADDLE_HIT_DURATION
    
    def start_move(self, direction):
        """Start moving in a direction and update timestamp"""
        current_time = time.time()
        
        print(f"\n>>> PADDLE DEBUG: Paddle {self.direction} start_move({direction}) called")
        
        # Record the start time for minimum movement enforcement
        self.movement_start_times[direction] = current_time
        
        if direction == "left":
            self.is_moving_left = True
            self.is_moving_right = False
            self.last_left_time = current_time
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_left set to TRUE")
        elif direction == "right":
            self.is_moving_right = True
            self.is_moving_left = False
            self.last_right_time = current_time
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_right set to TRUE")
        elif direction == "up":
            self.is_moving_up = True
            self.is_moving_down = False
            self.last_up_time = current_time
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_up set to TRUE")
        elif direction == "down":
            self.is_moving_down = True
            self.is_moving_up = False
            self.last_down_time = current_time
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_down set to TRUE")
        
        # Print current movement state
        print(f">>> PADDLE DEBUG: Paddle {self.direction} movement state: left={self.is_moving_left}, right={self.is_moving_right}, up={self.is_moving_up}, down={self.is_moving_down}")
    
    def stop_move(self, direction):
        """Stop moving in a direction"""
        print(f"\n>>> PADDLE DEBUG: Paddle {self.direction} stop_move({direction}) called")
        
        if direction == "left":
            was_moving = self.is_moving_left
            self.is_moving_left = False
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_left set to FALSE (was {was_moving})")
        elif direction == "right":
            was_moving = self.is_moving_right
            self.is_moving_right = False
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_right set to FALSE (was {was_moving})")
        elif direction == "up":
            was_moving = self.is_moving_up
            self.is_moving_up = False
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_up set to FALSE (was {was_moving})")
        elif direction == "down":
            was_moving = self.is_moving_down
            self.is_moving_down = False
            print(f">>> PADDLE DEBUG: Paddle {self.direction} is_moving_down set to FALSE (was {was_moving})")
        
        # Print current movement state
        print(f">>> PADDLE DEBUG: Paddle {self.direction} movement state: left={self.is_moving_left}, right={self.is_moving_right}, up={self.is_moving_up}, down={self.is_moving_down}")
    
    def move(self, direction, amount, game_rect):
        """
        Legacy movement method - now used to initialize movement direction
        For key down events, call start_move
        For key up events, call stop_move
        """
        # Set the movement state and update timestamp
        self.start_move(direction)
        
        # Also perform instant movement for backward compatibility
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
                
        # Apply boundary constraints
        self.apply_boundaries(game_rect)
    
    def apply_boundaries(self, game_rect):
        """Keep the paddle within the game boundaries"""
        if self.direction in [0, 2]:  # Top or bottom (horizontal paddle)
            self.x = max(game_rect.left, min(game_rect.right - self.width, self.x))
        else:  # Left or right (vertical paddle)
            self.y = max(game_rect.top, min(game_rect.bottom - self.height, self.y))
                
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