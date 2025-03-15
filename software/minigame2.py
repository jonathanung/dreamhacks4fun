# minigame2.py
import pygame

def run_minigame2(screen):
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

        pygame.display.flip()
        clock.tick(60)
