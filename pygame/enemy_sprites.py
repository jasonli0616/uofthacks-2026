import pygame
import random
import os 

# Map start positions to string
START_POSITIONS = {
    (50, 50): "E",
    (750, 50): "A",
    (50, 550): "D",
    (750, 550): "G",
    (400, 300): "B",
    (400, 50): "e",
}

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, image_path, string, speed):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.string = string
        self.speed = speed
        self.rect.center = self.get_start_position(string)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
    
    # Get start position based on what string the note is
    def get_start_position(self, string):
        for position, s in START_POSITIONS.items():
            if s == string:
                return position
        return (0, 0)  

        