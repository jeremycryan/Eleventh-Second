import pygame
import constants as c
from image_manager import ImageManager
import random
from primitives import Pose
import math


class Gear:

    RED_SURF = {}
    BLUE_SURF = {}

    def __init__(self, frame, size, position):
        self.frame = frame
        self.parallax = 0.5
        self.size = size
        if size == c.SMALL:
            num = random.choice([4, 5])
        else:
            num = random.choice([1, 2, 3])
        path = f"assets/images/gear_{num}.png"
        self.path = path
        self.first_load = path not in ImageManager.sounds
        self.surf = ImageManager.load(path)
        self.radius = self.surf.get_width()/2
        self.speed = 30
        if self.size == c.SMALL:
            self.speed *= -2
        self.position = Pose(position, 0)
        self.offset_position = Pose((0, 0))
        self.process_surf()

    def process_surf(self):
        if self.path not in self.BLUE_SURF:
            filter = self.surf.copy()
            filter.fill((60, 90, 180))
            Gear.BLUE_SURF[self.path] = self.surf.copy()
            Gear.BLUE_SURF[self.path].blit(filter, (0, 0), special_flags=pygame.BLEND_ADD)

        if self.path not in self.RED_SURF:
            filter = self.surf.copy()
            filter.fill((190, 60, 0))
            Gear.RED_SURF[self.path] = self.surf.copy()
            Gear.RED_SURF[self.path].blit(filter, (0, 0), special_flags=pygame.BLEND_ADD)
        self.surf = self.RED_SURF[self.path]

    def align_with(self, other):
        if other.size == self.size:
            self.speed = -other.speed
        elif other.size == c.BIG and self.size == c.SMALL:
            self.speed = other.speed * -2
        else:
            self.speed = -other.speed/2

        angle_to = -math.atan2((self.position.y - other.position.y)*self.parallax, self.position.x - other.position.x) * 180/math.pi
        x = other.position.angle - angle_to
        y = x * -self.speed/other.speed
        z = 180 - y
        self.position.angle = z + angle_to

    def update(self, dt, events):
        if self.frame.rewinding:
            factor = -5
        else:
            factor = 1
        self.position.angle += self.speed * dt * factor
        self.offset_position = Pose((0, self.frame.height))

        if self.frame.rewinding:
            self.surf = self.BLUE_SURF[self.path]
        else:
            self.surf = self.RED_SURF[self.path]

    def draw(self, surface, offset=(0, 0)):
        if self.get_apparent_y() < -self.radius - 50:
            return

        surfs_and_ops = []
        if not self.frame.rewinding or self.frame.rewind_intensity() > 0:
            surfs_and_ops.append((self.RED_SURF[self.path], 255))
        if self.frame.rewinding:
            surfs_and_ops.append((self.BLUE_SURF[self.path], 255 * (1 - self.frame.rewind_intensity())))

        for surf, op in surfs_and_ops:
            surf = pygame.transform.rotate(surf, self.position.angle)
            surf.set_alpha(op)
            position = self.position + self.offset_position
            y = position.y * self.parallax + offset[1] - surf.get_height()/2
            x = position.x + offset[0] - surf.get_width()/2
            surface.blit(surf, (x, y))

    def get_apparent_y(self):
        return (self.position.y + self.offset_position.y)* self.parallax

    def make_child(self, direction):
        dir_vec = Pose((random.random(), 2 * random.random() - 1))
        if direction == c.LEFT:
            dir_vec.x *= -1
        if self.size == c.BIG:
            other_size = c.SMALL
        else:
            other_size = random.choice([c.BIG, c.SMALL])
        dir_vec.scale_to(c.RADII[other_size] + c.RADII[self.size] - c.TOOTH_DEPTH)
        dir_vec.y /= self.parallax
        new_position = dir_vec + self.position
        new_gear = Gear(self.frame,other_size,new_position.get_position())
        new_gear.align_with(self)
        return new_gear

    def __repr__(self):
        return f"<Gear - x:{int(self.position.x)}, y:{int(self.position.y)}, apy:{int(self.get_apparent_y())}, angle:{int(self.position.angle)}, size:{self.size}"