# Add these imports if not already present
import pygame
import sys
import os
import random
import math
import traceback
from pong_utils import *
from pong_paddle import Paddle
from pong_ball import Ball
from pong_fever import FeverOrb, FeverEffect

# Define constants if they don't exist elsewhere
if not 'PLAYER_COLORS' in globals():
    PLAYER_COLORS = [
        (255, 50, 50),    # Red (Player 1 - Top)
        (50, 255, 50),    # Green (Player 2 - Right)
        (50, 50, 255),    # Blue (Player 3 - Bottom)
        (255, 255, 50)    # Yellow (Player 4 - Left)
    ]

if not 'WALL_COLOR' in globals():
    WALL_COLOR = (200, 200, 200)

if not 'PLAYER_STARTING_LIVES' in globals():
    PLAYER_STARTING_LIVES = 3

# Create a Pong game class that can be initialized and run as a state
class PongGame:
    def __init__(self, screen=None, event_handler=None):
        """Initialize the Pong game state"""
        self.screen = screen
        self.event_handler = event_handler
        self.running = False
        self.initialized = False
        self.clock = None
        self.font = None
        self.game_started = False
        self.game_over = False
        self.winner = None
        self.paddles = None
        self.ball = None
        self.players_alive = [True, True, True, True]
        self.player_lives = [PLAYER_STARTING_LIVES] * 4
        self.bg_image = None
        self.fever_effect = None
        self.fever_orb = None
        self.pokemon_sprites = {}
        self.player_pokemon = {}
        self.start_time = pygame.time.get_ticks()
        self.show_start_text = False
        self.player_count = 4  # Default, will be updated in initialize
        
    def initialize(self, player_count=4):
        """Initialize pygame and game resources"""
        if self.initialized:
            return True
            
        try:
            # If screen wasn't provided, create one
            if self.screen is None:
                if not pygame.get_init():
                    pygame.init()
                self.screen = pygame.display.set_mode((800, 600))
                pygame.display.set_caption("Multiplayer Pong")
            
            # Get screen dimensions
            self.WIDTH, self.HEIGHT = self.screen.get_size()
            
            # Initialize resources
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
            
            # Get game area
            self.GAME_RECT = get_square_game_rect(self.WIDTH, self.HEIGHT)
            
            # Calculate dimensions
            try:
                dims = calculate_game_dimensions(self.WIDTH, self.HEIGHT)
                self.ball_radius = dims.get('ball_radius', 15)
                self.ball_speed = dims.get('ball_speed', 5)
                self.paddle_hit_distance = dims.get('paddle_hit_distance', 10)
                self.fever_orb_radius = dims.get('fever_orb_radius', 30)
            except Exception as e:
                print(f"Error calculating dimensions: {e}")
                self.ball_radius = 15
                self.ball_speed = 5
                self.paddle_hit_distance = 10
                self.fever_orb_radius = 30
            
            # Load pokemon sprites
            self.load_pokemon_sprites()
            
            # Store player count
            self.player_count = player_count
            
            # Get the center of the game field
            center_x = self.GAME_RECT.centerx
            center_y = self.GAME_RECT.centery
            
            # Determine the short dimension for consistent positioning
            short_dim = min(self.GAME_RECT.width, self.GAME_RECT.height)
            
            # Define paddle dimensions
            paddle_long = int(short_dim * 0.15)  # 15% of short dimension
            paddle_short = int(short_dim * 0.02)  # 2% of short dimension
            hit_distance = int(short_dim * 0.05)  # 5% of short dimension
            
            # Distance from center to paddles (47.5% of short dimension)
            paddle_distance = int(short_dim * 0.475)
            
            # Initialize paddles with proper orientation
            self.paddles = [
                # Top paddle (horizontal) - width is longer than height
                Paddle(center_x, center_y - paddle_distance, 
                      paddle_long, paddle_short, 0, hit_distance),
                
                # Right paddle (vertical) - IMPORTANT: For right paddle (direction 1), 
                # width and height need to be swapped in a different way due to Paddle.get_rect() implementation
                Paddle(center_x + paddle_distance, center_y, 
                      paddle_long, paddle_short, 1, hit_distance),
                
                # Bottom paddle (horizontal) - width is longer than height
                Paddle(center_x, center_y + paddle_distance, 
                      paddle_long, paddle_short, 2, hit_distance),
                
                # Left paddle (vertical) - IMPORTANT: For left paddle (direction 3),
                # width and height need to be swapped in a different way due to Paddle.get_rect() implementation
                Paddle(center_x - paddle_distance, center_y, 
                      paddle_long, paddle_short, 3, hit_distance)
            ]

            self.ball = Ball(self.GAME_RECT.centerx, self.GAME_RECT.centery, 
                           self.ball_radius, self.ball_speed)
            
            # Load background
            try:
                bg_path = os.path.join(os.path.dirname(__file__), "pong-bg.jpg")
                if os.path.exists(bg_path):
                    self.bg_image = pygame.image.load(bg_path)
                    self.bg_image = pygame.transform.scale(self.bg_image, (self.WIDTH, self.HEIGHT))
            except Exception as e:
                print(f"Could not load background image: {e}")
                self.bg_image = None
            
            # Initialize fever mode
            self.fever_effect = FeverEffect(FEVER_DURATION)
            self.fever_orb = None
            
            # Try to play music if available
            try:
                music_path = os.path.join(os.path.dirname(__file__), "pong-music.mp3")
                if os.path.exists(music_path) and pygame.mixer.get_init():
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
            except Exception as e:
                print(f"Could not load music: {e}")
            
            # Explicitly set game to not started
            self.game_started = False
            
            # Make sure these values are properly initialized
            self.game_over = False
            self.winner = None
            
            # Make sure all players start with lives
            self.players_alive = [False, False, False, False]
            self.player_lives = [0, 0, 0, 0]
            
            # SWAPPED LOGIC: Player 1 (top) is always active
            self.players_alive[0] = True
            self.player_lives[0] = PLAYER_STARTING_LIVES
            
            # For 2 players, enable player 2 (bottom) - SWAPPED
            if player_count >= 2:
                self.players_alive[2] = True  # Bottom player is now Player 2
                self.player_lives[2] = PLAYER_STARTING_LIVES
            
            # For 3 players, enable player 3 (right) - SWAPPED
            if player_count >= 3:
                self.players_alive[1] = True  # Right player is now Player 3
                self.player_lives[1] = PLAYER_STARTING_LIVES
            
            # For 4 players, enable player 4 (left) - unchanged
            if player_count >= 4:
                self.players_alive[3] = True
                self.player_lives[3] = PLAYER_STARTING_LIVES
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing Pong game: {e}")
            traceback.print_exc()
            return False
    
    def load_pokemon_sprites(self):
        """Load Pokémon sprites for player lives"""
        pokemon_names = ['bulbasaur', 'charmander', 'squirtle', 'pikachu']
        
        for name in pokemon_names:
            try:
                sprite_path = os.path.join(os.path.dirname(__file__), f'{name}.png')
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path)
                    self.pokemon_sprites[name] = sprite
                else:
                    print(f"Sprite file not found: {sprite_path}")
                    self.create_placeholder_sprite(name)
            except Exception as e:
                print(f"Could not load {name} sprite: {e}")
                self.create_placeholder_sprite(name)
        
        # Map players to Pokémon sprites
        self.player_pokemon = {
            0: self.pokemon_sprites.get('charmander'),  # Red - Charmander
            1: self.pokemon_sprites.get('bulbasaur'),   # Green - Bulbasaur
            2: self.pokemon_sprites.get('squirtle'),    # Blue - Squirtle
            3: self.pokemon_sprites.get('pikachu')      # Yellow - Pikachu
        }
    
    def create_placeholder_sprite(self, name):
        """Create a placeholder colored square if sprite can't be loaded"""
        placeholder = pygame.Surface((30, 30))
        if name == 'charmander':
            placeholder.fill((255, 50, 50))  # Red
        elif name == 'bulbasaur':
            placeholder.fill((50, 255, 50))  # Green
        elif name == 'squirtle':
            placeholder.fill((50, 50, 255))  # Blue
        elif name == 'pikachu':
            placeholder.fill((255, 255, 50))  # Yellow
        else:
            placeholder.fill((255, 255, 255))  # White fallback
        self.pokemon_sprites[name] = placeholder
    
    def reset_game(self):
        """Reset the game state"""
        self.game_started = False
        self.game_over = False
        self.winner = None
        self.players_alive = [True, True, True, True]
        self.player_lives = [PLAYER_STARTING_LIVES] * 4
        self.ball.reset(self.GAME_RECT.centerx, self.GAME_RECT.centery)
        for paddle in self.paddles:
            self.reset_paddle_position(paddle)
        self.fever_orb = None
    
    def reset_paddle_position(self, paddle):
        """Reset paddle to center position"""
        # Get center coordinates and distance
        center_x = self.GAME_RECT.centerx
        center_y = self.GAME_RECT.centery
        short_dim = min(self.GAME_RECT.width, self.GAME_RECT.height)
        
        # Use EXACTLY the same distance as initialization (47.5% of short dimension)
        paddle_distance = int(short_dim * 0.475)
        
        # Reset to EXACT same positions as initialization
        # IMPORTANT: Mimic the exact same positioning logic from initialize()
        if paddle.direction == 0:  # Top
            paddle.x = center_x  # Paddle constructor will center itself
            paddle.y = center_y - paddle_distance
        elif paddle.direction == 1:  # Right
            paddle.x = center_x + paddle_distance
            paddle.y = center_y
        elif paddle.direction == 2:  # Bottom
            paddle.x = center_x
            paddle.y = center_y + paddle_distance
        elif paddle.direction == 3:  # Left
            paddle.x = center_x - paddle_distance
            paddle.y = center_y
    
    def handle_events(self, events):
        """Process pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                elif event.key == pygame.K_SPACE and not self.game_started:
                    print("Space pressed - starting game!")
                    self.game_started = True
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        
        return True
    
    def update(self):
        """Update game state"""
        if not self.game_started:
            return
        
        try:
            # Update paddles
            for paddle in self.paddles:
                paddle.update()
            
            # Update fever effect
            self.fever_effect.update()
            
            # Update fever orb if it exists
            if self.fever_orb:
                self.fever_orb.update()
                
                # Check for collision with ball
                if self.fever_orb.check_collision(self.ball.get_rect()):
                    self.fever_effect.activate()
                    self.fever_orb = None
            else:
                # Spawn new fever orb randomly
                if random.randint(0, 60 * random.randint(FEVER_ORB_MIN_SPAWN_TIME, FEVER_ORB_MAX_SPAWN_TIME)) == 0:
                    self.fever_orb = FeverOrb(self.GAME_RECT, self.fever_orb_radius)
            
            # Apply fever speed boost if active
            ball_speed_multiplier = 2.0 if self.fever_effect.active else 1.0
            
            # Add try-except for set_speed_multiplier
            try:
                self.ball.set_speed_multiplier(ball_speed_multiplier)
            except AttributeError:
                print("Warning: Ball doesn't have set_speed_multiplier method. Adding it dynamically.")
                # Add the method dynamically if it doesn't exist
                self.ball.speed_multiplier = ball_speed_multiplier
            
            # IMPORTANT: Make sure the ball knows the game has started
            self.ball.game_started = self.game_started
            
            # Debug ball state
            print(f"Ball state: position=({self.ball.x}, {self.ball.y}), direction=({self.ball.dx}, {self.ball.dy}), " +
                  f"reset_timer={self.ball.reset_timer}, game_started={self.ball.game_started}")
            
            # Update ball
            self.ball.update()
            
            # Check for collisions with paddles
            collision_detected = False
            for i, paddle in enumerate(self.paddles):
                if self.players_alive[i]:
                    collision_result = paddle.check_collision(self.ball)
                    if collision_result is not None:
                        # Apply appropriate boost based on hit vs regular bounce
                        if collision_result:  # True means hit was active
                            # Hit boost (stronger)
                            self.ball.hit_boost *= 1.2
                            if self.ball.hit_boost > 3.0:
                                self.ball.hit_boost = 3.0
                        else:
                            # Regular bounce (weaker)
                            self.ball.hit_boost *= 1.05
                            if self.ball.hit_boost > 2.0:
                                self.ball.hit_boost = 2.0
                        break
            
            # Check boundaries with player_alive status
            player_hit = self.ball.check_boundaries(self.GAME_RECT, self.players_alive)
            
            # Handle player elimination
            if player_hit is not None:
                self.player_lives[player_hit] -= 1
                
                if self.player_lives[player_hit] <= 0:
                    self.players_alive[player_hit] = False
                    
                    # Check if game is over (only one player left)
                    alive_count = sum(self.players_alive)
                    if alive_count <= 1:
                        last_player = -1
                        for i, alive in enumerate(self.players_alive):
                            if alive:
                                last_player = i
                                break
                        
                        if last_player >= 0:
                            self.game_over = True
                            self.winner = last_player
            
                # Reset ball
                self.ball.reset(self.GAME_RECT.centerx, self.GAME_RECT.centery)
                
                # Reset paddle
                if player_hit < len(self.paddles):
                    self.reset_paddle_position(self.paddles[player_hit])
        
        except Exception as e:
            print(f"Error updating game: {e}")
            import traceback
            traceback.print_exc()
    
    def draw(self):
        """Draw game state"""
        try:
            # Clear screen with black
            self.screen.fill((0, 0, 0))
            
            # Draw background if available
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            
            # Draw game boundary
            pygame.draw.rect(self.screen, WALL_COLOR, self.GAME_RECT, 2)
            
            # Draw fever orb if it exists
            if self.fever_orb:
                self.fever_orb.draw(self.screen)
            
            # Draw ball and paddles
            self.ball.draw(self.screen, (255, 255, 255))
            for i, paddle in enumerate(self.paddles):
                if self.players_alive[i]:
                    paddle.draw(self.screen, PLAYER_COLORS[i])
            
            # Draw fever effect overlay
            self.fever_effect.draw(self.screen)
            
            # Draw player lives with Pokémon
            self.draw_player_lives_with_pokemon()
            
            # Draw game messages
            if not self.game_started and self.show_start_text:
                text = self.font.render("Press SPACE to start", True, (255, 255, 255))
                self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2))
            elif self.game_over:
                if self.winner is not None:
                    text = self.font.render(f"Player {self.winner + 1} wins! Press R to restart", True, PLAYER_COLORS[self.winner])
                else:
                    text = self.font.render("Game Over! Press R to restart", True, (255, 255, 255))
                self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2))
            
            # Draw walls for eliminated players (thinner walls: 5% instead of 10%)
            wall_color = (100, 100, 100)  # Grey walls
            wall_thickness = int(min(self.GAME_RECT.width, self.GAME_RECT.height) * 0.05)
            
            # Top wall (Player 1)
            if not self.players_alive[0]:
                wall_rect = pygame.Rect(
                    self.GAME_RECT.left,
                    self.GAME_RECT.top,
                    self.GAME_RECT.width,
                    wall_thickness
                )
                pygame.draw.rect(self.screen, wall_color, wall_rect)
            
            # Right wall (Player 3) - SWAPPED
            if not self.players_alive[1]:
                wall_rect = pygame.Rect(
                    self.GAME_RECT.right - wall_thickness,
                    self.GAME_RECT.top,
                    wall_thickness,
                    self.GAME_RECT.height
                )
                pygame.draw.rect(self.screen, wall_color, wall_rect)
            
            # Bottom wall (Player 2) - SWAPPED
            if not self.players_alive[2]:
                wall_rect = pygame.Rect(
                    self.GAME_RECT.left,
                    self.GAME_RECT.bottom - wall_thickness,
                    self.GAME_RECT.width,
                    wall_thickness
                )
                pygame.draw.rect(self.screen, wall_color, wall_rect)
            
            # Left wall (Player 4)
            if not self.players_alive[3]:
                wall_rect = pygame.Rect(
                    self.GAME_RECT.left,
                    self.GAME_RECT.top,
                    wall_thickness,
                    self.GAME_RECT.height
                )
                pygame.draw.rect(self.screen, wall_color, wall_rect)
        
        except Exception as e:
            print(f"Error drawing game: {e}")
            traceback.print_exc()
    
    def draw_player_lives_with_pokemon(self):
        """Draw player lives using Pokémon sprites"""
        try:
            sprite_size = int(min(self.WIDTH, self.HEIGHT) * 0.05)  # 5% of screen size
            spacing = int(sprite_size * 1.2)
            
            for i, alive in enumerate(self.players_alive):
                if not alive:
                    # Draw eliminated text
                    text = self.font.render(f"Player {i+1}: ELIMINATED", True, WALL_COLOR)
                    if i == 0:  # Top
                        self.screen.blit(text, (10, 10))
                    elif i == 1:  # Right
                        self.screen.blit(text, (self.WIDTH - text.get_width() - 10, 10))
                    elif i == 2:  # Bottom
                        self.screen.blit(text, (10, self.HEIGHT - text.get_height() - 10))
                    elif i == 3:  # Left
                        self.screen.blit(text, (self.WIDTH - text.get_width() - 10, 
                                        self.HEIGHT - text.get_height() - 10))
                    continue
                
                # Get the player's Pokémon sprite
                sprite = self.player_pokemon.get(i)
                if sprite is None:
                    # Use fallback if sprite is missing
                    sprite = pygame.Surface((sprite_size, sprite_size))
                    sprite.fill(PLAYER_COLORS[i])
                
                # Scale sprite to desired size
                scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                
                # Get positions based on player
                if i == 0:  # Top
                    x_start = 10
                    y = 10
                elif i == 1:  # Right
                    x_start = self.WIDTH - (spacing * PLAYER_STARTING_LIVES) - 10
                    y = 10
                elif i == 2:  # Bottom
                    x_start = 10
                    y = self.HEIGHT - sprite_size - 10
                elif i == 3:  # Left
                    x_start = self.WIDTH - (spacing * PLAYER_STARTING_LIVES) - 10
                    y = self.HEIGHT - sprite_size - 10
                
                # Draw player number
                text = self.font.render(f"P{i+1}", True, PLAYER_COLORS[i])
                text_rect = text.get_rect()
                
                if i in [0, 2]:  # Left side
                    text_pos = (x_start, y + (sprite_size - text_rect.height) // 2)
                    x_start += text_rect.width + 10
                else:  # Right side
                    text_pos = (x_start - text_rect.width - 10, y + (sprite_size - text_rect.height) // 2)
                
                self.screen.blit(text, text_pos)
                
                # Draw lives as Pokémon sprites
                for j in range(self.player_lives[i]):
                    self.screen.blit(scaled_sprite, (x_start + j * spacing, y))
        
        except Exception as e:
            print(f"Error drawing player lives: {e}")
            traceback.print_exc()
    
    def process_input(self):
        """Process keyboard input"""
        try:
            keys = pygame.key.get_pressed()
            
            # Player 1 (Top) controls - W/A/S/D
            if self.players_alive[0]:
                if keys[pygame.K_a]:
                    self.paddles[0].move("left", self.paddles[0].hit_distance, self.GAME_RECT)
                if keys[pygame.K_d]:
                    self.paddles[0].move("right", self.paddles[0].hit_distance, self.GAME_RECT)
                if keys[pygame.K_s] and self.game_started and self.paddles[0].hit_timer == 0:
                    self.paddles[0].hit()
            
            # Player 2 (Right) controls - Arrow keys
            if self.players_alive[1]:
                if keys[pygame.K_UP]:
                    self.paddles[1].move("up", self.paddles[1].hit_distance, self.GAME_RECT)
                if keys[pygame.K_DOWN]:
                    self.paddles[1].move("down", self.paddles[1].hit_distance, self.GAME_RECT)
                if keys[pygame.K_LEFT] and self.game_started and self.paddles[1].hit_timer == 0:
                    self.paddles[1].hit()
            
            # Player 3 (Bottom) controls - H/J/K/L
            if self.players_alive[2]:
                if keys[pygame.K_j]:
                    self.paddles[2].move("left", self.paddles[2].hit_distance, self.GAME_RECT)
                if keys[pygame.K_l]:
                    self.paddles[2].move("right", self.paddles[2].hit_distance, self.GAME_RECT)
                if keys[pygame.K_k] and self.game_started and self.paddles[2].hit_timer == 0:
                    self.paddles[2].hit()
            
            # Player 4 (Left) controls - I/O/P
            if self.players_alive[3]:
                if keys[pygame.K_i]:
                    self.paddles[3].move("up", self.paddles[3].hit_distance, self.GAME_RECT)
                if keys[pygame.K_p]:
                    self.paddles[3].move("down", self.paddles[3].hit_distance, self.GAME_RECT)
                if keys[pygame.K_o] and self.game_started and self.paddles[3].hit_timer == 0:
                    self.paddles[3].hit()
        
        except Exception as e:
            print(f"Error processing input: {e}")
    
    def process_middleware_events(self):
        """Process events from middleware if available"""
        if self.event_handler is None:
            return
            
        try:
            events = []
            
            # Get events from the middleware
            if callable(self.event_handler):
                # It's a function we can call
                events = self.event_handler()
            elif hasattr(self.event_handler, 'get_events') and callable(self.event_handler.get_events):
                # It has a get_events method
                events = self.event_handler.get_events()
            elif isinstance(self.event_handler, list):
                # It's already a list of events
                events = self.event_handler
            else:
                print(f"Warning: Unsupported event_handler type: {type(self.event_handler)}")
                return
            
            # Process each event
            for event in events:
                if not isinstance(event, dict):
                    continue
                    
                player_id = event.get('player_id')
                action = event.get('action')
                
                if player_id is None or action is None:
                    continue
                    
                player_idx = player_id - 1  # Convert to 0-based index
                
                if player_idx < 0 or player_idx >= 4:
                    continue
                    
                if not self.players_alive[player_idx]:
                    continue
                
                # Process the event based on action
                if action == 'left':
                    if player_idx in [0, 2]:  # Top/Bottom
                        self.paddles[player_idx].move("left", self.paddles[player_idx].hit_distance, self.GAME_RECT)
                elif action == 'right':
                    if player_idx in [0, 2]:  # Top/Bottom
                        self.paddles[player_idx].move("right", self.paddles[player_idx].hit_distance, self.GAME_RECT)
                elif action == 'up':
                    if player_idx in [1, 3]:  # Right/Left
                        self.paddles[player_idx].move("up", self.paddles[player_idx].hit_distance, self.GAME_RECT)
                elif action == 'down':
                    if player_idx in [1, 3]:  # Right/Left
                        self.paddles[player_idx].move("down", self.paddles[player_idx].hit_distance, self.GAME_RECT)
                elif action == 'hit' and self.game_started and self.paddles[player_idx].hit_timer == 0:
                    self.paddles[player_idx].hit()
                elif action == 'start' and not self.game_started:
                    self.game_started = True
                elif action == 'restart' and self.game_over:
                    self.reset_game()
        
        except Exception as e:
            print(f"Error processing middleware events: {e}")
            import traceback
            traceback.print_exc()
    
    def run_frame(self):
        """Run a single frame of the game"""
        if not self.initialized and not self.initialize():
            print("Failed to initialize Pong game")
            return False
        
        # Process events
        if not self.handle_events(pygame.event.get()):
            return False
        
        # Process middleware events
        self.process_middleware_events()
        
        # Process input
        self.process_input()
        
        # Update game state
        self.update()
        
        # Draw
        self.draw()
        
        # Check if the game is over
        # THIS is likely happening too early - make sure game_over isn't True here
        if self.game_over and self.winner is not None:
            return self.winner
        
        return None
    
    def run(self):
        """Run the main game loop"""
        if not self.initialized and not self.initialize():
            print("Failed to initialize Pong game")
            return
        
        self.running = True
        
        try:
            while self.running:
                if not self.run_frame():
                    break
        
        except Exception as e:
            print(f"Error in game loop: {e}")
            traceback.print_exc()
        
        # Make sure we don't quit pygame if it's being managed externally
        if self.event_handler is None:
            pygame.quit()

    def debug_game_state(self):
        """Print debug information about the current game state"""
        print("\n--- GAME STATE DEBUG ---")
        print(f"Game started: {self.game_started}")
        print(f"Game over: {self.game_over}")
        print(f"Winner: {self.winner}")
        print(f"Players alive: {self.players_alive}")
        print(f"Player lives: {self.player_lives}")
        print(f"Ball position: ({self.ball.x}, {self.ball.y})")
        print(f"Ball direction: ({self.ball.dx}, {self.ball.dy})")
        print(f"Ball speed: {self.ball.base_speed * self.ball.hit_boost * self.ball.speed_multiplier}")
        print("--- END DEBUG ---\n")

# Fix the run_pong function to prevent random winners
def run_pong(screen=None, player_count=4, external_events=None):
    print("Starting Pong game")
    game = PongGame(screen, external_events)
    
    # Pass player_count to initialize
    if not game.initialize(player_count):
        print("Failed to initialize Pong game")
        return -1
    
    # Disable start text and start immediately (no countdown)
    game.show_start_text = False
    game.game_started = True
    game.ball.game_started = True
    
    running = True
    winner = -1
    frame_count = 0
    min_game_time = 600  # Ensure game runs at least 10 seconds

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        frame_count += 1
        
        result = game.run_frame()
        if result is False:
            running = False
        elif isinstance(result, int) and result >= 0:
            winner = result
            print(f"Player {winner + 1} won the game")
            running = False
        
        alive_players = [i for i, alive in enumerate(game.players_alive) if alive]
        if len(alive_players) == 1:
            winner = alive_players[0]
            print(f"Player {winner + 1} is the last one standing!")
            running = False
        
        if frame_count > 36000:  # timeout after 10 minutes
            print("Game timed out")
            alive_players = [(i, game.player_lives[i]) for i, alive in enumerate(game.players_alive) if alive]
            if not alive_players:
                winner = 0
            else:
                max_lives = max([lives for i, lives in alive_players])
                import random
                candidates = [i for i, lives in alive_players if lives == max_lives]
                winner = random.choice(candidates)
                print(f"Player {winner + 1} wins with {max_lives} lives remaining!")
            running = False
        
        pygame.display.flip()
        pygame.time.delay(16)
    
    return winner

# Rename the original function if it exists (if needed)
# Only do this if you had a previous run_pong implementation that didn't accept the new parameters
try:
    run_pong_original = run_pong
except NameError:
    # No previous implementation
    pass