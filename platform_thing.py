from image_manager import ImageManager
from primitives import Pose
import pygame
import time

class PlatformThing:
    SCALED = {}

    def __init__(self, frame, position, tutorial = False):
        self.frame = frame
        self.position = Pose(position)
        self.offset_position = Pose((0, 0))
        self.path = "assets/images/platform.png"
        self.surf = ImageManager.load(self.path)
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()
        self.state = 999

        self.tutorial = tutorial

    def get_apparent_y(self):
        return ((self.position.y + self.offset_position.y))

    def update(self, dt, events):
        old = self.offset_position.y
        new = self.frame.height
        self.speed = (new - old) / dt
        self.offset_position.y = self.frame.height

    def draw(self, surface, offset=(0, 0)):
        surf = self.get_speed_surf()
        x = self.position.x + self.offset_position.x + offset[0] - surf.get_width()//2
        y = self.position.y + self.offset_position.y + offset[1] - surf.get_height()//2
        surface.blit(surf, (x, y))

        if self.tutorial:
            surf = ImageManager.load("assets/images/grapple.png")
            if time.time()%1 < 0.5:
                surf = ImageManager.load("assets/images/grapple_click.png")
            surface.blit(surf, (x -20, y + 50))

    def get_speed_surf(self):
        scales = [1.01**x for x in range(100)]
        thresh = [300*(item**4) for item in scales]
        scale = 1

        for i, speed in enumerate(thresh):
            if self.speed >= speed:
                scale = scales[i]
                continue
            break

        if self.path not in Platform.SCALED:
            Platform.SCALED[self.path] = {}
        if scale not in Platform.SCALED[self.path]:
            Platform.SCALED[self.path][scale] = pygame.transform.smoothscale(self.surf, (self.surf.get_width(), int(self.surf.get_height()*scale)))
        return Platform.SCALED[self.path][scale]