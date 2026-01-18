import pygame
import math
import random
from strings import STRING_COLORS

class FlameParticle(pygame.sprite.Sprite):
    def __init__(self, pos, angle, speed, color, size, lifetime):
        super().__init__()
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color = color
        self.original_size = size
        self.lifetime = lifetime
        self.current_life = lifetime
        
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        self.velocity = [vx, vy]

        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        self.current_life -= 1
        if self.current_life <= 0:
            self.kill()
            return

        life_ratio = self.current_life / self.lifetime
        current_size = int(self.original_size * life_ratio)
        if current_size <= 0: 
            self.kill()
            return
            
        self.image = pygame.Surface((current_size*2, current_size*2), pygame.SRCALPHA)
        
        # Alpha fade
        alpha = int(255 * (life_ratio ** 0.5))
        
        # Draw Outer Glow (Main Color)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(self.image, color_with_alpha, (current_size, current_size), current_size)
        
        # Draw Inner Core (White)
        core_size = int(current_size * 0.6)
        if core_size > 0:
            core_color = (255, 255, 255, alpha)
            pygame.draw.circle(self.image, core_color, (current_size, current_size), core_size)

        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))


class ParticleBeam(pygame.sprite.Sprite):
    def __init__(self, start_pos, string, target_enemy=None):
        super().__init__()
        self.string = string
        self.color = STRING_COLORS.get(string, (255, 255, 255))
        self.start_pos = (float(start_pos[0]), float(start_pos[1]))
        self.target_enemy = target_enemy

        self.length = 0.0        
        self.speed = 22.0 
        self.lifetime = 60       
        self.current_lifetime = 0
        
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.start_pos)

        self._calculate_trajectory()

    def _calculate_trajectory(self):
        if self.target_enemy is not None:
            try:
                tx, ty = self.target_enemy.rect.center
                dx = tx - self.start_pos[0]
                dy = ty - self.start_pos[1]
                self.dist_to_target = math.hypot(dx, dy)
                
                if self.dist_to_target > 0:
                    self.dir = (dx / self.dist_to_target, dy / self.dist_to_target)
                else:
                    self.dir = (1.0, 0.0)
                
                self.angle_rad = math.atan2(dy, dx)
            except Exception:
                self._set_default()
        else:
            self._set_default()

    def _set_default(self):
        self.target_pos = None
        self.dist_to_target = None
        self.dir = (1.0, 0.0)
        self.angle_rad = 0.0

    def _spawn_flames(self):
        my_groups = self.groups()
        if not my_groups: return

        # High density for better effect
        particles_per_frame = 6 

        for _ in range(particles_per_frame):
            dist_variance = random.uniform(0, 40) 
            spawn_dist = max(0, self.length - dist_variance)
            
            bx = self.start_pos[0] + self.dir[0] * spawn_dist
            by = self.start_pos[1] + self.dir[1] * spawn_dist

            # Wide spread
            perp_angle = self.angle_rad + (math.pi / 2)
            jitter_dist = random.uniform(-15, 15)
            spawn_x = bx + math.cos(perp_angle) * jitter_dist
            spawn_y = by + math.sin(perp_angle) * jitter_dist

            angle_jitter = random.uniform(-0.2, 0.2)
            final_angle = self.angle_rad + angle_jitter

            # Large size
            size = random.randint(15, 30)
            
            speed_variance = random.uniform(0.8, 1.2)
            particle_speed = self.speed * 0.4 * speed_variance 
            
            p = FlameParticle(
                pos=(spawn_x, spawn_y),
                angle=final_angle,
                speed=particle_speed,
                color=self.color,
                size=size,
                lifetime=random.randint(20, 35)
            )
            
            for g in my_groups:
                g.add(p)

    def update(self):
        self.current_lifetime += 1
        if self.current_lifetime > self.lifetime:
            self.kill()
            return

        self.length += self.speed
        self._spawn_flames()

        # --- COLLISION LOGIC ---
        if self.target_enemy is not None and self.dist_to_target is not None:
            try:
                # Check if beam has reached the target
                if self.length >= self.dist_to_target:
                    
                    # 1. Trigger the specific hit reaction (Knockback)
                    if hasattr(self.target_enemy, 'hit_by_beam'):
                        self.target_enemy.hit_by_beam()
                    else:
                        # Safe fallback for older enemy types
                        try:
                            self.target_enemy.kill()
                        except:
                            pass
                    
                    # 2. Cap the beam length visually
                    # We stop the fire stream at the point of impact
                    self.length = self.dist_to_target 
                    
                    # 3. Stop tracking the enemy!
                    # If we don't do this, the beam tries to stretch further right 
                    # while the enemy flies right (knockback), creating a weird infinite beam.
                    self.target_enemy = None 

            except Exception:
                # If target died or vanished unexpectedly
                self.kill()