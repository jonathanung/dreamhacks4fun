import pygame
import random
import time
import math
import os
import sys

# Constants
GAME_DURATION = 30  # game lasts 30 seconds
STAR_SPAWN_RATE = 1.0  # stars spawn every second
POKEMON_SPEED = 8  # speed of pokemon movement
BULLET_SPEED = 15  # speed of bullets moving right
STAR_SPEED = 4  # increased star speed (was 2)
COUNTDOWN_DURATION = 5  # countdown before game starts

# Sizes
POKEMON_SIZE = 64  # increased Pokémon size (was implicitly 40)
STAR_SIZE = 50  # increased star size (was 30)
BULLET_SIZE = 12  # increased bullet size (was 8)

# Player colors (match the colors in main.py)
PLAYER_COLORS = [
    (255, 50, 50),    # Red (Player 1)
    (50, 255, 50),    # Green (Player 2)
    (50, 50, 255),    # Blue (Player 3)
    (255, 255, 50)    # Yellow (Player 4)
]

# Pokemon names for each player
POKEMON_NAMES = [
    "pikachu",        # Player 1
    "bulbasaur",      # Player 2
    "charmander",     # Player 3
    "squirtle"        # Player 4
]

class Star:
    def __init__(self, x, y, size=STAR_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.active = True
        # Random angle and speed for movement
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.8, 1.8) * STAR_SPEED  # Slightly increased speed variation
        # Keep track of velocity components for bouncing
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        
    def update(self, width, height):
        # Move the star using velocity components
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls
        radius = self.size // 2
        # Left and right walls
        if self.x - radius <= 0:
            self.x = radius  # Prevent getting stuck in wall
            self.vx = abs(self.vx)  # Reverse x direction (make positive)
        elif self.x + radius >= width:
            self.x = width - radius  # Prevent getting stuck in wall
            self.vx = -abs(self.vx)  # Reverse x direction (make negative)
            
        # Top and bottom walls
        if self.y - radius <= 0:
            self.y = radius  # Prevent getting stuck in wall
            self.vy = abs(self.vy)  # Reverse y direction (make positive)
        elif self.y + radius >= height:
            self.y = height - radius  # Prevent getting stuck in wall
            self.vy = -abs(self.vy)  # Reverse y direction (make negative)
        
        # Occasionally change direction slightly
        if random.random() < 0.01:  # 1% chance per frame
            # Add small random changes to velocity
            self.vx += random.uniform(-0.2, 0.2)
            self.vy += random.uniform(-0.2, 0.2)
            
            # Normalize speed to maintain consistent velocity
            current_speed = math.sqrt(self.vx**2 + self.vy**2)
            if current_speed > 0:  # Avoid division by zero
                self.vx = (self.vx / current_speed) * self.speed
                self.vy = (self.vy / current_speed) * self.speed
        
    def draw(self, screen, star_img):
        if self.active:
            # Calculate position to center the image
            pos_x = self.x - self.size // 2
            pos_y = self.y - self.size // 2
            screen.blit(star_img, (pos_x, pos_y))
            
            # Debug: Draw collision circle
            # pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.size // 2, 1)
            
    def is_hit(self, bullet_x, bullet_y):
        # Check if bullet hits star (simple circle collision)
        distance = math.sqrt((bullet_x - self.x)**2 + (bullet_y - self.y)**2)
        return distance < self.size // 2 and self.active
        
    def is_out_of_bounds(self, width, height):
        # Check if star is out of screen bounds
        # Note: This is no longer used since stars now bounce off walls
        return (self.x < -self.size or self.x > width + self.size or
                self.y < -self.size or self.y > height + self.size)

class Bullet:
    def __init__(self, x, y, player_id):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.active = True
        self.player_id = player_id
        self.size = BULLET_SIZE  # Larger bullets using the constant
        
    def update(self):
        # Bullets now move rightward
        self.x += self.speed
        
    def draw(self, screen):
        if self.active:
            color = PLAYER_COLORS[self.player_id]
            # Draw a pokeball-like bullet
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size // 2)
            
    def is_out_of_bounds(self, width, height):
        # Check if bullet is out of screen bounds
        return self.x < 0 or self.x > width

