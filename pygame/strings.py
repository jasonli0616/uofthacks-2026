import pygame
import random
import os 

# Color mapping for the 6 guitar strings (pastel versions)
STRING_COLORS = {
    "E": (255, 150, 150),     # Pastel red
    "A": (255, 200, 150),     # Pastel orange
    "D": (255, 255, 150),     # Pastel yellow
    "G": (150, 200, 150),     # Pastel green
    "B": (150, 150, 255),     # Pastel blue
    "e": (200, 150, 255),     # Pastel indigo
}

START_POSITIONS = {
    (640, 580): "E",
    (640, 500): "A",
    (640, 420): "D",
    (640, 340): "G",
    (640, 260): "B",
    (640, 180): "e",
}

# Map the guitar string to their respective positions on screen
# Sprite should be a coloured rectangle that looks like a metal wound string that runs across the entire screen
class StringSprite(pygame.sprite.Sprite):
    def __init__(self, string, position):
        super().__init__()
        self.string = string
        self.position = position
        color = STRING_COLORS.get(string, (200, 200, 200))
        
        # Create a retro pixel art wound string
        self.image = pygame.Surface((1280, 8), pygame.SRCALPHA)
        
        # Draw the main string body as a solid line
        pygame.draw.line(self.image, color, (0, 4), (1280, 4), 6)
        
        # Add wound texture on top with diagonal pattern
        black = (0, 0, 0)
        for x in range(0, 1280, 6):
            pygame.draw.line(self.image, black, (x, 1), (x + 3, 6), 2)
        
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        
    def update(self):
        pass
    