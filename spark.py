import pygame
from image_manager import ImageManager
from primitives import Pose
import random
import math

class Spark:

    PATHS = ["assets/images/spark.png","assets/images/spark3.png"]
    FOREGROUND_PATHS = ["assets/images/spark2.png","assets/images/spark4.png"]
    SCALED = {}

    def __init__(self, frame, position, foreground=False):
        self.frame = frame
        if not foreground:
            path = (random.choice(Spark.PATHS))
        else:
            path = random.choice(Spark.FOREGROUND_PATHS)
        self.surf = ImageManager.load(path)
        self.position = Pose(position)
        self.offset_position = Pose((0, 0))
        self.age = random.random() * 1000
        self.parallax = 0.7
        if "3" in path:
            self.parallax = 0.85
        self.foreground=foreground
        if self.foreground:
            self.parallax = 1.3
            if "4" in path:
                self.parallax = 1.1
        self.path = path
        self.speed = 0

    def update(self, dt, events):
        self.age += dt
        old_height = self.offset_position.y
        new_height = self.frame.height
        self.offset_position.y = self.frame.height

        if dt == 0:
            return
        self.speed = max((new_height - old_height)/dt, 0)

    def get_speed_surf(self):
        scales = [1.05**x for x in range(100)]
        thresh = [300*(item**2) for item in scales]
        scale = 1

        for i, speed in enumerate(thresh):
            if self.speed >= speed:
                scale = scales[i]
                continue
            break

        if self.path not in Spark.SCALED:
            Spark.SCALED[self.path] = {}
        if scale not in Spark.SCALED[self.path]:
            Spark.SCALED[self.path][scale] = pygame.transform.scale(self.surf, (self.surf.get_width()/scale, int(self.surf.get_height()*scale)))
        return Spark.SCALED[self.path][scale]

    def get_apparent_y(self):
        return ((self.position.y + self.offset_position.y)*self.parallax)

    def draw(self, surface, offset=(0, 0)):
        surf = self.get_speed_surf()
        x = (self.position.x + self.offset_position.x) + offset[0] - surf.get_width()//2 + 6*math.sin(self.age * 1.2) * (1 + 3*self.foreground)
        y = self.get_apparent_y() + offset[1] - surf.get_height()//2 + 8 * math.cos(self.age*1.05) * (1 + 3*self.foreground)
        surface.blit(surf, (x, y), special_flags=pygame.BLEND_ADD)
