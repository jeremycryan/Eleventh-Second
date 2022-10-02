import pygame
import constants as c
from enemy import Enemy
from explosion import Explosion
from hook import Hook
from image_manager import ImageManager
from gear import Gear
from primitives import Pose
import random

from sound_manager import SoundManager
from spark import Spark
from player import Player
import math

from platform_thing import PlatformThing
from timestepper import Timestepper

import sys


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


class TitleFrame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.surf = ImageManager.load("assets/images/title.png")
        self.age = 0
        self.pre_age = 0
        self.music_playing = False
        self.ending = False


    def update(self, dt, events):
        self.pre_age += dt
        if self.pre_age > 0.5:
            if not self.ending:
                self.age += dt
            else:
                self.age -= dt

            if self.age > 2:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if not self.ending:
                                self.ending = True
                                self.age = 0.3

        if self.ending and self.age < 0:
            self.done = True

    def draw(self, surface, offset=(0, 0)):
        self.surf.set_alpha(min(255, self.age * 500))
        surface.fill((0, 0, 0))
        surface.blit(self.surf, (0, 0))
        if self.age > 2:
            if self.age % 1 < 0.5:
                enter = ImageManager.load("assets/images/press_enter.png")
                surface.blit(enter, (c.WINDOW_WIDTH//2 - enter.get_width()//2 - 15, c.WINDOW_HEIGHT - enter.get_height()), special_flags=pygame.BLEND_ADD)

    def next_frame(self):
        return IntroFrame(self.game)


class IntroFrame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.surf = ImageManager.load("assets/images/intro.png")
        self.age = 0
        self.pre_age = 0
        self.music_playing = False
        self.ending = False


    def update(self, dt, events):
        self.pre_age += dt
        if self.pre_age > 0.5:
            if not self.ending:
                self.age += dt
            else:
                self.age -= dt

            if self.age > 2:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if not self.ending:
                                self.ending = True
                                self.age = 0.3

        if self.ending and self.age < 0:
            self.done = True

    def draw(self, surface, offset=(0, 0)):
        self.surf.set_alpha(min(255, self.age * 500))
        surface.fill((0, 0, 0))
        surface.blit(self.surf, (0, 0))
        if self.age > 2:
            if self.age % 1 < 0.5:
                enter = ImageManager.load("assets/images/press_enter.png")
                surface.blit(enter, (c.WINDOW_WIDTH//2 - enter.get_width()//2, c.WINDOW_HEIGHT - enter.get_height()))

    def next_frame(self):
        return Intro2Frame(self.game)

class Intro2Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.surf = ImageManager.load("assets/images/intro2.png")
        self.age = 0
        self.pre_age = 0
        self.music_playing = False
        self.ending = False


    def update(self, dt, events):
        self.pre_age += dt
        if self.pre_age > 0.5:
            if not self.ending:
                self.age += dt
            else:
                self.age -= dt

            if self.age > 2:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if not self.ending:
                                self.ending = True
                                self.age = 0.3

        if self.ending and self.age < 0:
            self.done = True

    def draw(self, surface, offset=(0, 0)):
        self.surf.set_alpha(min(255, self.age * 500))
        surface.fill((0, 0, 0))
        surface.blit(self.surf, (0, 0))
        if self.age > 2:
            if self.age % 1 < 0.5:
                enter = ImageManager.load("assets/images/press_enter.png")
                surface.blit(enter, (c.WINDOW_WIDTH//2 - enter.get_width()//2, c.WINDOW_HEIGHT - enter.get_height()))

    def next_frame(self):
        return GameFrame(self.game)


class WinFrame:
    def __init__(self, game):
        self.game = game
        self.done = False
        pygame.mixer.music.fadeout(1000)

    def load(self):
        self.surf = ImageManager.load("assets/images/win.png")
        self.age = 0
        self.pre_age = 0
        self.music_playing = False


    def update(self, dt, events):
        self.pre_age += dt
        if self.pre_age > 4:
            self.age += dt
            if not self.music_playing:
                self.music_playing = True
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)

            if self.age > 2:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            pygame.quit()
                            sys.exit()

    def draw(self, surface, offset=(0, 0)):
        self.surf.set_alpha(min(255, self.age * 500))
        surface.fill((255, 255, 255))
        surface.blit(self.surf, (0, 0))
        if self.age > 2:
            if self.age % 1 < 0.5:
                enter = ImageManager.load("assets/images/enter_to_close.png")
                surface.blit(enter, (c.WINDOW_WIDTH//2 - enter.get_width()//2, c.WINDOW_HEIGHT - enter.get_height()))

    def next_frame(self):
        return GameFrame(self.game)


class GameFrame(Frame):

    def load(self):
        self.height = 0

        self.gradient = ImageManager.load("assets/images/gradient.png")
        self.gradient = pygame.transform.scale(self.gradient, (c.CHAMBER_WIDTH, c.WINDOW_HEIGHT))
        self.rewinding_gradient = ImageManager.load("assets/images/rewinding_gradient.png")
        self.rewinding_gradient = pygame.transform.scale(self.rewinding_gradient, (c.CHAMBER_WIDTH, c.WINDOW_HEIGHT))
        self.background_detail = ImageManager.load("assets/images/background_detail.png")
        self.background_edge = ImageManager.load("assets/images/background_detail_edge.png")

        self.gear_1 = Gear(self, c.BIG,(c.CHAMBER_LEFT, c.WINDOW_HEIGHT/2))
        self.gear_2 = self.gear_1.make_child(c.RIGHT)
        self.gears = [self.gear_1, self.gear_2]
        self.sparks = []
        self.foreground_sparks = []
        self.platforms = [PlatformThing(self, (c.WINDOW_WIDTH//2  + random.random() * 200 - 100, 120), tutorial=True),
                          Enemy(self, (c.WINDOW_WIDTH//2 + random.random() * 250 - 200, -1100)),
                          Enemy(self, (c.WINDOW_WIDTH // 2 + random.random() * 250 - 200, -1850)),
                          PlatformThing(self, (c.WINDOW_WIDTH//2 + random.random() * 200 - 100, -3000))]
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
        self.time_left = 10
        self.age = 0
        self.age_no_shenanigans = 0

        self.timer_font_big = pygame.font.Font("assets/fonts/7seg.ttf",80)
        self.timer_font_small = pygame.font.Font("assets/fonts/7seg.ttf", 25)
        self.height_font = pygame.font.Font("assets/fonts/voyager_heavy.otf", 50)
        self.meters_font = pygame.font.Font("assets/fonts/voyager_heavy.otf", 25)

        if not self.game.music_has_started:
            self.game.music_has_started = True
            pygame.mixer.music.load("assets/sounds/ld51.ogg")
            pygame.mixer.music.play(-1)

        self.wind_sound = pygame.mixer.Sound("assets/sounds/wind.wav")
        self.wind_sound.play(-1)
        self.wind_sound.set_volume(0)
        self.wind_sound_target = 0

        self.stepper = Timestepper(self)

        self.rewinding = False
        self.since_rewind = 0

        self.since_enemy = 0

        self.big_boi = ImageManager.load("assets/images/big_boi.png")

        self.shade = self.rewinding_gradient.copy()
        self.shade.fill((219, 0, 0))

        self.original_passed_times = [0.01, 5, 6, 7, 8, 8.5, 9, 9.25, 9.5, 9.6, 9.7, 9.8, 9.9, 9.95]
        self.passed_times = self.original_passed_times.copy()

        self.score_position = Pose((1071, 65))
        self.score_target = self.score_position.copy()

        self.black_cover = pygame.Surface((c.WINDOW_SIZE))
        self.black_cover.fill((0, 0, 0))

        self.black_cover_2 = self.black_cover.copy()
        self.black_cover_2_alpha_target = 0
        self.black_cover_2_alpha = 255

        self.tutorial_shade = self.black_cover.copy()
        self.tutorial_shade_alpha = 0
        self.tutorial_shade_alpha_target = 0

        self.since_player_dead = 0

        self.ending = False
        self.has_grappled = False
        self.has_collected = False
        self.has_grabbed_enemy = False

        self.since_tick = 999
        self.won = False

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
        self.age_no_shenanigans += dt
        slowdown = 1

        if not self.player.dead and self.height/100 > 1000:
            self.win()

        if not self.player.dead and not self.ending:
            if not self.has_grappled and self.player.velocity.y > -150:
                slowdown = 5
                dt *= 1/slowdown
            elif not self.has_grabbed_enemy and self.has_collected and self.player.velocity.y > -150:
                slowdown = 5
                dt *= 1/slowdown
                for platform in sorted(self.platforms, key=lambda x: (x.position - self.player.position).magnitude()):
                    if isinstance(platform, Enemy):
                        platform.tutorial = True
                        break
        self.slowdown_amt = slowdown
        if self.sim_speed < 1:
            self.sim_speed += 5*dt
            if self.sim_speed > 1:
                self.sim_speed = 1
        dt *= self.sim_speed
        self.shake_time += dt

        if self.ending:
            if self.black_cover_2_alpha >= 255:
                self.done = True
                return
            else:
                self.black_cover_2_alpha += 500*dt
        else:
            self.black_cover_2_alpha_target = 0
            if self.black_cover_2_alpha > self.black_cover_2_alpha_target:
                self.black_cover_2_alpha -= 1000 * dt
            if self.black_cover_2_alpha < 0:
                self.black_cover_2_alpha = 0
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.ending = True

        if slowdown > 1:
            self.tutorial_shade_alpha_target = 150
            self.tutorial_shade_alpha += dt * 2000
            if self.tutorial_shade_alpha > self.tutorial_shade_alpha_target:
                self.tutorial_shade_alpha = self.tutorial_shade_alpha_target
        else:
            self.tutorial_shade_alpha -= 2000*dt
            if self.tutorial_shade_alpha < 0:
                self.tutorial_shade_alpha = 0

        if self.player.dead:

            self.since_player_dead += dt
            self.score_target = Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2))
            self.score_position += (self.score_target - self.score_position - Pose((self.height_surf.get_width()//2, self.height_surf.get_height()//2))) * dt * 5

        if not self.rewinding:
            pygame.mixer.music.set_volume(1)
            self.since_tick = 5
        else:
            self.since_tick += dt
            if self.since_tick > 0.2:
                self.since_tick = 0
                sound = SoundManager.load("assets/sounds/tick.wav")
                sound.set_volume(0.25)
                sound.play()
            pygame.mixer.music.set_volume(0.06 + 0.94 * self.rewind_intensity())
        if self.passed_times:
            if (10 - self.time_left) > self.passed_times[0]:
                beep = SoundManager.load("assets/sounds/beep.wav")
                beep.set_volume(0.2)
                beep.play()
                self.passed_times.pop(0)
        self.age += dt
        if self.rewinding:
            self.since_rewind += dt
            amt = 10 - self.time_left
            time_to_do = 2 - self.since_rewind
            self.time_left += amt/time_to_do * dt
            if self.since_rewind > 2:
                self.time_left = 10
                self.stop_rewinding()
        if self.age > 2:
            if not self.player.dead:
                if self.time_left < 0.25:
                    self.time_left -= dt * 0.5
                elif self.time_left < 1:
                    self.time_left -= dt * 0.75
                elif self.time_left < 2:
                    self.time_left -= dt * 0.88
                else:
                    self.time_left -= dt
                if self.time_left < 0:
                    self.time_left = 0

        if self.time_left <= 0:
            self.bomb_go_off()

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
        speed = 0
        if dy > 0:
            speed = dy**2 * 0.2
            self.height += speed * dt
        self.wind_sound_target = min(0.5, speed/500)
        wind_sound_current = self.wind_sound.get_volume()
        d = self.wind_sound_target - wind_sound_current
        if d < 0:
            self.wind_sound.set_volume(wind_sound_current + d*dt*5)
        else:
            self.wind_sound.set_volume(wind_sound_current + d * dt * 3)
        factor = 1
        if self.rewinding:
            factor = max(0.2, self.rewind_intensity())

        self.player.update(dt*factor, events)
        self.stepper.update(dt, events)

        self.gears.sort(key=lambda x: x.get_apparent_y())
        if self.gears:
            top_gear = self.gears[0]
            if top_gear.get_apparent_y() > 0:
                self.spawn_new_gear_set(top_gear)

        for gear in self.gears[:]:
            if not self.rewinding:
                gear.update(dt, events)
            else:
                gear.update(-dt, events)
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
            top_platform = PlatformThing(self, (0, c.WINDOW_HEIGHT))
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
                self.stepper.get_charge()
                if self.stepper.full():
                    self.rewind()

        for explosion in self.explosions[:]:
            explosion.update(dt, events)
            if explosion.get_apparent_y() - explosion.radius * 2 > c.WINDOW_HEIGHT:
                self.explosions.remove(explosion)
            elif explosion.destroyed:
                self.explosions.remove(explosion)

        self.refill_sparks()

    def bomb_go_off(self):
        self.player.die()

    def win(self):
        self.won = True
        self.ending = True
        self.black_cover_2.fill((255, 255, 255))

    def rewind(self):
        self.rewinding = True
        self.since_rewind = 0
        self.bbpos = self.player.position.x - self.big_boi.get_width()//2, self.player.get_apparent_y() - self.big_boi.get_height()//2
        self.stepper.charges = 0
        sound = SoundManager.load("assets/sounds/timestep.wav")
        sound.set_volume(0.2)
        sound.play()

    def stop_rewinding(self):
        self.rewinding = False
        self.age = 1
        self.passed_times = self.original_passed_times.copy()

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

    def rewind_intensity(self):
        if not self.rewinding:
            return 0
        else:
            return max(0, 2*(self.since_rewind - 1.5))

    def spawn_new_platform(self, top_platform):
        x = random.random() * c.CHAMBER_WIDTH + c.CHAMBER_LEFT

        enemy_chance = 1
        height = self.height/100
        if height < 35:
            enemy_chance = 1
        if height < 300:
            enemy_chance = 0.4
        elif height < 800:
            enemy_chance = 0.25
        elif height < 1000:
            enemy_chance = 0.2
        else:
            enemy_chance = 0.15

        if self.since_enemy != 0:
            if 1/self.since_enemy < enemy_chance:
                enemy_chance = 1

        height_min = 100
        height_var = 300 + 200 * self.height/1000/50

        y = top_platform.position.y - (random.random() * height_var + height_min)

        new_platform = PlatformThing(self, (x, y))

        print(enemy_chance)
        if random.random() < enemy_chance:
            new_platform = Enemy(self, (random.random() * c.CHAMBER_WIDTH * 0.75 + c.CHAMBER_LEFT + c.CHAMBER_WIDTH*0.125, y))
            self.since_enemy = 0
        else:
            self.since_enemy += 1
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

        clock = ImageManager.load("assets/images/seconds_until_detonation.png")
        seconds_text = f"{int(self.time_left)}."
        decimal_text = f"{round(self.time_left - int(self.time_left), 2)}"
        if "." in decimal_text:
            decimal_text = decimal_text.split(".")[1]
        while len(decimal_text) < 2:
            decimal_text += "0"
        color = 255, 0, 0
        if self.rewinding:
            color = 30, 80, 255
        seconds = self.timer_font_big.render(seconds_text,1,(color))
        decimal = self.timer_font_big.render(decimal_text, 1, (color))

        clock = clock.copy()
        filter = clock.copy()
        filter.fill((color))
        clock.blit(filter, (0, 0), special_flags=pygame.BLEND_MULT)
        surface.blit(clock, (c.CHAMBER_LEFT/2 - clock.get_width()/2, 130))
        x = 166
        y = 90
        surface.blit(seconds, (c.CHAMBER_LEFT/2 - seconds.get_width() - 5, 50))
        surface.blit(decimal, (c.CHAMBER_LEFT/2 - 5, 50))

        surface.blit(ImageManager.load("assets/images/timekeepers_tower.png"), (1071, 56))

        height_text = f"{int(self.height/100)}"
        height_surf = self.height_font.render(height_text, 1, (255, 255, 255))
        self.height_surf = height_surf

        if self.player.dead:
            self.black_cover.set_alpha(min(self.since_player_dead * 400, 196))
            surface.blit(self.black_cover, (0, 0))
            if self.age%1 < 0.7:
                r = ImageManager.load("assets/images/r_to_restart.png")
                surface.blit(r, (c.WINDOW_WIDTH//2 - r.get_width()//2, c.WINDOW_HEIGHT - r.get_height() - 10))

        color = min(255, 128 + 128*(min(self.since_player_dead*3, 1)))
        surface.blit(self.meters_font.render("FT", 1, (color, color, color)), (self.score_position + Pose((height_surf.get_width() + 3, 23))).get_position())
        surface.blit(height_surf, self.score_position.get_position())





        self.stepper.draw(surface, (0, 0))

    def slowdown(self):
        self.age = 0

    def draw_background(self, surface, offset=(0, 0)):
        left = c.CHAMBER_LEFT + offset[0]
        if not self.rewinding or self.rewind_intensity() > 0:
            surface.blit(self.gradient, (left, 0))
        if self.rewinding:
            opacity = 255 * (1 - self.rewind_intensity())
            self.rewinding_gradient.set_alpha(opacity)
            surface.blit(self.rewinding_gradient, (left, 0))

        x = c.WINDOW_WIDTH//2 - self.background_detail.get_width()//2
        y = ((int(self.height * 0.25 + offset[1])) % self.background_detail.get_height()) - self.background_detail.get_height()
        while y < c.WINDOW_HEIGHT:
            surface.blit(self.background_detail, (x, y), special_flags=pygame.BLEND_MULT)
            #surface.blit(self.background_edge, (x, y), special_flags=pygame.BLEND_ADD)
            y += self.background_detail.get_height()

    def draw(self, surface, offset=(0, 0)):
        offset = (Pose(offset) + Pose(self.get_shake_offset())).get_position()
        self.draw_background(surface, offset)
        if self.rewinding:
            self.flare_alpha = 90 - 90*self.rewind_intensity()
        if self.flare_alpha > 0:
            self.flare.set_alpha(self.flare_alpha)
            surface.blit(self.flare, (offset[0] + c.CHAMBER_LEFT, 0))
        for gear in self.gears:
            gear.draw(surface, offset)
        if not self.rewinding:
            alpha = 128 * ((1 - self.time_left/10) **2)
            self.shade.set_alpha(int(alpha))
            surface.blit(self.shade, (c.CHAMBER_LEFT, 0))
        for spark in self.sparks:
            spark.draw(surface, offset)
        if self.tutorial_shade_alpha > 0:
            self.tutorial_shade.set_alpha(self.tutorial_shade_alpha)
            surface.blit(self.tutorial_shade, (c.CHAMBER_LEFT, 0))
        for platform in self.platforms:
            platform.draw(surface, offset)
        if self.rewinding:
            alpha = (1 - self.since_rewind)*128
            self.big_boi.set_alpha(alpha)
            surface.blit(self.big_boi, (self.bbpos))
        self.player.draw(surface, offset)
        for explosion in self.explosions:
            explosion.draw(surface, offset)
        for spark in self.foreground_sparks:
            spark.draw(surface, offset)
        self.draw_sides(surface, offset)
        if self.black_cover_2_alpha > 0:
            self.black_cover_2.set_alpha(self.black_cover_2_alpha)
            surface.blit(self.black_cover_2, (0, 0))

    def next_frame(self):
        if self.won:
            self.wind_sound.fadeout(500)
            return WinFrame(self.game)
        return GameFrame(self.game)