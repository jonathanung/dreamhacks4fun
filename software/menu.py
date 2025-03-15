# menu.py
import pygame

def show_menu(screen, external_events=None):
    font = pygame.font.Font(None, 74)
    menu_options = [("Minigame 1", "minigame1"), ("Minigame 2", "minigame2"), ("Quit", "quit")]
    selected = 0

    while True:
        screen.fill((30, 30, 30))
        for idx, (text, _) in enumerate(menu_options):
            color = (255, 0, 0) if idx == selected else (255, 255, 255)
            label = font.render(text, True, color)
            screen.blit(label, (100, 100 + idx * 100))

        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    return menu_options[selected][1]
        
        # Process external events
        if external_events:
            for event in external_events:
                if event.get('action') == 'up':
                    selected = (selected - 1) % len(menu_options)
                elif event.get('action') == 'down':
                    selected = (selected + 1) % len(menu_options)
                elif event.get('action') == 'select':
                    return menu_options[selected][1]

        pygame.display.flip()   
