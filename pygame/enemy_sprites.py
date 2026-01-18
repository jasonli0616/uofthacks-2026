import pygame
import random
import math
import os 
import sys
from strings import START_POSITIONS, STRING_COLORS

# REMOVED: sys.path hacks and the broken import "from gemini.enemies import Enemy"
# We don't need the Enemy class definition because we are using dictionaries now.

class DebrisParticle(pygame.sprite.Sprite):
    """
    A small piece of the enemy that flies off when it explodes.
    """
    def __init__(self, pos, color, scale):
        super().__init__()
        self.pos = list(pos)
        self.color = color
        eff_scale = max(0.4, scale) 
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(8, 22) * eff_scale 
        self.vel = [math.cos(angle) * speed, math.sin(angle) * speed]
        
        self.size = random.randint(int(10 * eff_scale), int(30 * eff_scale))
        self.original_size = self.size
        self.lifetime = random.randint(40, 70)
        self.start_life = self.lifetime
        
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.vel[0] *= 0.96
        self.vel[1] *= 0.96

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        life_ratio = self.lifetime / self.start_life
        current_size = max(0, int(self.original_size * life_ratio))
        
        self.image = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        
        r, g, b = self.color
        if life_ratio > 0.6:
            draw_color = (255, 255, 255)
        else:
            draw_color = (r, g, b)
            
        alpha = int(255 * life_ratio)
        pygame.draw.circle(self.image, (*draw_color, alpha), (current_size, current_size), current_size)
        
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))


class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, enemy_data, speed=3, image_path=None, screen_width=None, scale=1.0, offset=(0,0)):
        super().__init__()
        
        self.scale = max(0.0001, float(scale))
        self.offset = offset
        self.data = enemy_data if isinstance(enemy_data, dict) else {}
        
        # --- Data Parsing ---
        # Simplified to handle the dictionary format from gemini/enemies.py
        if isinstance(enemy_data, dict):
            self.string = enemy_data.get('string', 'E')
            self.note = enemy_data.get('note', 'A')
            self.fret = enemy_data.get('fret', 0)
        else:
            # Fallback for legacy calls or plain strings
            self.string = str(enemy_data)
            self.note = "A"
            self.fret = 0
        
        self.speed = speed

        # --- Image Loading ---
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

        if not any(self.frames):
            fallback = pygame.Surface((max(8, int(40 * self.scale)), max(8, int(40 * self.scale))), pygame.SRCALPHA)
            color = STRING_COLORS.get(self.string, (255, 255, 255))
            fallback.fill(color)
            self.frames = [fallback, fallback]
        else:
            if self.frames[0] is None: self.frames[0] = self.frames[1]
            if self.frames[1] is None: self.frames[1] = self.frames[0]

        # Scale and Tint
        scaled_frames = []
        for f in self.frames:
            w, h = f.get_width(), f.get_height()
            nw = max(1, int(w * self.scale * 1.8))
            nh = max(1, int(h * self.scale * 1.8))
            scaled_frames.append(pygame.transform.scale(f, (nw, nh)))
        
        color = STRING_COLORS.get(self.string, (255, 255, 255))
        self.frames = [self._colorize_frame(f, color) for f in scaled_frames]

        # --- Animation State ---
        self.frame_index = 0
        self.anim_counter = 0
        self.anim_interval = max(1, int(30 * self.scale))

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        
        # --- Positioning ---
        spawn_x = screen_width if screen_width is not None else int(self.offset[0] + (1920 * self.scale))
        string_y = int(self.get_string_y_position(self.string) * self.scale + self.offset[1])
        self.rect.center = (spawn_x, string_y - max(1, int(30 * self.scale)))

        # --- HIT/KNOCKBACK STATE ---
        self.is_hit = False
        self.knockback_timer = 0
        self.knockback_speed = int(self.speed * 4 * max(1, self.scale))

    def update(self):
        if not self.is_hit:
            self.rect.x -= int(self.speed * max(1, self.scale))
        else:
            self.rect.x += self.knockback_speed
            shake = random.randint(-3, 3)
            self.rect.y += shake

            self.knockback_timer -= 1
            if self.knockback_timer <= 0:
                self._finalize_explosion()
                return

        self.anim_counter += 1
        if self.anim_counter >= self.anim_interval:
            self.anim_counter = 0
            self.frame_index = 0 if self.frame_index == 1 else 1
            self.image = self.frames[self.frame_index]

    def hit_by_beam(self):
        if not self.is_hit:
            self.is_hit = True
            self.knockback_timer = 12 

    def _finalize_explosion(self):
        my_groups = self.groups()
        color = STRING_COLORS.get(self.string, (255, 255, 255))
        
        num_particles = 40
        for _ in range(num_particles):
            debris = DebrisParticle(
                pos=self.rect.center, 
                color=color, 
                scale=self.scale
            )
            for g in my_groups:
                g.add(debris)
                
        self.kill()

    def draw_label(self, surface: pygame.Surface):
        if self.is_hit: return 

        w, h = self.image.get_width(), self.image.get_height()
        label_size = max(12, int(h * 0.7))
        font = pygame.font.Font(None, label_size)
        font.set_bold(True)
        center = (self.rect.centerx + max(8, int(50 * self.scale)), self.rect.centery)
        self._blit_outlined_text(surface, str(self.fret), font, center, thickness=max(1, int(2 * self.scale)))

    def _colorize_frame(self, frame: pygame.Surface, color: tuple) -> pygame.Surface:
        f = frame.copy()
        tint = pygame.Surface(f.get_size(), pygame.SRCALPHA)
        tint.fill(color + (0,))
        f.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        return f

    def _blit_outlined_text(self, surface, text, font, center, text_color=(255, 255, 255), outline_color=(0, 0, 0), thickness=2):
        text_surf = font.render(text, True, text_color)
        outline_surf = font.render(text, True, outline_color)
        cx, cy = center
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx == 0 and dy == 0: continue
                rect = outline_surf.get_rect(center=(cx + dx, cy + dy))
                surface.blit(outline_surf, rect)
        rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, rect)
    
    def get_string_y_position(self, string):
        for position, s in START_POSITIONS.items():
            if s == string:
                return position[1]
        return 360