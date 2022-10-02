from primitives import Pose
import constants as c
from image_manager import ImageManager
import pygame
import math
from hook import Hook


class Player:

    GRAVITY = 2000

    def __init__(self, frame):
        self.frame = frame
        self.velocity = Pose((200, -self.GRAVITY/2))
        self.position = Pose((c.WINDOW_WIDTH//3, c.WINDOW_HEIGHT))
        self.offset_position = Pose((0, 0))
        self.hook = Hook(self)
        self.radius = 25
        self.can_pick_up = True


    def update(self, dt, events):
        self.hook.update(dt, events)

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

        if self.position.x < c.CHAMBER_LEFT and self.velocity.x < 0:
            self.velocity.x *= -0.7
            self.frame.shake(5, Pose((1, 0)))
        if self.position.x > c.CHAMBER_RIGHT and self.velocity.x > 0:
            self.velocity.x *= -0.7
            self.frame.shake(5, Pose((-1, 0)))

        if self.hook.state == Hook.STUCK_REELING:
            new_acceleration = self.hook.position - self.position
            if new_acceleration.x * acceleration.x < 0 or new_acceleration.y * acceleration.y < 0:
                # Must have passed hook point
                if self.can_pick_up:
                    self.hook.un_stick()

        self.offset_position = Pose((0, self.frame.height))

        pass


    def draw(self, surface, offset=(0, 0)):
        surf = pygame.Surface((50, 50))
        surf.fill((100, 0, 0))

        x = self.position.x + offset[0] + self.offset_position.x - surf.get_width()//2
        y = self.position.y + offset[1] + self.offset_position.y - surf.get_height()//2
        surface.blit(surf, (x, y))

        self.hook.draw(surface, offset)

    def get_apparent_y(self):
        return self.position.y + self.offset_position.y