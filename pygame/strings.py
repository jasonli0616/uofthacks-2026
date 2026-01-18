import pygame
import random
import os
from start_screen import SCREEN_WIDTH as DESIGN_WIDTH, SCREEN_HEIGHT as DESIGN_HEIGHT

# Screen constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Color mapping for the 6 guitar strings (metallic rainbow)
STRING_COLORS = {
    "E": (255, 100, 100),     # Metallic red
    "A": (255, 180, 80),      # Metallic orange
    "D": (255, 255, 100),     # Metallic yellow
    "G": (100, 220, 100),     # Metallic green
    "B": (100, 150, 255),     # Metallic blue
    "e": (150, 100, 220),     # Metallic indigo
}

# Image mapping for the 6 guitar strings
STRING_IMAGES = {
    "E": "red.png",
    "A": "orange.png",
    "D": "yellow.png",
    "G": "green.png",
    "B": "cyan.png",
    "e": "purple.png",
}

START_POSITIONS = {
    (960, 940): "E",
    (960, 780): "A",
    (960, 620): "D",
    (960, 460): "G",
    (960, 300): "B",
    (960, 140): "e",
}

class StringSprite(pygame.sprite.Sprite):
    def __init__(self, string, position, scale=1.0, offset=(0,0)):
        super().__init__()
        self.string = string
        self.scale = max(0.0001, float(scale))
        self.offset = offset
        
        # 1. Define dimensions (design values scaled)
        design_gap = 225  # design-space gap
        self.gap_width = int(design_gap * self.scale)
        # compute string width from design width scaled - gap
        self.string_width = int(DESIGN_WIDTH * self.scale) - self.gap_width
        
        color = STRING_COLORS.get(string, (200, 200, 200))
        
        # Get the correct image for this string
        image_filename = STRING_IMAGES.get(string, "orange.png")
        full_path = os.path.join(os.path.dirname(__file__), "imgs", image_filename)
        
        try:
            # 2. Load and Scale Image
            base_image = pygame.image.load(full_path).convert_alpha()
            
            original_height = base_image.get_height()
            # Make strings thinner: scale to design fraction then apply scale multiplier
            new_height = max(1, int(original_height * 0.45 * self.scale))
            
            # STRETCH the image to fit exactly the remaining width
            self.image = pygame.transform.scale(base_image, (max(1, self.string_width), new_height))
                
        except (FileNotFoundError, pygame.error):
            # Fallback: Pixel art string filling the exact remaining width (thinner)
            self.image = pygame.Surface((max(1, self.string_width), max(1, int(6 * self.scale))), pygame.SRCALPHA)
            
            # Draw thinner main line
            pygame.draw.line(self.image, color, (0, max(1, int(3 * self.scale))), (self.string_width, max(1, int(3 * self.scale))), max(1, int(4 * self.scale)))
            
            # Draw finer texture
            black = (0, 0, 0)
            step = max(2, int(6 * self.scale))
            for x in range(0, self.string_width, step):
                pygame.draw.line(self.image, black, (x, max(1, int(2 * self.scale))), (min(self.string_width, x + 2), max(1, int(4 * self.scale))), max(1, int(1 * self.scale)))
        
        # 3. Position the Rect (position is design-space tuple)
        self.rect = self.image.get_rect()
        self.rect.midleft = (self.gap_width + self.offset[0], int(position[1] * self.scale + self.offset[1]))
        
    def update(self):
        pass