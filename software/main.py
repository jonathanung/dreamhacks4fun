# main.py - Simplified version
import pygame
import sys
import time
import os
import traceback
import random
import json

# Try to import event controller
try:
    from event_controller import EventController
except ImportError:
    print("Warning: Could not import EventController")
    EventController = None

# Try to import pong game
try:
    from pong import run_pong
except ImportError:
    print("Warning: Could not import run_pong")
    def run_pong(screen, player_count, events):
        print("Pong game not available")
        return -1

# Try to import shooting stars game
try:
    from shooting_stars import run_shooting_stars
except ImportError:
    print("Warning: Could not import run_shooting_stars")
    def run_shooting_stars(screen, player_count, external_events):
        print("Shooting Stars game not available")
        return -1

# Define player colors for UI consistency
PLAYER_COLORS = [
    (255, 50, 50),    # Red (Player 1 - Top)
    (50, 255, 50),    # Green (Player 2 - Right)
    (50, 50, 255),    # Blue (Player 3 - Bottom)
    (255, 255, 50)    # Yellow (Player 4 - Left)
]

# Load and save player win statistics
def load_win_stats():
    try:
        with open('win_stats.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize empty win stats
        return {"Player 1": 0, "Player 2": 0, "Player 3": 0, "Player 4": 0}

def save_win_stats(stats):
    with open('win_stats.json', 'w') as f:
        json.dump(stats, f)

def draw_win_stats(screen, stats, font, center_x, y_pos):
    """Draw player win statistics on the menu screen"""
    # Draw heading
    heading = font.render("Player Win Statistics:", True, (255, 255, 255))
    screen.blit(heading, (center_x - heading.get_width() // 2, y_pos))
    
    # Draw individual player stats
    y_offset = 40
    for i, player in enumerate(["Player 1", "Player 2", "Player 3", "Player 4"]):
        color = PLAYER_COLORS[i]
        text = f"{player}: {stats[player]}"
        render = font.render(text, True, color)
        screen.blit(render, (center_x - render.get_width() // 2, y_pos + y_offset))
        y_offset += 30

def draw_menu(screen, player_count):
    # ... existing menu drawing code ...
    
    # Add player count display
    font = pygame.font.Font(None, 36)
    player_text = font.render(f"Player Count: {player_count}", True, (255, 255, 255))
    player_rect = player_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 100))
    screen.blit(player_text, player_rect)
    
    # Add player count controls
    controls_text = font.render("Press 2, 3, or 4 to set player count", True, (200, 200, 200))
    controls_rect = controls_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))
    screen.blit(controls_text, controls_rect)
    
    # ... rest of menu drawing code ...

def main():
    # Initialize pygame
    pygame.init()
    
    # Initialize mixer for audio
    pygame.mixer.init()
    
    # Set up fullscreen display
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("My Multi-Minigame Project")
    clock = pygame.time.Clock()
    
    # Menu state
    menu_selected = 0
    menu_options = [("Pong", "pong"), ("Shooting Stars", "shooting_stars"), ("Quit", "quit")]
    
    # Game settings
    player_count = 4 # Set to 4 by default
    
    # Player win tracking
    player_wins = load_win_stats()
    
    # Initialize event controller
    controller = None
    if EventController is not None:
        try:
            controller = EventController()
            controller.start()
            print("Event controller started and listening on port 5555")
        except Exception as e:
            print(f"Error starting event controller: {e}")
    
    # Fonts
    title_font = pygame.font.Font(None, 100)
    menu_font = pygame.font.Font(None, 74)
    info_font = pygame.font.Font(None, 36)
    
    # For debouncing external events
    last_event_time = 0
    event_cooldown = 0.2  # seconds
    
    # Game state
    running = True
    state = "menu"  # Possible states: "menu", "pong", "shooting_stars"
    
    # Load sound files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    win_sound = None
    try:
        # Load main menu music
        menu_music_path = os.path.join(current_dir, "main-menu.mp3")
        win_sound_path = os.path.join(current_dir, "win-sound.mp3")
        
        # Load and play menu music
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.set_volume(0.4)  # Set volume to 40%
        pygame.mixer.music.play(-1)  # Loop indefinitely
        
        # Load win sound effect
        win_sound = pygame.mixer.Sound(win_sound_path)
        win_sound.set_volume(0.7)  # Set volume to 70%
    except Exception as e:
        print(f"Error loading sound files: {e}")
    
    try:
        while running:
            # Handle events based on current state
            if state == "menu":
                # Ensure menu music is playing
                if not pygame.mixer.music.get_busy():
                    try:
                        pygame.mixer.music.load(menu_music_path)
                        pygame.mixer.music.play(-1)
                    except Exception as e:
                        print(f"Error playing menu music: {e}")
                
                # Fill background
                screen.fill((30, 30, 30))
                
                # Process pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_UP:
                            menu_selected = (menu_selected - 1) % len(menu_options)
                        elif event.key == pygame.K_DOWN:
                            menu_selected = (menu_selected + 1) % len(menu_options)
                        elif event.key == pygame.K_RETURN:
                            selected_option = menu_options[menu_selected][1]
                            if selected_option == "pong":
                                # Stop menu music before starting the game
                                pygame.mixer.music.stop()
                                state = "pong"
                            elif selected_option == "shooting_stars":
                                # Stop menu music before starting the game
                                pygame.mixer.music.stop()
                                state = "shooting_stars"
                            elif selected_option == "quit":
                                running = False
                        elif event.key == pygame.K_2:
                            player_count = 2
                        elif event.key == pygame.K_3:
                            player_count = 3
                        elif event.key == pygame.K_4:
                            player_count = 4
                
                # Process external events with debouncing if controller exists
                if controller:
                    try:
                        external_events = controller.get_events()
                        current_time = time.time()
                        
                        if external_events and current_time - last_event_time > event_cooldown:
                            last_event_time = current_time
                            print(f"Processing external events: {external_events}")
                            
                            for event in external_events:
                                action = event.get('action')
                                if action == 'up':
                                    menu_selected = (menu_selected - 1) % len(menu_options)
                                    print(f"Menu selection moved up to {menu_selected}")
                                elif action == 'down':
                                    menu_selected = (menu_selected + 1) % len(menu_options)
                                    print(f"Menu selection moved down to {menu_selected}")
                                elif action == 'select':
                                    selected_option = menu_options[menu_selected][1]
                                    print(f"Selected option: {selected_option}")
                                    if selected_option == "pong":
                                        # Stop menu music before starting the game
                                        pygame.mixer.music.stop()
                                        state = "pong"
                                    elif selected_option == "shooting_stars":
                                        # Stop menu music before starting the game
                                        pygame.mixer.music.stop()
                                        state = "shooting_stars"
                                    elif selected_option == "quit":
                                        running = False
                    except Exception as e:
                        print(f"Error processing external events: {e}")
                
                # Draw menu
                screen_width, screen_height = screen.get_size()
                center_x = screen_width // 2
                center_y = screen_height // 2
                
                # Draw title
                title_text = title_font.render("Mini-Games", True, (255, 255, 255))
                screen.blit(title_text, (center_x - title_text.get_width() // 2, 50))
                
                # Draw menu options
                menu_y_start = center_y - 150
                for idx, (text, _) in enumerate(menu_options):
                    color = (255, 0, 0) if idx == menu_selected else (255, 255, 255)
                    label = menu_font.render(text, True, color)
                    screen.blit(label, (center_x - label.get_width() // 2, 
                                      menu_y_start + idx * 100))
                
                # Draw player win stats
                win_stats_y = center_y + 150
                draw_win_stats(screen, player_wins, info_font, center_x, win_stats_y)
                
                # Add player count display
                player_text = info_font.render(f"Player Count: {player_count}", True, (255, 255, 255))
                player_rect = player_text.get_rect(center=(screen_width // 2, screen_height - 100))
                screen.blit(player_text, player_rect)
                
                # Add player count controls
                controls_text = info_font.render("Press 2, 3, or 4 to set player count", True, (200, 200, 200))
                controls_rect = controls_text.get_rect(center=(screen_width // 2, screen_height - 60))
                screen.blit(controls_text, controls_rect)
            
            elif state == "pong":
                print("Starting Pong game...")
                # Run pong with specified player count and get the winner
                winner = run_pong(screen, player_count, controller.get_events() if controller else None)
                print(f"Pong game returned result: {winner}")
                
                # Update win count ONLY if there was a valid winner (>= 0)
                if isinstance(winner, int) and winner >= 0:
                    player = f"Player {winner + 1}"
                    player_wins[player] += 1
                    print(f"{player} won! Total wins: {player_wins[player]}")
                    
                    # Only play win sound if it wasn't already played in the game
                    if win_sound and not pygame.mixer.get_busy():
                        win_sound.play()
                        # Wait for sound to finish (or set a timer)
                        pygame.time.delay(1000)  # Wait 1 second
                        pygame.mixer.stop()  # Stop all sounds
                else:
                    print("Pong game ended without a winner")
                
                # Force a small delay before returning to menu to let any sounds finish
                pygame.time.delay(500)
                state = "menu"  # Return to menu after the game finishes
            
            elif state == "shooting_stars":
                # Run the Shooting Stars game
                winner = run_shooting_stars(screen, player_count, controller.get_events() if controller else None)
                # Update win stats
                if winner != -1:
                    player = f"Player {winner + 1}"
                    player_wins[player] += 1
                    
                    # Play win sound if available and not already played in the game
                    if win_sound and winner >= 0:
                        win_sound.play()
                        # Wait briefly for sound to start then stop it
                        pygame.time.delay(1000)  # Wait 1 second
                        pygame.mixer.stop()  # Stop all sounds
                
                # Force a small delay before returning to menu
                pygame.time.delay(500)
                state = "menu"  # Return to menu after the game finishes
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
    
    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
    
    finally:
        # Clean up and save wins
        save_win_stats(player_wins)
        
        # Stop all sounds
        pygame.mixer.music.stop()
        
        # Cleanup event controller if it was initialized
        if controller:
            controller.stop()
        pygame.quit()
        sys.exit()

# Run the main function
if __name__ == '__main__':
    main()
