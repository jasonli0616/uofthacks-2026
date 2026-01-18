import pygame
import random
import os 

# Color mapping for the 6 guitar strings (metallic rainbow)
STRING_COLORS = {
    "E": (255, 100, 100),     # Metallic red
    "A": (255, 180, 80),      # Metallic orange
    "D": (255, 255, 100),     # Metallic yellow
    "G": (100, 220, 100),     # Metallic green
    "B": (100, 150, 255),     # Metallic blue
    "e": (150, 100, 220),     # Metallic indigo
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
        
        # Create a retro pixel art wound string with a gap on the left
        gap_width = 150  # Gap on the left for the player
        string_width = 1280 - gap_width
        self.image = pygame.Surface((string_width, 8), pygame.SRCALPHA)
        
        # Draw the main string body as a solid line
        pygame.draw.line(self.image, color, (0, 4), (string_width, 4), 6)
        
        # Add wound texture on top with diagonal pattern
        black = (0, 0, 0)
        for x in range(0, string_width, 6):
            pygame.draw.line(self.image, black, (x, 1), (x + 3, 6), 2)
        
        self.rect = self.image.get_rect()
        # Position the string starting after the gap
        self.rect.center = (position[0] + gap_width // 2, position[1])
        
        
    def update(self):
        pass
    