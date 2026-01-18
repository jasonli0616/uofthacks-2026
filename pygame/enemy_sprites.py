import pygame
import random
import os 
from strings import START_POSITIONS
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gemini'))
from enemies import Enemy

# Screen width for spawning at right edge
SCREEN_WIDTH = 1280

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, enemy_data, speed=3, image_path=None):
        """
        Create an enemy sprite from Enemy data
        Args:
            enemy_data: Enemy object from enemies.py or dict with 'string', 'note', 'fret'
            speed: Movement speed (default 3)
            image_path: Optional path to enemy image (default None = square)
        """
        super().__init__()
        
        # Handle both Enemy objects and dicts
        if isinstance(enemy_data, Enemy):
            self.string = enemy_data.string
            self.note = enemy_data.note
            self.fret = enemy_data.fret
        elif isinstance(enemy_data, dict):
            self.string = enemy_data.get('string', 'E')
            self.note = enemy_data.get('note', 'A')
            self.fret = enemy_data.get('fret', 0)
        else:
            # Fallback for simple string input (backwards compatibility)
            self.string = enemy_data
            self.note = "A"
            self.fret = 0
        
        self.speed = speed
        
        # If image_path is None, create a simple square with note label
        if image_path is None:
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 255, 255))  # White square
            
            # Add note and fret text
            font = pygame.font.Font(None, 20)
            text = font.render(f"{self.note}{self.fret}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(20, 20))
            self.image.blit(text, text_rect)
        else:
            self.image = pygame.image.load(image_path).convert_alpha()
        
        self.rect = self.image.get_rect()
        
        # Spawn at the right edge of the screen on the string's y position
        string_y = self.get_string_y_position(self.string)
        self.rect.center = (SCREEN_WIDTH, string_y)

    def update(self):
        # Move left along the string
        self.rect.x -= self.speed
    
    # Get the y position of the string this enemy belongs to
    def get_string_y_position(self, string):
        for position, s in START_POSITIONS.items():
            if s == string:
                return position[1]  # Return the y coordinate
        return 360  # Default to middle of screen if not found  

        