import pygame
import os

# Player sprite at the left center of the screen
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, image_path="player.png", scale=1.0, offset=(0,0)):
        super().__init__()
        self.scale = max(0.0001, float(scale))
        self.offset = offset
        
        # Try to load image from the correct path
        full_path = os.path.join(os.path.dirname(__file__), "imgs", image_path)
        
        try:
            self.image = pygame.image.load(full_path).convert_alpha()
            # Scale by design multiplier and runtime scale
            new_w = max(1, int(self.image.get_width() * 4 * self.scale))
            new_h = max(1, int(self.image.get_height() * 4 * self.scale))
            self.image = pygame.transform.scale(self.image, (new_w, new_h))
        except (FileNotFoundError, pygame.error):
            # If image not found, create a simple green rectangle sized according to scale
            w = max(1, int(100 * self.scale))
            h = max(1, int(300 * self.scale))
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.image.fill((0, 255, 0))  # Green rectangle
            
        self.rect = self.image.get_rect()
        # center from design-space (125,540) scaled + offset
        self.rect.center = (int(125 * self.scale + self.offset[0]), int(540 * self.scale + self.offset[1]))

    def update(self):
        pass