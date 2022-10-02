from enemy import Enemy
from primitives import Pose
import pygame
import constants as c
import math
from image_manager import ImageManager
from sound_manager import SoundManager


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
        self.end_surf = ImageManager.load("assets/images/kunai.png")


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
        elif self.state == Hook.STUCK_REELING:
            self.since_stuck += dt
        else:
            self.since_stuck = 0
        if self.state == Hook.REELING:
            direction = self.player.position - self.position
            direction.scale_to(Hook.REEL_VELOCITY)
            self.velocity = direction
        if self.state == Hook.DEPLOYED or self.state == Hook.REELING:
            self.position += self.velocity * dt
            self.player.position -= self.velocity * dt * 0.3
            if self.player.position.x < c.CHAMBER_LEFT:
                self.player.position.x = c.CHAMBER_LEFT
            elif self.player.position.x > c.CHAMBER_RIGHT:
                self.player.position.x = c.CHAMBER_RIGHT
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
            if self.player.dead:
                break
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
        self.player.frame.has_grappled = True
        if not self.state == Hook.DEPLOYED:
            return
        kunai_sound = SoundManager.load("assets/sounds/kunai_hit.wav")
        kunai_sound.set_volume(0.2)
        kunai_sound.play()
        self.state = Hook.STUCK
        self.since_stuck = 0
        self.player.frame.shake(25, self.player.position - self.position)
        if isinstance(thing, Enemy):
            self.player.can_pick_up = False
            thing.hooked = True

    def start_stuck_reel(self):
        self.state = Hook.STUCK_REELING

    def un_stick(self):
        self.state = Hook.CARRIED
        self.player.frame.has_collected = True

    def deploy(self):
        self.player.frame.has_grappled = True
        if self.player.frame.has_collected:
            self.player.frame.has_grabbed_enemy = True
        if not self.state == Hook.CARRIED:
            return
        self.player.can_pick_up = True
        self.position = self.player.position.copy()
        self.state = self.DEPLOYED
        self.velocity = Pose(pygame.mouse.get_pos()) - (self.player.position + self.player.offset_position)
        self.velocity.scale_to(Hook.DEPLOY_VELOCITY)

        sound = SoundManager.load("assets/sounds/deploy_kunai.wav")
        sound.set_volume(0.05)
        sound.play()

    def retract(self):
        self.player.frame.has_grappled = True
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
        if self.player.dead:
            return
        if self.state == Hook.CARRIED:
            return
        surf = self.end_surf
        diff = self.position - self.player.position
        surf = pygame.transform.rotate(surf, -math.atan2(diff.y, diff.x) * 180/math.pi)
        surface.blit(surf, (self.position + self.player.offset_position + Pose(offset) - Pose((surf.get_width()//2, surf.get_height()//2))).get_position())

        start = (self.position + self.player.offset_position + Pose(offset))
        end = (self.player.position + self.player.offset_position + Pose(offset))

        unit = end - start
        total_length = unit.magnitude()
        if total_length < 0.1:
            return
        unit.scale_to(10)
        ortho = Pose((unit.y, -unit.x))
        ortho.scale_to(1)
        unit_ct = max(int(total_length/10), 1)
        poses = [start + (unit * i) for i in range(unit_ct)] + [end]
        length_so_far = 0
        period = 15 - 15 * min((self.since_stuck * 2), 1)
        for i, pose in enumerate(poses):
            through = length_so_far/total_length
            mag = min(20, through*35)
            mag = min(mag, (1 - through) * 100)
            mag = min(mag, (20 - self.since_stuck * 200))
            mag = max(mag, 0)
            if self.state == Hook.REELING:
                mag = 0
            if period < 1:
                period = 1
            change = ortho * math.sin(length_so_far/period) * mag
            pose.x += change.x
            pose.y += change.y
            length_so_far += 10


        poses_to_draw = [pose.get_position() for pose in poses]
        pygame.draw.lines(surface, (0, 0, 0), False, poses_to_draw, 3)

