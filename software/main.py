# main.py
import pygame
import sys
from event_controller import EventController
from menu import show_menu
from minigame1 import run_minigame1
from minigame2 import run_minigame2

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Multi-Minigame Project")
clock = pygame.time.Clock()

def main():
    running = True
    state = "menu"  # Possible states: "menu", "minigame1", "minigame2"
    
    # Initialize event controller
    controller = EventController()
    controller.start()

    try:
        while running:
            # Process external events
            external_events = controller.get_events()
            
            # Handle state transitions based on external events
            for event in external_events:
                if event.get('action') == 'quit':
                    running = False
                elif event.get('action') == 'goto_menu':
                    state = "menu"
                elif event.get('action') == 'goto_minigame1':
                    state = "minigame1"
                elif event.get('action') == 'goto_minigame2':
                    state = "minigame2"
            
            if state == "menu":
                # Pass the controller's events to the menu
                selected_game = show_menu(screen, external_events)
                if selected_game == "minigame1":
                    state = "minigame1"
                elif selected_game == "minigame2":
                    state = "minigame2"
                elif selected_game == "quit":
                    running = False

            elif state == "minigame1":
                # Pass the controller's events to minigame1
                run_minigame1(screen, external_events)
                state = "menu"  # Return to menu after the game finishes

            elif state == "minigame2":
                # Pass the controller's events to minigame2
                run_minigame2(screen, external_events)
                state = "menu"  # Return to menu after the game finishes

            pygame.display.flip()
            clock.tick(120)
    finally:
        # Make sure to stop the controller when exiting
        controller.stop()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()
