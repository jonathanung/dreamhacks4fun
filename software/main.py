# main.py
import pygame
import sys
import time
from event_controller import EventController
from minigame1 import run_minigame1
from minigame2 import run_minigame2

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Multi-Minigame Project")
clock = pygame.time.Clock()

# Menu state
menu_selected = 0
menu_options = [("Minigame 1", "minigame1"), ("Minigame 2", "minigame2"), ("Quit", "quit")]

def main():
    global menu_selected, menu_options
    
    running = True
    state = "menu"  # Possible states: "menu", "minigame1", "minigame2"
    
    # Initialize event controller
    controller = EventController()
    controller.start()
    print("Event controller started and listening on port 5555")
    
    # Font for menu
    font = pygame.font.Font(None, 74)
    
    # For debouncing external events
    last_event_time = 0
    event_cooldown = 0.2  # seconds

    try:
        while running:
            # Handle events based on current state
            if state == "menu":
                # Process pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            menu_selected = (menu_selected - 1) % len(menu_options)
                        elif event.key == pygame.K_DOWN:
                            menu_selected = (menu_selected + 1) % len(menu_options)
                        elif event.key == pygame.K_RETURN:
                            selected_option = menu_options[menu_selected][1]
                            if selected_option == "minigame1":
                                state = "minigame1"
                            elif selected_option == "minigame2":
                                state = "minigame2"
                            elif selected_option == "quit":
                                running = False
                
                # Process external events with debouncing
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
                            if selected_option == "minigame1":
                                state = "minigame1"
                            elif selected_option == "minigame2":
                                state = "minigame2"
                            elif selected_option == "quit":
                                running = False
                
                # Draw menu
                screen.fill((30, 30, 30))
                for idx, (text, _) in enumerate(menu_options):
                    color = (255, 0, 0) if idx == menu_selected else (255, 255, 255)
                    label = font.render(text, True, color)
                    screen.blit(label, (100, 100 + idx * 100))
            
            elif state == "minigame1":
                # Run minigame1
                run_minigame1(screen)
                state = "menu"  # Return to menu after the game finishes
            
            elif state == "minigame2":
                # Run minigame2
                run_minigame2(screen)
                state = "menu"  # Return to menu after the game finishes
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
    
    finally:
        # Clean up
        controller.stop()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()
