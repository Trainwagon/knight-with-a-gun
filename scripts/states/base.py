import pygame
import os

class BaseState:
    def __init__(self):
        self.choosing_sound = pygame.mixer.Sound(os.path.join('data', 'sound', 'sfx', 'choosing.wav'))
        self.choosing_sound.set_volume(1)
        self.font_path = os.path.join('data', 'homespun.ttf')
        self.background_path = os.path.join('data', 'images', 'menu_back.png')
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.persist = {}
        self.font = pygame.font.Font(self.font_path, 24)

    def startup(self, persistent):
        self.persist = persistent

    def get_event(self, event):
        pass
    
    def update(self, dt):
        pass

    def draw(self, surface):
        pass