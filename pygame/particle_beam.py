import pygame
from strings import STRING_COLORS

class ParticleBeam(pygame.sprite.Sprite):
    def __init__(self, start_pos, string):
        super().__init__()
        self.string = string
        self.color = STRING_COLORS.get(string, (255, 255, 255))
        self.start_pos = start_pos
        self.length = 50  # Initial beam length
        self.speed = 15  # Expansion speed per frame
        self.lifetime = 20  # Frames before disappearing
        self.current_lifetime = 0
        
        # Create initial image as a thin rectangle
        self.image = pygame.Surface((self.length, 5), pygame.SRCALPHA)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.midleft = self.start_pos
    
    def update(self):
        self.current_lifetime += 1
        if self.current_lifetime > self.lifetime:
            self.kill()
        else:
            # Expand the beam length
            self.length += self.speed
            # Recreate the image with new length
            self.image = pygame.Surface((self.length, 5), pygame.SRCALPHA)
            self.image.fill(self.color)
            self.rect.width = self.length
            # Keep the beam anchored at the start position
            self.rect.midleft = self.start_pos
