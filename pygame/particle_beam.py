import pygame
import math
from strings import STRING_COLORS

class ParticleBeam(pygame.sprite.Sprite):
    def __init__(self, start_pos, string, target_enemy=None):
        super().__init__()
        self.string = string
        self.color = STRING_COLORS.get(string, (255, 255, 255))
        # start_pos is screen coords (x,y)
        self.start_pos = (float(start_pos[0]), float(start_pos[1]))
        self.target_enemy = target_enemy

        # beam geometry
        self.length = 0.0        # grows from 0 toward target
        self.speed = 20.0        # pixels per frame
        self.lifetime = 60       # fallback
        self.current_lifetime = 0

        # precompute target position and direction if target provided
        if self.target_enemy is not None:
            try:
                tx, ty = self.target_enemy.rect.center
                dx = tx - self.start_pos[0]
                dy = ty - self.start_pos[1]
                self.target_pos = (float(tx), float(ty))
                self.dist_to_target = math.hypot(dx, dy)
                # unit direction vector toward target
                if self.dist_to_target > 0:
                    self.dir = (dx / self.dist_to_target, dy / self.dist_to_target)
                else:
                    self.dir = (1.0, 0.0)
                # angle in degrees for drawing (pygame rotates counter-clockwise)
                self.angle_deg = -math.degrees(math.atan2(dy, dx))
            except Exception:
                self.target_pos = None
                self.dist_to_target = None
                self.dir = (1.0, 0.0)
                self.angle_deg = 0.0
        else:
            # no target: shoot horizontally right
            self.target_pos = None
            self.dist_to_target = None
            self.dir = (1.0, 0.0)
            self.angle_deg = 0.0

        # initial image (zero length)
        self.thickness = 6
        self._rebuild_image()

    def _rebuild_image(self):
        # Build a base surface with current length, rotate it, and set rect centered between start and end
        length_int = max(1, int(self.length))
        base = pygame.Surface((length_int, self.thickness), pygame.SRCALPHA)
        base.fill(self.color)
        if self.angle_deg != 0.0:
            rotated = pygame.transform.rotate(base, self.angle_deg)
        else:
            rotated = base
        self.image = rotated
        # compute end point and place rect center at midpoint
        end_x = self.start_pos[0] + self.dir[0] * self.length
        end_y = self.start_pos[1] + self.dir[1] * self.length
        mid_x = (self.start_pos[0] + end_x) / 2.0
        mid_y = (self.start_pos[1] + end_y) / 2.0
        self.rect = self.image.get_rect()
        # set rect center to midpoint so sprite.draw will position correctly
        self.rect.center = (int(mid_x), int(mid_y))

    def update(self):
        self.current_lifetime += 1
        if self.current_lifetime > self.lifetime:
            self.kill()
            return

        # expand beam
        self.length += self.speed
        self._rebuild_image()

        # if we have a target, check if the beam has reached it
        if self.target_enemy is not None and self.dist_to_target is not None:
            try:
                # if beam length reaches or exceeds distance to target -> hit
                if self.length >= self.dist_to_target:
                    try:
                        self.target_enemy.kill()
                    except Exception:
                        pass
                    self.kill()
            except Exception:
                # target may have been removed already
                self.kill()
                return