class Pokemon:
    def __init__(self, x, y, player_id, size=POKEMON_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.player_id = player_id
        self.color = PLAYER_COLORS[player_id]
        self.pokemon_name = POKEMON_NAMES[player_id if player_id < len(POKEMON_NAMES) else 0]
        self.score = 0
        self.image = None  # Will be loaded later
        
    def move(self, direction, screen_height):
        # Move up or down within screen bounds
        new_y = self.y + direction * POKEMON_SPEED
        if 50 <= new_y <= screen_height - 50:
            self.y = new_y
            
    def draw(self, screen):
        if self.image:
            # Draw the Pokemon image
            screen.blit(self.image, (self.x - self.size // 2, self.y - self.size // 2))
            
            # Debug: Draw collision box
            # pygame.draw.rect(screen, (255, 0, 0), 
            #                 (self.x - self.size // 2, self.y - self.size // 2, 
            #                  self.size, self.size), 1)
        else:
            # Fallback if image not loaded
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
            
        # Draw a score indicator next to the Pokemon
        font = pygame.font.Font(None, 30)  # Slightly bigger score text
        score_text = f"{self.score}"
        score_render = font.render(score_text, True, self.color)
        screen.blit(score_render, (self.x - 40, self.y - self.size // 2))

def draw_win_screen(screen, winner, pokemon_shooters, pokemon_images, width, height, font, big_font):
    """Draw a dedicated win screen showing the winner's Pokémon"""
    # Create semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Black with 200/255 alpha
    screen.blit(overlay, (0, 0))
    
    # Get center coordinates
    center_x = width // 2
    center_y = height // 2
    
    # Draw winner title
    if winner == -1:
        title_text = big_font.render("It's a tie!", True, (255, 255, 255))
    else:
        title_text = big_font.render(f"Player {winner + 1} Wins!", True, PLAYER_COLORS[winner])
    
    screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 200))
    
    # Draw winner's Pokémon (larger size)
    if winner != -1 and winner < len(pokemon_shooters):
        pokemon_name = POKEMON_NAMES[winner]
        pokemon_sprite = pokemon_images[pokemon_name]
        if pokemon_sprite:
            # Create a large sprite for display
            display_size = int(min(width, height) * 0.3)  # 30% of screen size
            scaled_sprite = pygame.transform.scale(pokemon_sprite, (display_size, display_size))
            
            # Draw centered sprite
            sprite_x = center_x - display_size // 2
            sprite_y = center_y - display_size // 2
            screen.blit(scaled_sprite, (sprite_x, sprite_y))
    
    # Show final scores
    scores_y = center_y + (50 if winner == -1 else 150)  # Adjust position based on whether there's a winner
    scores_text = "Final Scores:"
    scores_render = font.render(scores_text, True, (255, 255, 255))
    screen.blit(scores_render, (center_x - scores_render.get_width() // 2, scores_y))
    
    for i, pokemon in enumerate(pokemon_shooters):
        p_score_text = f"Player {i+1}: {pokemon.score}"
        p_score_render = font.render(p_score_text, True, pokemon.color)
        screen.blit(p_score_render, (center_x - p_score_render.get_width() // 2, scores_y + 40 + (i * 30)))
    
    # Draw continue instructions
    instructions_text = font.render("Press any key to continue", True, (255, 255, 255))
    screen.blit(instructions_text, 
                (center_x - instructions_text.get_width() // 2, height - 100))

def run_shooting_stars(screen, player_count, external_events=None):
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()
    
    # Initialize pygame mixer for sound if not already initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Screen dimensions
    width, height = screen.get_size()
    center_x, center_y = width // 2, height // 2
    
    # Load sounds
    try:
        # Get current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load background music
        bg_music_path = os.path.join(current_dir, "shooting-stars.mp3")
        pygame.mixer.music.load(bg_music_path)
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # Loop indefinitely (-1)
        
        # Load win sound
        win_sound_path = os.path.join(current_dir, "win-sound.mp3")
        win_sound = pygame.mixer.Sound(win_sound_path)
        win_sound.set_volume(0.7)  # Set volume to 70%
    except Exception as e:
        print(f"Error loading sounds: {e}")
        win_sound = None
    
    # Load images
    try:
        # Get current script directory (already defined above)
        star_img_path = os.path.join(current_dir, "star.jpg")
        bg_img_path = os.path.join(current_dir, "nightsky.jpg")
        
        # Load and scale images
        star_img = pygame.image.load(star_img_path)
        star_img = pygame.transform.scale(star_img, (STAR_SIZE, STAR_SIZE))
        
        bg_img = pygame.image.load(bg_img_path)
        bg_img = pygame.transform.scale(bg_img, (width, height))
        
        # Load Pokemon images
        pokemon_images = {}
        for pokemon in POKEMON_NAMES:
            try:
                pokemon_path = os.path.join(current_dir, f"{pokemon}.png")
                pokemon_img = pygame.image.load(pokemon_path)
                pokemon_img = pygame.transform.scale(pokemon_img, (POKEMON_SIZE, POKEMON_SIZE))
                pokemon_images[pokemon] = pokemon_img
            except Exception as e:
                print(f"Could not load {pokemon} image: {e}")
                
    except Exception as e:
        print(f"Error loading images: {e}")
        # Create fallback images if loading fails
        star_img = pygame.Surface((STAR_SIZE, STAR_SIZE))
        star_img.fill((255, 255, 0))
        
        bg_img = pygame.Surface((width, height))
        bg_img.fill((0, 0, 30))
        
        pokemon_images = {}
    
    # Font for score display
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    
    # Game variables
    clock = pygame.time.Clock()
    running = True
    game_started = False
    game_over = False
    start_time = time.time()
    last_spawn_time = 0
    winner = -1
    
    # Flag to track if win sound has been played
    win_sound_played = False
    
    # Initialize Pokemon for each player - on left side of screen
    pokemon_shooters = []
    left_side_x = 100  # Position on left side
    
    for i in range(player_count):
        # Position Pokemon at different heights based on player number
        spacing = height / (player_count + 1)
        pokemon_y = spacing * (i + 1)
        pokemon = Pokemon(left_side_x, pokemon_y, i)
        
        # Set the image if available
        if pokemon.pokemon_name in pokemon_images:
            pokemon.image = pokemon_images[pokemon.pokemon_name]
            
        pokemon_shooters.append(pokemon)
    
    # Game objects
    stars = []
    bullets = []
    
    # Input state
    key_pressed = {}  # Track currently pressed keys
    key_held = {}     # Track keys being held down
    
    # Countdown variables
    countdown_start = time.time()
    countdown_done = False
    
    # Main game loop
    while running:
        # Process pygame events for local play
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()  # Stop music when exiting
                return -1
            elif event.type == pygame.KEYDOWN:
                key_pressed[event.key] = True
                key_held[event.key] = True
                
                # Check for escape key to quit
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.mixer.music.stop()  # Stop music when exiting
                    return -1
            elif event.type == pygame.KEYUP:
                key_held[event.key] = False
                key_pressed[event.key] = False  # Remove from pressed keys
        
        # Process external events if controller is present
        if external_events is not None:
            for event in external_events:
                if isinstance(event, dict):  # Ensure it's a dictionary
                    if event.get('type') == 'QUIT':
                        running = False
                        pygame.mixer.music.stop()  # Stop music when exiting
                        return -1
                    elif event.get('type') == 'KEYDOWN':
                        key = event.get('key')
                        if key:
                            key_pressed[key] = True
                            key_held[key] = True
                            
                            # Also check for escape
                            if key == pygame.K_ESCAPE:
                                running = False
                                pygame.mixer.music.stop()  # Stop music when exiting
                                return -1
                    elif event.get('type') == 'KEYUP':
                        key = event.get('key')
                        if key:
                            key_held[key] = False
                            key_pressed[key] = False
                    # Handle controller actions
                    elif 'action' in event:
                        action = event.get('action')
                        player_id = event.get('player_id', 0)  # Default to player 1 if not specified
                        
                        # Ensure player_id is within valid range
                        if player_id >= 0 and player_id < player_count:
                            if action == 'up':
                                # Move the player's Pokemon up
                                pokemon_shooters[player_id].move(-1, height)
                                print(f"Player {player_id + 1} moving up via controller")
                            elif action == 'down':
                                # Move the player's Pokemon down
                                pokemon_shooters[player_id].move(1, height)
                                print(f"Player {player_id + 1} moving down via controller")
                            elif action == 'shoot' or action == 'select':
                                # Fire a bullet
                                bullets.append(Bullet(pokemon_shooters[player_id].x + pokemon_shooters[player_id].size // 2, 
                                                     pokemon_shooters[player_id].y, player_id))
                                print(f"Player {player_id + 1} fired via controller")
        
        # Check countdown
        current_time = time.time()
        if not countdown_done:
            if current_time - countdown_start >= COUNTDOWN_DURATION:
                countdown_done = True
                game_started = True
                start_time = current_time
            
            # Allow exiting during countdown with escape key or controller
            if key_pressed.get(pygame.K_ESCAPE, False):
                running = False
                pygame.mixer.music.stop()  # Stop music when exiting
                return -1
                
            # Check for exit via middleware during countdown
            if external_events:
                try:
                    middleware_events = []
                    if callable(external_events):
                        middleware_events = external_events()
                    elif hasattr(external_events, 'get_events') and callable(external_events.get_events):
                        middleware_events = external_events.get_events()
                    elif isinstance(external_events, list):
                        middleware_events = external_events
                        
                    for event in middleware_events:
                        if isinstance(event, dict):
                            # Check for escape action
                            if event.get('action') == 'escape' or event.get('action') == 'quit':
                                running = False
                                pygame.mixer.music.stop()
                                return -1
                            # Check for any action that should exit the win screen
                            elif (event.get('action') == 'select' or 
                                 event.get('action') == 'shoot' or
                                 event.get('action') == 'hit' or
                                 event.get('action') == 'up' or
                                 event.get('action') == 'down' or
                                 event.get('type') == pygame.KEYDOWN):
                                print(f"Win screen: Detected middleware event to exit: {event}")
                                any_key_pressed = True
                                break
                except Exception as e:
                    print(f"Error processing middleware events during countdown: {e}")
        
        # Process input for each player
        if game_started and not game_over:
            # Player 1 controls (arrows) - now UP/DOWN
            if player_count >= 1:
                if key_held.get(pygame.K_UP, False):
                    pokemon_shooters[0].move(-1, height)
                    print("Player 1 moving up")
                if key_held.get(pygame.K_DOWN, False):
                    pokemon_shooters[0].move(1, height)
                    print("Player 1 moving down")
                if key_pressed.get(pygame.K_RIGHT, False):
                    bullets.append(Bullet(pokemon_shooters[0].x + pokemon_shooters[0].size // 2, pokemon_shooters[0].y, 0))
                    print("Player 1 fired")
                    key_pressed[pygame.K_RIGHT] = False  # Consume the press
            
            # Player 2 controls (WASD) - now W/S
            if player_count >= 2:
                if key_held.get(pygame.K_w, False):
                    pokemon_shooters[1].move(-1, height)
                    print("Player 2 moving up")
                if key_held.get(pygame.K_s, False):
                    pokemon_shooters[1].move(1, height)
                    print("Player 2 moving down")
                if key_pressed.get(pygame.K_d, False):
                    bullets.append(Bullet(pokemon_shooters[1].x + pokemon_shooters[1].size // 2, pokemon_shooters[1].y, 1))
                    print("Player 2 fired")
                    key_pressed[pygame.K_d] = False  # Consume the press
            
            # Player 3 controls (IJKL) - now I/K
            if player_count >= 3:
                if key_held.get(pygame.K_i, False):
                    pokemon_shooters[2].move(-1, height)
                    print("Player 3 moving up")
                if key_held.get(pygame.K_k, False):
                    pokemon_shooters[2].move(1, height)
                    print("Player 3 moving down")
                if key_pressed.get(pygame.K_l, False):
                    bullets.append(Bullet(pokemon_shooters[2].x + pokemon_shooters[2].size // 2, pokemon_shooters[2].y, 2))
                    print("Player 3 fired")
                    key_pressed[pygame.K_l] = False  # Consume the press
            
            # Player 4 controls (NUM pad) - now 8/5
            if player_count >= 4:
                if key_held.get(pygame.K_KP8, False):
                    pokemon_shooters[3].move(-1, height)
                    print("Player 4 moving up")
                if key_held.get(pygame.K_KP5, False):
                    pokemon_shooters[3].move(1, height)
                    print("Player 4 moving down")
                if key_pressed.get(pygame.K_KP6, False):
                    bullets.append(Bullet(pokemon_shooters[3].x + pokemon_shooters[3].size // 2, pokemon_shooters[3].y, 3))
                    print("Player 4 fired")
                    key_pressed[pygame.K_KP6] = False  # Consume the press
        
        # Spawn stars randomly across right 2/3 of screen
        if game_started and not game_over:
            if current_time - last_spawn_time >= STAR_SPAWN_RATE:
                # Spawn star at random positions, mainly on right side
                star_x = random.randint(width // 3, width - 50)
                star_y = random.randint(50, height - 50)
                stars.append(Star(star_x, star_y))
                last_spawn_time = current_time
        
        # Update game objects
        for star in stars[:]:
            star.update(width, height)  # Pass width and height for bouncing off walls
                
        for bullet in bullets[:]:
            bullet.update()
            # Check collision with stars
            hit_detected = False
            for star in stars[:]:
                if star.is_hit(bullet.x, bullet.y):
                    pokemon_shooters[bullet.player_id].score += 1
                    print(f"Player {bullet.player_id + 1} hit a star! Score: {pokemon_shooters[bullet.player_id].score}")
                    stars.remove(star)
                    hit_detected = True
                    break
            
            if hit_detected:
                bullets.remove(bullet)
            elif bullet.is_out_of_bounds(width, height):
                bullets.remove(bullet)
        
        # Check if game is over
        if game_started and not game_over:
            elapsed_time = current_time - start_time
            if elapsed_time >= GAME_DURATION:
                game_over = True
                show_win_screen = True
                # Fade out music over 2 seconds
                pygame.mixer.music.fadeout(2000)
                
                # Determine winner
                max_score = -1
                for i, pokemon in enumerate(pokemon_shooters):
                    if pokemon.score > max_score:
                        max_score = pokemon.score
                        winner = i
                
                # Check for tie
                tie = False
                for i, pokemon in enumerate(pokemon_shooters):
                    if i != winner and pokemon.score == max_score:
                        tie = True
                
                if tie:
                    winner = -1  # No winner on tie
                    
                print(f"Game over! Winner: {winner if winner != -1 else 'Tie'}")
        
        # Draw everything
        # Draw background
        screen.blit(bg_img, (0, 0))
        
        # If we're showing the win screen, draw it and skip the regular game drawing
        if game_over and show_win_screen:
            draw_win_screen(screen, winner, pokemon_shooters, pokemon_images, width, height, font, big_font)
            
            # Play win sound if not already played
            if not win_sound_played and win_sound:
                win_sound.play()
                win_sound_played = True
            
            # Check for key press or external event to exit
            any_key_pressed = False
            for key in key_pressed:
                if key_pressed[key]:
                    any_key_pressed = True
                    break
                    
            # Check for middleware events if available
            if external_events:
                try:
                    middleware_events = []
                    if callable(external_events):
                        middleware_events = external_events()
                    elif hasattr(external_events, 'get_events') and callable(external_events.get_events):
                        middleware_events = external_events.get_events()
                    elif isinstance(external_events, list):
                        middleware_events = external_events
                        
                    for event in middleware_events:
                        if isinstance(event, dict):
                            # Check for escape action
                            if event.get('action') == 'escape' or event.get('action') == 'quit':
                                running = False
                                pygame.mixer.music.stop()
                                return -1
                            # Check for any action that should exit the win screen
                            elif (event.get('action') == 'select' or 
                                 event.get('action') == 'shoot' or
                                 event.get('action') == 'hit' or
                                 event.get('action') == 'up' or
                                 event.get('action') == 'down' or
                                 event.get('type') == pygame.KEYDOWN):
                                print(f"Win screen: Detected middleware event to exit: {event}")
                                any_key_pressed = True
                                break
                except Exception as e:
                    print(f"Error processing middleware events: {e}")
                    
            if any_key_pressed:
                # Make sure win sound stops playing when exiting
                pygame.mixer.stop()
                running = False
        else:
            # Draw regular game elements
            # Draw game objects
            for star in stars:
                star.draw(screen, star_img)
                
            for bullet in bullets:
                bullet.draw(screen)
                
            for pokemon in pokemon_shooters:
                pokemon.draw(screen)
            
            # Draw countdown or timer
            if not countdown_done:
                countdown_value = max(1, int(COUNTDOWN_DURATION - (current_time - countdown_start) + 1))
                if countdown_value == COUNTDOWN_DURATION:
                    countdown_text = "Get ready!"
                else:
                    countdown_text = str(countdown_value)
                countdown_render = big_font.render(countdown_text, True, (255, 255, 255))
                screen.blit(countdown_render, (center_x - countdown_render.get_width() // 2, center_y - 150))
            elif game_started and not game_over:
                # Show remaining time
                remaining_time = max(0, int(GAME_DURATION - (current_time - start_time)))
                time_text = f"Time: {remaining_time}s"
                time_render = font.render(time_text, True, (255, 255, 255))
                screen.blit(time_render, (width - time_render.get_width() - 20, 20))
            
            # Draw scores at the top
            score_y = 20
            score_text = "Scores:"
            score_render = font.render(score_text, True, (255, 255, 255))
            screen.blit(score_render, (center_x - score_render.get_width() // 2, score_y))
            
            # Draw instructions
            controls_y = height - 80
            if player_count >= 1:
                p1_text = "P1: ↑/↓ to move, → to shoot"
                p1_render = font.render(p1_text, True, PLAYER_COLORS[0])
                screen.blit(p1_render, (20, controls_y))
                
            if player_count >= 2:
                p2_text = "P2: W/S to move, D to shoot"
                p2_render = font.render(p2_text, True, PLAYER_COLORS[1])
                screen.blit(p2_render, (20, controls_y + 25))
                
            # Draw "Press ESC to quit" text
            quit_text = font.render("Press ESC to quit", True, (200, 200, 200))
            screen.blit(quit_text, (center_x - quit_text.get_width() // 2, height - 40))
            
            # Debug text for key presses
            debug_y = height - 150
            if game_started and not game_over and False:  # Set to True to show debug info
                for i, player_keys in enumerate([
                    ["Up/Down/Right", key_held.get(pygame.K_UP, False), key_held.get(pygame.K_DOWN, False)],
                    ["W/S/D", key_held.get(pygame.K_w, False), key_held.get(pygame.K_s, False)],
                    ["I/K/L", key_held.get(pygame.K_i, False), key_held.get(pygame.K_k, False)],
                    ["Num8/Num5/Num6", key_held.get(pygame.K_KP8, False), key_held.get(pygame.K_KP5, False)]
                ]):
                    if i < player_count:
                        debug_text = f"P{i+1} keys: {player_keys[0]} [{player_keys[1]}/{player_keys[2]}]"
                        debug_render = font.render(debug_text, True, PLAYER_COLORS[i])
                        screen.blit(debug_render, (width - 300, debug_y + i * 25))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Stop music before exiting
    pygame.mixer.music.stop()
    
    return winner

if __name__ == "__main__":
    # Test the game independently
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pokémon Star Shooters")
    run_shooting_stars(screen, 2)
    pygame.quit() 