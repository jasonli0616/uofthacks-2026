import pygame
import os

# Player sprite at the left center of the screen
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, image_path="imgs/player.png"):
        super().__init__()
        
        # Try to load image from the correct path
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        
        try:
            self.image = pygame.image.load(full_path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            # If image not found, create a simple green rectangle
            self.image = pygame.Surface((50, 100))
            self.image.fill((0, 255, 0))  # Green rectangle
        
        self.rect = self.image.get_rect()
        self.rect.center = (100, 360)  # Left center of the screen

    def update(self):
        pass