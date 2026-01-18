import pygame
import random
import os 
from strings import START_POSITIONS, STRING_COLORS
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gemini'))
from enemies import Enemy

# remove hardcoded SCREEN_WIDTH usage; spawn X will be passed in or computed from scale

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, enemy_data, speed=3, image_path=None, screen_width=None, scale=1.0, offset=(0,0)):
        """
        Create an enemy sprite from Enemy data
        Args:
            enemy_data: Enemy object from enemies.py or dict with 'string', 'note', 'fret'
            speed: Movement speed (default 3)
            screen_width: actual screen width in pixels where enemies should spawn (right edge)
            scale: uniform scale factor from design-space -> screen-space
            offset: (offset_x, offset_y) letterbox offset
        """
        super().__init__()
        
        self.scale = max(0.0001, float(scale))
        self.offset = offset
        
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

        # If both images failed, build a plain square (no note text)
        if not any(self.frames):
            fallback = pygame.Surface((max(8, int(40 * self.scale)), max(8, int(40 * self.scale))), pygame.SRCALPHA)
            # Use the string's color instead of white
            color = STRING_COLORS.get(self.string, (255, 255, 255))
            fallback.fill(color)
            self.frames = [fallback, fallback]
        else:
            # Replace missing frames with the other available frame
            if self.frames[0] is None and self.frames[1] is not None:
                self.frames[0] = self.frames[1]
            if self.frames[1] is None and self.frames[0] is not None:
                self.frames[1] = self.frames[0]

        # Scale frames by scale factor and a design multiplier (keep visible)
        scaled_frames = []
        for f in self.frames:
            w, h = f.get_width(), f.get_height()
            nw = max(1, int(w * self.scale * 1.8))
            nh = max(1, int(h * self.scale * 1.8))
            scaled_frames.append(pygame.transform.scale(f, (nw, nh)))
        
        # Apply string color tinting to frames
        color = STRING_COLORS.get(self.string, (255, 255, 255))
        self.frames = [self._colorize_frame(f, color) for f in scaled_frames]

        # Animation state
        self.frame_index = 0
        self.anim_counter = 0
        self.anim_interval = max(1, int(30 * self.scale))  # scale animation timing slightly

        self.image = self.frames[self.frame_index]
        
        self.rect = self.image.get_rect()
        
        # Spawn at the right edge of the screen on the string's y position
        # Use provided screen_width (actual screen pixels) or compute from design * scale + offset
        spawn_x = screen_width if screen_width is not None else int(self.offset[0] + (1920 * self.scale))
        string_y = int(self.get_string_y_position(self.string) * self.scale + self.offset[1])
        # Offset enemies a bit up on their string scaled
        self.rect.center = (spawn_x, string_y - max(1, int(30 * self.scale)))

    def update(self):
        # Move left along the string
        self.rect.x -= int(self.speed * max(1, self.scale))

        # Animate frames
        self.anim_counter += 1
        if self.anim_counter >= self.anim_interval:
            self.anim_counter = 0
            self.frame_index = 0 if self.frame_index == 1 else 1
            self.image = self.frames[self.frame_index]

    def _colorize_frame(self, frame: pygame.Surface, color: tuple) -> pygame.Surface:
        """Tint a frame with the given RGB color"""
        f = frame.copy()
        tint = pygame.Surface(f.get_size(), pygame.SRCALPHA)
        tint.fill(color + (0,))
        f.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        return f

    def _blit_outlined_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font, center: tuple, text_color=(255, 255, 255), outline_color=(0, 0, 0), thickness=2):
        # Draw outline by rendering text around the center
        text_surf = font.render(text, True, text_color)
        outline_surf = font.render(text, True, outline_color)
        cx, cy = center
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                rect = outline_surf.get_rect(center=(cx + dx, cy + dy))
                surface.blit(outline_surf, rect)
        rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, rect)

    def draw_label(self, surface: pygame.Surface):
        # Render only the fret number, trailing behind the enemy by +50px scaled
        w, h = self.image.get_width(), self.image.get_height()
        label_size = max(12, int(h * 0.7))
        font = pygame.font.Font(None, label_size)
        font.set_bold(True)
        center = (self.rect.centerx + max(8, int(50 * self.scale)), self.rect.centery)
        self._blit_outlined_text(surface, str(self.fret), font, center, text_color=(255, 255, 255), outline_color=(0, 0, 0), thickness=max(1, int(2 * self.scale)))
    
    # Get the y position of the string this enemy belongs to
    def get_string_y_position(self, string):
        for position, s in START_POSITIONS.items():
            if s == string:
                return position[1]  # Return the design y coordinate
        return 360  # Default to middle of design screen if not found

