import pygame

import constants as c
import frame as f
import sys
from sound_manager import SoundManager
from image_manager import ImageManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.set_num_channels(20)
        SoundManager.init()
        ImageManager.init()
        self.screen = pygame.display.set_mode((c.WINDOW_SIZE))
        pygame.display.set_caption(c.CAPTION)
        self.clock = pygame.time.Clock()
        SoundManager.load("assets/sounds/title.wav").play()
        self.music_has_started = False
        self.main()

    def main(self):
        current_frame = f.TitleFrame(self)
        current_frame.load()
        self.clock.tick(60)

        pygame.mouse.set_cursor((1, 1), ImageManager.load("assets/images/cursor.png"))

        while True:
            dt, events = self.get_events()
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            current_frame.draw(self.screen, (0, 0))
            pygame.display.flip()
            #pygame.display.update((c.CHAMBER_LEFT - 50, 0, c.CHAMBER_WIDTH + 100, c.WINDOW_HEIGHT))

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()

    def get_events(self):
        dt = self.clock.tick(c.FRAMERATE)/1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()

        return dt, events


if __name__=="__main__":
    Game()
