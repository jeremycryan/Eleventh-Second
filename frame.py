import pygame
import constants as c
from enemy import Enemy
from explosion import Explosion
from hook import Hook
from image_manager import ImageManager
from gear import Gear
from primitives import Pose
import random
from spark import Spark
from player import Player
import math

from platform import Platform


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))

    def next_frame(self):
        return Frame()


class GameFrame(Frame):

    def load(self):
        self.height = 0

        self.gradient = ImageManager.load("assets/images/gradient.png")
        self.gradient = pygame.transform.scale(self.gradient, (c.CHAMBER_WIDTH, c.WINDOW_HEIGHT))
        self.background_detail = ImageManager.load("assets/images/background_detail.png")
        self.background_edge = ImageManager.load("assets/images/background_detail_edge.png")

        self.gear_1 = Gear(self, c.BIG,(c.CHAMBER_LEFT, c.WINDOW_HEIGHT/2))
        self.gear_2 = self.gear_1.make_child(c.RIGHT)
        self.gears = [self.gear_1, self.gear_2]
        self.sparks = []
        self.foreground_sparks = []
        self.platforms = []
        self.explosions = []
        self.refill_sparks()

        self.player = Player(self)

        self.shake_amp = 0
        self.shake_time = 0
        self.shake_direction = Pose((1, 1))
        self.speed = 0
        self.sim_speed = 1

        self.flare = pygame.Surface((c.CHAMBER_WIDTH, c.WINDOW_HEIGHT))
        self.flare.fill((255, 255, 255))
        self.flare_alpha = 0


    def do_flare(self, amt):
        self.flare_alpha = amt


    def shake(self, amt=15, direction=None):
        if amt > self.shake_amp:
            self.shake_amp = amt
            self.shake_time = 0
        if self.shake_direction is None or self.shake_direction.magnitude() == 0:
            self.shake_direction = Pose((1, -1))
        self.shake_direction.scale_to(1)

    def get_shake_offset(self):
        x, y = (self.shake_direction * (math.cos(self.shake_time * 35)) * self.shake_amp).get_position()
        return x, y

    def update(self, dt, events):
        odt = dt
        if self.sim_speed < 1:
            self.sim_speed += 5*dt
            if self.sim_speed > 1:
                self.sim_speed = 1
        dt *= self.sim_speed
        self.shake_time += dt

        self.flare_alpha -= 200*dt
        if self.flare_alpha < 0:
            self.flare_alpha = 0

        self.height += self.speed*dt
        self.speed *= 0.5**dt

        self.shake_amp *= 0.001**dt
        self.shake_amp -= 30*dt
        if self.shake_amp < 0:
            self.shake_amp = 0

        dy = 250 - self.player.get_apparent_y()
        if dy > 0:
            self.height += dy**2 * 0.2 * dt

        self.player.update(dt, events)

        self.gears.sort(key=lambda x: x.get_apparent_y())
        if self.gears:
            top_gear = self.gears[0]
            if top_gear.get_apparent_y() > 0:
                self.spawn_new_gear_set(top_gear)

        for gear in self.gears[:]:
            gear.update(dt, events)
            if gear.get_apparent_y() > c.WINDOW_HEIGHT + gear.radius + 50:
                self.gears.remove(gear)

        for spark in self.sparks[:]:
            spark.update(dt, events)
            if spark.get_apparent_y() > c.WINDOW_HEIGHT + 20:
                self.sparks.remove(spark)

        for spark in self.foreground_sparks[:]:
            spark.update(dt, events)
            if spark.get_apparent_y() > c.WINDOW_HEIGHT + 50:
                if len(self.foreground_sparks) > 1:
                    self.foreground_sparks.remove(spark)

        self.platforms.sort(key=lambda x: x.get_apparent_y())
        if self.platforms:
            top_platform = self.platforms[0]
        else:
            top_platform = Platform(self, (0, c.WINDOW_HEIGHT))
        while top_platform.get_apparent_y() > 0:
            self.spawn_new_platform(top_platform)
            self.platforms.sort(key=lambda x: x.get_apparent_y())
            top_platform = self.platforms[0]

        for platform in self.platforms[:]:
            platform.update(dt, events)
            if platform.get_apparent_y() > c.WINDOW_HEIGHT + platform.height//2:
                if not hasattr(platform, "hooked") or not platform.hooked:
                    self.platforms.remove(platform)
            if platform.state == Enemy.EXPLODED:
                self.platforms.remove(platform)
                self.slowdown()
                self.explosions.append(Explosion(self, platform))

        for explosion in self.explosions[:]:
            explosion.update(dt, events)
            if explosion.get_apparent_y() - explosion.radius * 2 > c.WINDOW_HEIGHT:
                self.explosions.remove(explosion)
            elif explosion.destroyed:
                self.explosions.remove(explosion)

        self.refill_sparks()



    def spawn_new_gear_set(self, top_gear=None):
        if top_gear.position.x < c.WINDOW_WIDTH//2:
            favor_side = c.RIGHT
        else:
            favor_side = c.LEFT
        side = random.choice([c.RIGHT, c.LEFT])
        y = random.random() * -500 - 200 - top_gear.radius + top_gear.position.y
        if side != favor_side:
            y -= 200
        y -= 500

        x = c.CHAMBER_LEFT if side == c.LEFT else c.CHAMBER_RIGHT
        new_gear = Gear(self, random.choice([c.BIG, c.BIG, c.SMALL]),(x, y))
        dir = c.LEFT if side is c.RIGHT else c.RIGHT
        new_gear_2 = new_gear.make_child(dir)
        self.gears.append(new_gear)
        self.gears.append(new_gear_2)

    def spawn_new_platform(self, top_platform):
        x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT
        y = top_platform.position.y - (random.random() * 300 + 100)
        new_platform = Platform(self, (x, y))
        if random.random() < 0.2:
            new_platform = Enemy(self, (random.random() * c.CHAMBER_WIDTH * 0.75 + c.CHAMBER_LEFT + c.CHAMBER_WIDTH*0.125, y))
        self.platforms.append(new_platform)

    def refill_sparks(self):
        if not self.sparks:
            x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT
            new_spark = Spark(self, (x, c.WINDOW_HEIGHT + 200))
            self.sparks.append(new_spark)
        highest = self.sparks[-1]
        while highest.get_apparent_y() > -20:
            x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT
            new_spark = Spark(self, (x, highest.position.y - random.random() * 5 - 5))
            self.sparks.append(new_spark)
            new_spark.update(0, [])
            highest = new_spark


        #FOREGROUND SPARKS
        if not self.foreground_sparks:
            x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT
            new_spark = Spark(self, (x, 0),foreground=True)
            new_spark.position.y -= (new_spark.get_apparent_y() * new_spark.parallax)
            new_spark.position.y += (c.WINDOW_HEIGHT + 20) * new_spark.parallax
            self.foreground_sparks.append(new_spark)
        self.foreground_sparks.sort(key=lambda x: -x.position.y)
        highest = self.foreground_sparks[-1]
        while highest.get_apparent_y() > -50:
            x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT
            new_spark = Spark(self, (x, highest.position.y - random.random() * 10 - 40), foreground=True)
            self.foreground_sparks.append(new_spark)
            new_spark.update(0, [])
            highest = new_spark

    def draw_sides(self, surface, offset=(0, 0)):
        left = c.CHAMBER_LEFT + offset[0]
        right = c.CHAMBER_RIGHT + offset[0]
        pygame.draw.rect(surface,c.BLACK,(0, 0, left, c.WINDOW_HEIGHT))
        pygame.draw.rect(surface, c.BLACK, (right, 0, left, c.WINDOW_HEIGHT))

    def slowdown(self):
        self.sim_speed = 1

    def draw_background(self, surface, offset=(0, 0)):
        left = c.CHAMBER_LEFT + offset[0]
        surface.blit(self.gradient, (left, 0))

        x = c.WINDOW_WIDTH//2 - self.background_detail.get_width()//2
        y = ((int(self.height * 0.25 + offset[1])) % self.background_detail.get_height()) - self.background_detail.get_height()
        while y < c.WINDOW_HEIGHT:
            surface.blit(self.background_detail, (x, y), special_flags=pygame.BLEND_MULT)
            #surface.blit(self.background_edge, (x, y), special_flags=pygame.BLEND_ADD)
            y += self.background_detail.get_height()

    def draw(self, surface, offset=(0, 0)):
        offset = (Pose(offset) + Pose(self.get_shake_offset())).get_position()
        self.draw_background(surface, offset)
        if self.flare_alpha > 0:
            self.flare.set_alpha(self.flare_alpha)
            surface.blit(self.flare, (offset[0] + c.CHAMBER_LEFT, 0))
        for gear in self.gears:
            gear.draw(surface, offset)
        for spark in self.sparks:
            spark.draw(surface, offset)
        for platform in self.platforms:
            platform.draw(surface, offset)
        self.player.draw(surface, offset)
        for explosion in self.explosions:
            explosion.draw(surface, offset)
        for spark in self.foreground_sparks:
            spark.draw(surface, offset)
        self.draw_sides(surface, offset)