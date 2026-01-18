import pygame
import random
import os 
from strings import START_POSITIONS
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gemini'))
from enemies import Enemy

# Screen width for spawning at right edge
SCREEN_WIDTH = 1920

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

        # Load animation frames: enemy_1.png and enemy_2.png (fallback to square)
        imgs_dir = os.path.join(os.path.dirname(__file__), "imgs")
        frame_paths = [
            os.path.join(imgs_dir, "enemy_1.png"),
            os.path.join(imgs_dir, "enemy_2.png"),
        ]

        self.frames = []
        for p in frame_paths:
            try:
                self.frames.append(pygame.image.load(p).convert_alpha())
            except (FileNotFoundError, pygame.error):
                self.frames.append(None)

        # If both images failed, build a labeled square
        if not any(self.frames):
            fallback = pygame.Surface((40, 40), pygame.SRCALPHA)
            fallback.fill((255, 255, 255))
            font = pygame.font.Font(None, 20)
            text = font.render(f"{self.note}{self.fret}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(20, 20))
            fallback.blit(text, text_rect)
            self.frames = [fallback, fallback]
        else:
            # Replace missing frames with the other available frame
            if self.frames[0] is None and self.frames[1] is not None:
                self.frames[0] = self.frames[1]
            if self.frames[1] is None and self.frames[0] is not None:
                self.frames[1] = self.frames[0]

        # Animation state
        self.frame_index = 0
        self.anim_counter = 0
        self.anim_interval = 30  # ticks between frame switches

        self.image = self.frames[self.frame_index]
        
        self.rect = self.image.get_rect()
        
        # Spawn at the right edge of the screen on the string's y position
        string_y = self.get_string_y_position(self.string)
        # Offset enemies 15 pixels higher on their string
        self.rect.center = (SCREEN_WIDTH, string_y - 15)

    def update(self):
        # Move left along the string
        self.rect.x -= self.speed

        # Animate frames
        self.anim_counter += 1
        if self.anim_counter >= self.anim_interval:
            self.anim_counter = 0
            self.frame_index = 0 if self.frame_index == 1 else 1
            self.image = self.frames[self.frame_index]
    
    # Get the y position of the string this enemy belongs to
    def get_string_y_position(self, string):
        for position, s in START_POSITIONS.items():
            if s == string:
                return position[1]  # Return the y coordinate
        return 360  # Default to middle of screen if not found  

        