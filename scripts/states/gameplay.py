import pygame
from .base import BaseState
from scripts.player import Player



class Gameplay(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "GAME_OVER"

        # Sprite Group
        self.all_sprites = pygame.sprite.Group()

        # Player
        self.player = Player(pos=self.screen_rect.center)
        self.all_sprites.add(self.player)


    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.done = True

    def update(self, dt):
        self.all_sprites.update(dt)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.all_sprites.draw(surface)
            