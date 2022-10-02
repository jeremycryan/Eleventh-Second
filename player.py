from explosion import PlayerExplosion
from primitives import Pose
import constants as c
from image_manager import ImageManager
import pygame
import math
from hook import Hook
import time

from sound_manager import SoundManager


class Player:

    GRAVITY = 2000

    def __init__(self, frame):
        self.frame = frame
        self.velocity = Pose((200, -self.GRAVITY*0.5))
        self.position = Pose((c.WINDOW_WIDTH//3, c.WINDOW_HEIGHT))
        self.offset_position = Pose((0, 0))
        self.hook = Hook(self)
        self.radius = 25
        self.can_pick_up = True

        self.surf = ImageManager.load("assets/images/catmissile.png")
        self.age = 0

        self.dead = False


    def update(self, dt, events):
        if self.dead:
            return

        self.hook.update(dt, events)
        self.age += dt

        acceleration = Pose((0, 0))
        if self.hook.state == Hook.STUCK:
            self.velocity = Pose((0, 0))
        elif self.hook.state == Hook.STUCK_REELING:
            acceleration = self.hook.position - self.position
            acceleration.scale_to(5000)
            if self.velocity.magnitude() < 1000:
                acceleration.scale_to(25000)
        else:
            acceleration = Pose((0, self.GRAVITY))
        self.velocity += acceleration * dt

        if self.hook.state == Hook.DEPLOYED or self.hook.state == Hook.REELING:
            self.position += self.velocity * dt * 0.2
        else:
            self.position += self.velocity * dt

        bump = SoundManager.load("assets/sounds/bump.wav")
        bump.set_volume(0.1)
        if self.position.x < c.CHAMBER_LEFT and self.velocity.x < 0:
            self.velocity.x *= -0.7
            self.frame.shake(5, Pose((1, 0)))
            bump.play()
        if self.position.x > c.CHAMBER_RIGHT and self.velocity.x > 0:
            self.velocity.x *= -0.7
            self.frame.shake(5, Pose((-1, 0)))
            bump.play()
        if self.hook.state == Hook.STUCK_REELING:
            new_acceleration = self.hook.position - self.position
            if new_acceleration.x * acceleration.x < 0 or new_acceleration.y * acceleration.y < 0:
                # Must have passed hook point
                if self.can_pick_up:
                    self.hook.un_stick()

        if self.get_apparent_y() > c.WINDOW_HEIGHT + 50 and not self.hook.state in [Hook.STUCK, Hook.STUCK_REELING, Hook.DEPLOYED]:
            if not self.dead:
                self.die()

        self.offset_position = Pose((0, self.frame.height))

        pass

    def die(self):
        if self.dead:
            return
        self.dead = True
        self.frame.explosions.append(PlayerExplosion(self.frame, self))


    def draw(self, surface, offset=(0, 0)):
        if self.dead:
            return
        if self.velocity.y < -350 or self.hook.state == Hook.STUCK_REELING:
            angle = -math.atan2(self.velocity.y, self.velocity.x) * 180/math.pi - 90
            surf = ImageManager.load("assets/images/catmissile.png")
            if (self.age % (2/12)) < 1/12:
                surf = ImageManager.load("assets/images/catmissile2.png")

            surf = pygame.transform.rotate(surf, angle)
        elif self.velocity.y < 0:
            surf = ImageManager.load("assets/images/between_cat.png")
        else:
            surf = ImageManager.load("assets/images/catman.png")

        x = self.position.x + offset[0] + self.offset_position.x - surf.get_width()//2
        y = self.position.y + offset[1] + self.offset_position.y - surf.get_height()//2
        surface.blit(surf, (x, y))

        self.hook.draw(surface, offset)

    def get_apparent_y(self):
        return self.position.y + self.offset_position.y