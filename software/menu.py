# menu.py
import pygame

# Global menu state
_selected = 0
_menu_options = [("Minigame 1", "minigame1"), ("Minigame 2", "minigame2"), ("Quit", "quit")]

def show_menu(screen, external_events=None):
    global _selected, _menu_options
    
    font = pygame.font.Font(None, 74)
    
    # Process external events
    if external_events:
        for event in external_events:
            action = event.get('action')
            if action == 'up':
                _selected = (_selected - 1) % len(_menu_options)
            elif action == 'down':
                _selected = (_selected + 1) % len(_menu_options)
            elif action == 'select':
                return _menu_options[_selected][1]
    
    # Draw menu
    screen.fill((30, 30, 30))
    for idx, (text, _) in enumerate(_menu_options):
        color = (255, 0, 0) if idx == _selected else (255, 255, 255)
        label = font.render(text, True, color)
        screen.blit(label, (100, 100 + idx * 100))
    
    # Process pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                _selected = (_selected - 1) % len(_menu_options)
            elif event.key == pygame.K_DOWN:
                _selected = (_selected + 1) % len(_menu_options)
            elif event.key == pygame.K_RETURN:
                return _menu_options[_selected][1]
    
    # No selection made yet
    return None
