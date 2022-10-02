
from image_manager import ImageManager
from primitives import Pose
import pygame
from pyracy.sprite_tools import Sprite, Animation
import random
import math

class Enemy:

    NORMAL = 0
    EXPLODED = 1

    SCALED = {}

    def __init__(self, frame, position):
        self.frame = frame
        self.position = Pose(position)
        self.offset_position = Pose((0, 0))
        self.path = "assets/images/energy.png"
        self.surf = ImageManager.load(self.path)
        self.pulse_surf = ImageManager.load("assets/images/energy_full.png")
        self.width = 90
        self.height = 90
        self.radius = 45
        self.age = random.random() * 1000
        self.shift_position = Pose((0, 0))
        self.state = Enemy.NORMAL
        self.hooked = False

    def get_apparent_y(self):
        return ((self.position.y + self.offset_position.y))

    def update(self, dt, events):
        old = self.offset_position.y
        new = self.frame.height
        self.speed = (new - old) / dt
        self.offset_position.y = self.frame.height
        self.age += dt

        d = self.position - self.frame.player.position
        if d.magnitude() < self.radius + self.frame.player.radius and self.state == Enemy.NORMAL:
            self.collide_with_player()

        if self.hooked:
            d.scale_to(abs(self.frame.player.velocity.magnitude()) * 0.3)
            self.position -= d*dt
            self.frame.player.hook.position -= d*dt

    def collide_with_player(self):
        if not self.frame.player.hook.state == 3: # STUCK_REELING
            return
        self.frame.player.hook.un_stick()
        self.state = Enemy.EXPLODED
        self.frame.shake(150, (1, 0))
        d = self.position - self.frame.player.position
        player_push = d.copy()
        if player_push.magnitude() == 0:
            player_push = Pose((0, -1))
        player_push.y = -1200
        player_push.x *= 10
        self.frame.player.velocity = player_push
        self.frame.player.velocity.y = min(-1500, self.frame.player.velocity.y - 2500)

    def draw(self, surface, offset=(0, 0)):
        surf, pulse_surf = self.get_speed_surf()
        self.shift_position.x = 8 * math.sin(self.age*1.9)
        self.shift_position.y = 5 * math.sin(self.age*2.1)
        x = self.position.x + self.offset_position.x + offset[0] - surf.get_width()//2 + self.shift_position.x
        y = self.position.y + self.offset_position.y + offset[1] - surf.get_height()//2 + self.shift_position.y
        pulse_surf.set_alpha(128 + 128*math.sin(self.age * 6))


        surface.blit(surf, (x, y))
        surface.blit(pulse_surf, (x, y))

    def get_speed_surf(self):
        scales = [1.01**x for x in range(100)]
        thresh = [2000*(item**4) for item in scales]
        scale = 1

        for i, speed in enumerate(thresh):
            if self.speed >= speed:
                scale = scales[i]
                continue
            break

        if self.path not in Enemy.SCALED:
            Enemy.SCALED[self.path] = {}
        if scale not in Enemy.SCALED[self.path]:
            Enemy.SCALED[self.path][scale] = \
                (pygame.transform.smoothscale(self.surf, (self.surf.get_width()/scale, int(self.surf.get_height()*scale))),
                pygame.transform.smoothscale(self.pulse_surf, (self.pulse_surf.get_width()/scale, int(self.pulse_surf.get_height()*scale))))
        return Enemy.SCALED[self.path][scale]