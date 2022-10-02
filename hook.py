from enemy import Enemy
from primitives import Pose
import pygame
import constants as c


class Hook:

    CARRIED = 0
    DEPLOYED = 1
    STUCK = 2
    STUCK_REELING = 3
    REELING = 4

    DEPLOY_VELOCITY = 4000
    REEL_VELOCITY = 7000

    def __init__(self, player):
        self.player = player
        self.position = Pose((0, 0))
        self.velocity = Pose((0, 0))
        self.state = Hook.CARRIED
        self.radius = 10
        self.since_stuck = 0


    def update(self, dt, events):
        min_step = 1/200
        while dt > 0:
            if dt < min_step:
                self.each_update(dt, events)
                break
            self.each_update(min_step, events)
            dt -= min_step

    def each_update(self, dt, events):
        if self.state == Hook.STUCK:
            if self.since_stuck > 0.1:
                self.start_stuck_reel()
            self.since_stuck += dt
        if self.state == Hook.REELING:
            direction = self.player.position - self.position
            direction.scale_to(Hook.REEL_VELOCITY)
            self.velocity = direction
        if self.state == Hook.DEPLOYED or self.state == Hook.REELING:
            self.position += self.velocity * dt
            if self.position.x < c.CHAMBER_LEFT and self.velocity.x < 0:
                self.retract()
                self.player.frame.shake(5, Pose((1, 0)))
            elif self.position.x > c.CHAMBER_RIGHT and self.velocity.x > 0:
                self.retract()
                self.player.frame.shake(5, Pose((-1, 0)))
            elif self.position.y + self.player.offset_position.y > c.WINDOW_HEIGHT + 50:
                self.retract()
            elif self.position.y + self.player.offset_position.y < - 50:
                self.retract()

            if self.state == Hook.REELING:
                direction = self.player.position - self.position
                if direction.magnitude() < self.radius:
                    self.catch()
                else:
                    direction.scale_to(Hook.REEL_VELOCITY)
                    # Detect whether player caught hook
                    new_direction = self.player.position - self.position
                    if direction.y * new_direction.y < 0:
                        self.catch()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.deploy()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.retract()

        if self.state == Hook.DEPLOYED:
            for platform in self.player.frame.platforms:
                if hasattr(platform, "radius"):
                    d = platform.position - self.position
                    if d.magnitude() < self.radius + platform.radius:
                        self.hit_something(platform)
                        continue
                rw = platform.width + self.radius*2
                rh = platform.height + self.radius*2
                rx = platform.position.x - platform.width//2 - self.radius
                ry = platform.position.y - platform.height//2 - self.radius
                rect = pygame.Rect(rx, ry, rw, rh)
                if rect.collidepoint(self.position.x, self.position.y):
                    self.hit_something(platform)

    def hit_something(self, thing):
        if not self.state == Hook.DEPLOYED:
            return
        self.state = Hook.STUCK
        self.since_stuck = 0
        self.player.frame.shake(15, self.player.position - self.position)
        if isinstance(thing, Enemy):
            self.player.can_pick_up = False
            thing.hooked = True

    def start_stuck_reel(self):
        self.state = Hook.STUCK_REELING

    def un_stick(self):
        self.state = Hook.CARRIED

    def deploy(self):
        if not self.state == Hook.CARRIED:
            return
        self.player.can_pick_up = True
        self.position = self.player.position.copy()
        self.state = self.DEPLOYED
        self.velocity = Pose(pygame.mouse.get_pos()) - (self.player.position + self.player.offset_position)
        self.velocity.scale_to(Hook.DEPLOY_VELOCITY)

    def retract(self):
        if not self.state == Hook.DEPLOYED:
            return
        self.state = Hook.REELING

    def catch(self):
        if not self.state == Hook.REELING or self.state == Hook.STUCK_REELING:
            return
        if not self.player.can_pick_up:
            return
        self.state = Hook.CARRIED

    def draw(self, surface, offset=(0, 0)):
        if self.state == Hook.CARRIED:
            return
        surf = pygame.Surface((20, 20))
        surf.fill((0, 0, 255))
        surface.blit(surf, (self.position + self.player.offset_position + Pose(offset) - Pose((surf.get_width()//2, surf.get_height()//2))).get_position())

        start = (self.position + self.player.offset_position + Pose(offset)).get_position()
        end = (self.player.position + self.player.offset_position + Pose(offset)).get_position()
        pygame.draw.line(surface, (0, 0, 0), start, end, 2)