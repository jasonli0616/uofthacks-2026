import pygame
import random
import os 

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
    def __init__(self, string, position):
        super().__init__()
        self.string = string
        
        # 1. Define dimensions
        self.gap_width = 225  # The empty space on the left
        self.string_width = SCREEN_WIDTH - self.gap_width # The remaining space
        
        color = STRING_COLORS.get(string, (200, 200, 200))
        
        # Get the correct image for this string
        image_filename = STRING_IMAGES.get(string, "orange.png")
        full_path = os.path.join(os.path.dirname(__file__), "imgs", image_filename)
        
        try:
            # 2. Load and Scale Image
            base_image = pygame.image.load(full_path).convert_alpha()
            
            original_height = base_image.get_height()
            # Make strings even thinner: scale to 30% of original height
            new_height = int(original_height * 0.45)
            
            # STRETCH the image to fit exactly the remaining width (1770px)
            self.image = pygame.transform.scale(base_image, (self.string_width, new_height))
                
        except (FileNotFoundError, pygame.error):
            # Fallback: Pixel art string filling the exact remaining width (thinner)
            self.image = pygame.Surface((self.string_width, 6), pygame.SRCALPHA)
            
            # Draw thinner main line
            pygame.draw.line(self.image, color, (0, 3), (self.string_width, 3), 4)
            
            # Draw finer texture
            black = (0, 0, 0)
            for x in range(0, self.string_width, 6):
                pygame.draw.line(self.image, black, (x, 2), (x + 2, 4), 1)
        
        # 3. Position the Rect
        self.rect = self.image.get_rect()
        
        # We use 'midleft' to anchor the left side of the string to the gap
        # position[1] is the Y-coordinate from START_POSITIONS
        self.rect.midleft = (self.gap_width, position[1])
        
    def update(self):
        pass