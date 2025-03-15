# minigame1.py
import pygame

def run_minigame1(screen, external_events=None):
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 50)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Include game-specific event handling here

        screen.fill((0, 100, 200))
        text = font.render("Minigame 1 - Press ESC to return", True, (255, 255, 255))
        screen.blit(text, (50, 250))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # Add handling for external events
        if external_events:
            for event in external_events:
                # Handle specific events for this minigame
                if event.get('action') == 'jump':
                    # Implement jump action
                    pass
                elif event.get('action') == 'shoot':
                    # Implement shoot action
                    pass
                # Add more actions as needed

        pygame.display.flip()
        clock.tick(60)
