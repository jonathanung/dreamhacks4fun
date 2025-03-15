# pong_fever.py - Even more simplified version
import pygame
import random
import math
import traceback

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

class FeverOrb:
    """A simplified orb with robust error handling"""
    def __init__(self, game_rect, radius=30):
        try:
            self.radius = radius
            self.game_rect = game_rect
            
            # Random position within the game area (with margin to avoid edges)
            margin = int(game_rect.width * 0.15)  # 15% margin
            self.x = random.randint(game_rect.left + margin, game_rect.right - margin)
            self.y = random.randint(game_rect.top + margin, game_rect.bottom - margin)
            
            # Color cycling
            self.hue = 0
            self.hue_speed = 1
        except Exception as e:
            print(f"Error initializing FeverOrb: {e}")
            # Set default values
            self.radius = 30
            self.game_rect = game_rect
            self.x = game_rect.centerx
            self.y = game_rect.centery
            self.hue = 0
            self.hue_speed = 1
    
    def update(self):
        """Update the fever orb animation"""
        try:
            self.hue = (self.hue + self.hue_speed) % 360
        except Exception as e:
            print(f"Error updating FeverOrb: {e}")
    
    def check_collision(self, ball_rect):
        """Check if the ball collides with the fever orb"""
        try:
            orb_rect = pygame.Rect(
                self.x - self.radius, 
                self.y - self.radius,
                self.radius * 2, 
                self.radius * 2
            )
            return orb_rect.colliderect(ball_rect)
        except Exception as e:
            print(f"Error checking collision in FeverOrb: {e}")
            return False
    
    def draw(self, screen):
        """Draw the fever orb"""
        try:
            r, g, b = hsv_to_rgb(self.hue/360, 1, 1)
            pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), int(self.radius))
            
            # Draw inner highlight
            highlight_radius = self.radius * 0.7
            r, g, b = hsv_to_rgb((self.hue + 30)/360, 0.5, 1)
            pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), int(highlight_radius))
        except Exception as e:
            print(f"Error drawing FeverOrb: {e}")
            # Fallback drawing
            try:
                pygame.draw.circle(screen, (255, 0, 255), (int(self.x), int(self.y)), int(self.radius))
            except:
                pass

class FeverEffect:
    """A simplified fever effect with robust error handling"""
    def __init__(self, duration=10):
        self.active = False
        self.duration = duration
        self.timer = 0
        self.hue = 0
    
    def activate(self):
        """Activate the fever effect"""
        try:
            self.active = True
            self.timer = self.duration * 60  # Convert seconds to frames (60 FPS)
        except Exception as e:
            print(f"Error activating FeverEffect: {e}")
    
    def update(self):
        """Update the fever effect"""
        try:
            if self.active:
                self.timer -= 1
                if self.timer <= 0:
                    self.active = False
                
                self.hue = (self.hue + 2) % 360
        except Exception as e:
            print(f"Error updating FeverEffect: {e}")
            # Reset to safe state
            self.active = False
    
    def draw(self, screen):
        """Draw the fever effect overlay"""
        if not self.active:
            return
        
        try:
            width, height = screen.get_size()
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            
            try:
                r, g, b = hsv_to_rgb(self.hue/360, 0.7, 1)
                overlay.fill((r, g, b, 30))  # Translucent color overlay
            except:
                # Fallback color
                overlay.fill((255, 0, 255, 30))
            
            screen.blit(overlay, (0, 0))
        except Exception as e:
            print(f"Error drawing FeverEffect: {e}")
    
    def deactivate(self):
        """Immediately deactivate fever effect"""
        self.active = False
        self.timer = 0
        print("Fever effect deactivated due to ball reset") 