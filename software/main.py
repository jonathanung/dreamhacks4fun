# main.py - Simplified version
import pygame
import sys
import time
import os
import traceback

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

# Define player colors for UI consistency
PLAYER_COLORS = [
    (255, 50, 50),    # Red (Player 1 - Top)
    (50, 255, 50),    # Green (Player 2 - Right)
    (50, 50, 255),    # Blue (Player 3 - Bottom)
    (255, 255, 50)    # Yellow (Player 4 - Left)
]

def draw_win_stats(screen, player_wins, font, center_x, y_pos):
    """Draw player win statistics on the menu screen"""
    # Draw heading
    heading = font.render("Player Wins This Session:", True, (200, 200, 200))
    screen.blit(heading, (center_x - heading.get_width() // 2, y_pos))
    
    # Draw individual player stats
    for i, wins in enumerate(player_wins):
        color = PLAYER_COLORS[i] if i < len(PLAYER_COLORS) else (200, 200, 200)
        text = font.render(f"Player {i+1}: {wins} wins", True, color)
        screen.blit(text, (center_x - text.get_width() // 2, y_pos + 40 + i * 30))

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
    
    # Set up fullscreen display
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("My Multi-Minigame Project")
    clock = pygame.time.Clock()
    
    # Menu state
    menu_selected = 0
    menu_options = [("Pong", "pong"), ("Minigame 2", "minigame2"), ("Quit", "quit")]
    
    # Game settings
    player_count = 4 # Set to 4 by default
    
    # Player win tracking
    player_wins = [0, 0, 0, 0]  # Tracks wins for each player
    
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
    state = "menu"  # Possible states: "menu", "pong", "minigame2"
    
    try:
        while running:
            # Handle events based on current state
            if state == "menu":
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
                                state = "pong"
                            elif selected_option == "minigame2":
                                state = "minigame2"
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
                                        state = "pong"
                                    elif selected_option == "minigame2":
                                        state = "minigame2"
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
                
                # Update win count if there was a winner
                if winner >= 0 and winner < len(player_wins):
                    player_wins[winner] += 1
                    print(f"Player {winner + 1} won! Total wins: {player_wins[winner]}")
                
                state = "menu"  # Return to menu after the game finishes
            
            elif state == "minigame2":
                # Placeholder for minigame2
                print("Minigame 2 not implemented yet")
                state = "menu"  # Return to menu
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
    
    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
    
    finally:
        # Clean up
        if controller:
            controller.stop()
        pygame.quit()
        sys.exit()

# Run the main function
if __name__ == '__main__':
    main()
