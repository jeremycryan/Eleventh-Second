
from image_manager import ImageManager
from primitives import Pose
import pygame
from pyracy.sprite_tools import Sprite, Animation
import random
import math
import constants as c

from sound_manager import SoundManager


class Particle:

    def __init__(self, explosion, position):
        self.explosion = explosion
        self.position = Pose(position)
        self.duration = 0.3 * explosion.duration/0.25
        self.age = random.random() * self.duration
        self.offset_position = Pose((0, 0))

        self.surf = ImageManager.load("assets/images/spark2.png")

        angle = random.random() * math.pi * 2
        self.velocity = Pose((math.sin(angle), math.cos(angle)))
        self.velocity.scale_to(random.random()**2 * 2000 + 1000)
        self.velocity *= 0.30/explosion.duration

    def update(self, dt, events):
        self.age += dt
        self.position += self.velocity*dt
        self.offset_position = self.explosion.offset_position
        self.velocity *= 0.1**dt

    def through(self):
        return self.age / self.duration

    def draw(self, surface, offset=(0, 0)):
        r = max(30 * (1-self.through()**2), 1)
        surf = pygame.transform.scale(self.surf, (2*r, 2*r))
        x = self.position.x + self.offset_position.x + offset[0] - r
        y = self.position.y + self.offset_position.y + offset[1] - r
        surface.blit(surf, (x, y), special_flags=pygame.BLEND_ADD)


class Explosion:


    def __init__(self, frame, enemy):
        self.frame = frame
        self.position = enemy.position
        self.radius = 45
        self.age = random.random() * 1000
        self.offset_position = enemy.offset_position
        self.age = 0
        self.duration = 0.3
        self.destroyed = False

        self.frame.do_flare(128)
        self.particles = [Particle(self, self.position.get_position()) for _ in range(30)]

        self.boom_noise = SoundManager.load("assets/sounds/explosion.wav")
        self.boom_noise.play()

    def through(self):
        return self.age / self.duration

    def get_apparent_y(self):
        return ((self.position.y + self.offset_position.y))

    def update(self, dt, events):
        self.age += dt
        self.offset_position.y = self.frame.height

        if self.age > self.duration:
            self.destroyed = True
            return

        for particle in self.particles:
            particle.update(dt, events)

        self.radius += 2000 * (1 - self.through())**2 * dt

    def get_color(self):
        r = 255 - (self.through() * 128)
        g = 255 - (self.through() * 55)
        b = 255 - (self.through() * 0)
        return r, g, b


    def draw(self, surface, offset=(0, 0)):
        #self.frame.player.velocity = Pose((0, 0))
        if self.destroyed:
            return
        x = self.position.x + self.offset_position.x + offset[0]
        y = self.position.y + self.offset_position.y + offset[1]
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius, int(50 * (1 - self.through()**2)) + 1)
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius*2, int(25 * (1 - self.through() ** 2)) + 1)

        for particle in self.particles:
            particle.draw(surface, offset=(0, 0))


class PlayerExplosion(Explosion):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = 0.75

    def get_color(self):
        r = 255 - (self.through() * 0)
        g = 255 - (self.through() * 255)
        b = 255 - (self.through() * 200)
        return r, g, b

    def draw(self, surface, offset=(0, 0)):
        #self.frame.player.velocity = Pose((0, 0))
        if self.destroyed:
            return
        x = self.position.x + self.offset_position.x + offset[0]
        y = min(c.WINDOW_HEIGHT, self.position.y + self.offset_position.y + offset[1])
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius*0.5, int(60 * (1 - self.through()**2)) + 1)
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius*1, int(40 * (1 - self.through() ** 2)) + 1)
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius * 2, int(30 * (1 - self.through() ** 2)) + 1)
        pygame.draw.circle(surface, self.get_color(), (x, y), self.radius*3, int(20 * (1 - self.through()**2)) + 1)

        for particle in self.particles:
            particle.draw(surface, offset=(0, 0))