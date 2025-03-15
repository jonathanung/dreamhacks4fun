import pygame
import sys
import os
from pong import run_pong

def test_pong():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create a window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pong Test")
    
    # Run the Pong game
    print("Starting Pong test")
    result = run_pong(screen, 2, None)
    
    print(f"Game finished with result: {result}")
    
    # Wait for the user to close the window
    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_pong() 