import pygame

from primitives import Pose
import math


class Timestepper:

    EMPTY_COLOR = 39, 47, 61
    CHARGED_COLOR = 255, 255, 255
    BORDER_COLOR = 0, 0, 0

    SMALL_RADIUS = 36
    BUMP_RADIUS = 50

    def __init__(self, frame):
        self.frame = frame
        self.position = Pose((1025, 85))
        self.radius = self.SMALL_RADIUS
        self.charges = 0
        self.border_width = 3
        self.inner_radius = 20
        self.target_radius = self.radius

        self.angle = 0

        self.target_position = self.position.copy()

    def update(self, dt, events):
        if abs(self.radius - self.target_radius) > 2:
            d = self.target_radius - self.radius
            self.radius += d * dt * 5
        else:
            self.radius = self.target_radius
        self.inner_radius = self.radius//2
        self.border_width = self.radius//12

        dp = self.target_position - self.position
        self.position += dp * dt

    def get_charge(self):
        self.charges += 1
        self.radius = self.BUMP_RADIUS

    def full(self):
        return self.charges >= 4

    def draw(self, surface, offset=(0, 0)):
        x = self.position.x + offset[0]
        y = self.position.y + offset[1]
        pygame.draw.circle(
            surface,
            self.EMPTY_COLOR,
            (x, y),
            self.radius,
            0,
        )
        if self.charges > 0:
            pygame.draw.circle(
                surface,
                self.CHARGED_COLOR,
                (x, y),
                self.radius,
                0,
                draw_top_left=self.charges > 0,
                draw_top_right=self.charges > 1,
                draw_bottom_left=self.charges > 2,
                draw_bottom_right=self.charges > 3
            )
        self.border_width = int(self.border_width)
        pygame.draw.line(surface, self.BORDER_COLOR, (x + self.radius, y), (x - self.radius, y), self.border_width)
        pygame.draw.line(surface, self.BORDER_COLOR, (x, y - self.radius), (x, y+self.radius), self.border_width)
        pygame.draw.circle(surface, self.CHARGED_COLOR if self.charges >= 4 else self.EMPTY_COLOR, (x, y), self.inner_radius, 0)
        pygame.draw.circle(surface, self.BORDER_COLOR, (x, y), self.inner_radius, self.border_width)
        pygame.draw.circle(surface, self.BORDER_COLOR, (x, y), self.radius, self.border_width)