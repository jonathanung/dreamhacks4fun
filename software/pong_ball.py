# pong_ball.py - Ball class for Pong game
import pygame
import math
import random
import time
from pong_utils import *

# Constants (if not defined elsewhere)
BALL_RESET_DURATION = 60  # Number of frames to wait before moving after reset
BALL_SPEED_INCREMENT = 0.75 # Speed increase after each paddle hit (increased by 1.5x, was 0.5)
BALL_MAX_SPEED = 1000  # Maximum ball speed

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.base_speed = speed
        self.speed_multiplier = 1.0
        self.dx = 0
        self.dy = 0
        self.reset_timer = 0
        self.hit_boost = 1.0
        self.game_started = False
        self.first_launch = True
        
        # Hit boost tracking
        self.is_boosted = False
        self.boost_multiplier = 1.0
        
        # For visual effects
        self.effect_time = 0
        self.effect_duration = 0.2
        self.boost_color = (255, 255, 100)
        
        # Initialize with a normalized direction vector
        self.reset(x, y)
        print(f"Ball initialized: position=({self.x}, {self.y}), direction=({self.dx}, {self.dy}), speed={self.base_speed}, radius={self.radius}")
    
    def reset(self, x, y):
        """Reset the ball after a player loses a life (between rounds)"""
        self.x = x
        self.y = y
        self.reset_timer = BALL_RESET_DURATION
        
        # Reset hit boost multiplier
        self.hit_boost = 1.0
        
        # Increment base speed between rounds
        self.base_speed = min(self.base_speed + BALL_SPEED_INCREMENT, BALL_MAX_SPEED)
        print(f"Round ended: Ball speed increased to {self.base_speed}")
        
        # IMPROVED DIRECTION SELECTION: include all 4 quadrants with better angle distribution
        import random, math
        
        # Choose from 4 quadrants instead of just 2
        quadrant = random.randint(0, 3)
        
        if quadrant == 0:  # Top-right
            angle = random.uniform(0, 0.5 * math.pi)
        elif quadrant == 1:  # Bottom-right
            angle = random.uniform(0.5 * math.pi, math.pi)
        elif quadrant == 2:  # Bottom-left
            angle = random.uniform(math.pi, 1.5 * math.pi)
        else:  # Top-left
            angle = random.uniform(1.5 * math.pi, 2 * math.pi)
        
        # Avoid angles that are too vertical or horizontal (within 15 degrees of axes)
        min_angle_offset = 0.26  # ~15 degrees
        
        # Calculate how close we are to 0, 90, 180, or 270 degrees
        angle_mod = angle % (0.5 * math.pi)  # Distance to closest 90-degree increment
        if angle_mod < min_angle_offset:
            # Too close to 0, 90, 180, or 270 - adjust angle
            angle += min_angle_offset
        elif angle_mod > (0.5 * math.pi - min_angle_offset):
            angle -= min_angle_offset
        
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        
        # Normalize direction vector
        length = math.sqrt(self.dx**2 + self.dy**2)
        if length > 0:
            self.dx /= length
            self.dy /= length
        
        print(f"Ball reset: position=({self.x}, {self.y}), direction=({self.dx}, {self.dy}), reset_timer={self.reset_timer}")
    
    def set_speed_multiplier(self, multiplier):
        """Set a multiplier for the ball's speed (for fever mode)"""
        self.speed_multiplier = multiplier
    
    def update(self):
        """Update ball position and state"""
        print(f"Ball update: game_started={self.game_started}, reset_timer={self.reset_timer}")
        
        if not self.game_started:
            print("Ball not moving: game not started")
            return
            
        if self.reset_timer > 0:
            self.reset_timer -= 1
            print(f"Ball in reset state: {self.reset_timer} frames remaining")
            return
        
        # Fix for speed multipliers: calculate effective speed correctly
        effective_speed = self.base_speed * self.hit_boost * self.speed_multiplier
        
        # CRITICAL: Normalize direction and apply effective speed
        magnitude = math.sqrt(self.dx**2 + self.dy**2)
        if magnitude > 0:
            normalized_dx = self.dx / magnitude
            normalized_dy = self.dy / magnitude
            
            # Store old position for boundary checks
            old_x = self.x
            old_y = self.y
            
            # Move with proper speed
            self.x += normalized_dx * effective_speed
            self.y += normalized_dy * effective_speed
            
            # Update the direction vectors to maintain proportions but have correct magnitude
            self.dx = normalized_dx 
            self.dy = normalized_dy
        
        print(f"Ball moved to: ({self.x}, {self.y}) with speed {effective_speed}")
        
        # Update effect timer
        if self.effect_time > 0:
            current_time = time.time()
            if current_time > self.effect_time + self.effect_duration:
                self.effect_time = 0
    
    def show_speed_effect(self, is_boost=False):
        """Start visual effect to show speed increase"""
        self.effect_time = time.time()
        if is_boost:
            self.boost_color = (255, 165, 0)  # Orange for boosted ball
    
    def apply_hit_boost(self):
        """Apply speed boost from a hit"""
        # Double the speed from current speed (allows chaining)
        self.boost_multiplier *= 2.0
        
        # Calculate current direction unit vector
        current_magnitude = math.sqrt(self.dx**2 + self.dy**2)
        dir_x = self.dx / current_magnitude
        dir_y = self.dy / current_magnitude
        
        # Apply new speed with boost multiplier
        boosted_speed = self.base_speed * self.hit_boost * self.speed_multiplier * self.boost_multiplier
        self.dx = dir_x * boosted_speed
        self.dy = dir_y * boosted_speed
        
        self.is_boosted = True
        self.show_speed_effect(True)
    
    def reset_boost(self):
        """Reset speed boost after regular bounce"""
        if self.is_boosted:
            # Calculate current direction unit vector
            current_magnitude = math.sqrt(self.dx**2 + self.dy**2)
            dir_x = self.dx / current_magnitude
            dir_y = self.dy / current_magnitude
            
            # Apply normal speed
            self.dx = dir_x * self.base_speed * self.hit_boost * self.speed_multiplier
            self.dy = dir_y * self.base_speed * self.hit_boost * self.speed_multiplier
            
            self.is_boosted = False
            self.boost_multiplier = 1.0
    
    def check_boundaries(self, game_rect, players_alive=None):
        """Check for collisions with game boundaries and walls for eliminated players"""
        if self.reset_timer > 0:
            return None
        
        # Add defensive boundary check - if the ball is way outside the boundaries, 
        # reset it to the center of the screen
        if (self.x < game_rect.left - self.radius * 2 or
            self.x > game_rect.right + self.radius * 2 or
            self.y < game_rect.top - self.radius * 2 or
            self.y > game_rect.bottom + self.radius * 2):
            print(f"WARNING: Ball escaped boundaries at ({self.x}, {self.y}). Resetting to center.")
            self.reset(game_rect.centerx, game_rect.centery)
            return None
        
        wall_thickness = int(min(game_rect.width, game_rect.height) * 0.05)
        
        # Check dead player walls first
        if players_alive:
            # Left wall (Player 4)
            if not players_alive[3] and self.x - self.radius < game_rect.left + wall_thickness:
                self.dx = abs(self.dx)  # Bounce right
                # Ensure ball is inside the boundary
                self.x = game_rect.left + wall_thickness + self.radius
                return None
            
            # Right wall (Player 3) - SWAPPED
            if not players_alive[1] and self.x + self.radius > game_rect.right - wall_thickness:
                self.dx = -abs(self.dx)  # Bounce left
                # Ensure ball is inside the boundary
                self.x = game_rect.right - wall_thickness - self.radius
                return None
            
            # Top wall (Player 1)
            if not players_alive[0] and self.y - self.radius < game_rect.top + wall_thickness:
                self.dy = abs(self.dy)  # Bounce down
                # Ensure ball is inside the boundary
                self.y = game_rect.top + wall_thickness + self.radius
                return None
            
            # Bottom wall (Player 2) - SWAPPED
            if not players_alive[2] and self.y + self.radius > game_rect.bottom - wall_thickness:
                self.dy = -abs(self.dy)  # Bounce up
                # Ensure ball is inside the boundary
                self.y = game_rect.bottom - wall_thickness - self.radius
                return None
        
        # Normal boundaries check - only for ACTIVE player walls
        # Left wall (Player 4)
        if self.x - self.radius < game_rect.left:
            if players_alive is None or players_alive[3]:
                print(f"Ball hit LEFT wall - Player 4 (index 3) loses a life")
                return 3  # Player 4 loses a life
            self.dx = abs(self.dx)  # Bounce right
            # Ensure ball is inside the boundary
            self.x = game_rect.left + self.radius
        
        # Right wall (Player 2)
        elif self.x + self.radius > game_rect.right:
            if players_alive is None or players_alive[1]:
                print(f"Ball hit RIGHT wall - Player 2 (index 1) loses a life")
                return 1  # Player 2 loses a life
            self.dx = -abs(self.dx)  # Bounce left
            # Ensure ball is inside the boundary
            self.x = game_rect.right - self.radius
        
        # Top wall (Player 1)
        elif self.y - self.radius < game_rect.top:
            if players_alive is None or players_alive[0]:
                print(f"Ball hit TOP wall - Player 1 (index 0) loses a life")
                return 0  # Player 1 loses a life
            self.dy = abs(self.dy)  # Bounce down
            # Ensure ball is inside the boundary
            self.y = game_rect.top + self.radius
        
        # Bottom wall (Player 3)
        elif self.y + self.radius > game_rect.bottom:
            if players_alive is None or players_alive[2]:
                print(f"Ball hit BOTTOM wall - Player 3 (index 2) loses a life")
                return 2  # Player 3 loses a life
            self.dy = -abs(self.dy)  # Bounce up
            # Ensure ball is inside the boundary
            self.y = game_rect.bottom - self.radius
        
        # Safeguard against out-of-bounds ball (beyond all walls)
        # This should never happen, but just in case the ball goes out of bounds
        if (self.x < game_rect.left - 2*self.radius or 
            self.x > game_rect.right + 2*self.radius or
            self.y < game_rect.top - 2*self.radius or
            self.y > game_rect.bottom + 2*self.radius):
            print(f"WARNING: Ball is out of bounds at ({self.x}, {self.y}). Resetting to center.")
            self.reset(game_rect.centerx, game_rect.centery)
            return None
            
        return None
    
    def draw(self, screen, color):
        """Draw the ball on the screen with speed effect"""
        # Use boosted color if ball is boosted
        ball_color = self.boost_color if self.is_boosted else color
        
        # Normal ball
        pygame.draw.circle(screen, ball_color, (int(self.x), int(self.y)), self.radius)
        
        # Draw speed effect if active
        if self.effect_time > 0:
            current_time = time.time()
            effect_progress = 1.0 - min(1.0, (current_time - self.effect_time) / self.effect_duration)
            
            # Calculate effect size
            effect_radius = self.radius * (1 + effect_progress * 2)  # Larger effect for boost
            
            # Effect color depends on whether it's a boost or regular speed increase
            effect_color = self.boost_color if self.is_boosted else (255, 255, 255)
            effect_color = (*effect_color[:3], int(200 * effect_progress))  # Add alpha
            
            effect_surface = pygame.Surface((effect_radius*2, effect_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(effect_surface, effect_color, 
                             (int(effect_radius), int(effect_radius)), int(effect_radius))
            
            screen.blit(effect_surface, 
                      (int(self.x - effect_radius), int(self.y - effect_radius)))

    def check_collision(self, paddle_rect):
        """Check if the ball collides with a paddle"""
        # Create a rect for the ball
        ball_rect = pygame.Rect(
            self.x - self.radius, 
            self.y - self.radius,
            self.radius * 2, 
            self.radius * 2
        )
        
        # Debug output for collision detection
        if ball_rect.colliderect(paddle_rect):
            print(f"Ball collision detected! Ball: {ball_rect}, Paddle: {paddle_rect}")
            return True
        
        return False

    def get_rect(self):
        """Get the ball's rectangle for collision detection"""
        return pygame.Rect(
            self.x - self.radius, 
            self.y - self.radius,
            self.radius * 2, 
            self.radius * 2
        )

    def apply_boost(self):
        """Apply speed boost to the ball"""
        # Simple boost for paddle hits
        self.hit_boost *= 1.5
        
        # # Cap the boost multiplier
        # if self.hit_boost > 3.0:
        #     self.hit_boost = 3.0