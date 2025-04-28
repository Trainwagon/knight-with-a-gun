import pygame
from .base import BaseState
from scripts.player import Player
from scripts.settings import *
from random import randint
from scripts.tilemap import TileMap
from os.path import join
from scripts.collision import CollisionSprite
from scripts.AssetLoader import custom_cursor
from scripts.camera import Camera

class Gameplay(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "GAME_OVER"

        self.camera = Camera(WIDTH, HEIGHT)

        # Sprite Group
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprite = pygame.sprite.Group()

        # load map
        self.tilemap = TileMap(filename=join('data', 'maps', '0.tmx'),
                               all_sprites=self.all_sprites,
                               collision_sprites=self.collision_sprite)

        # Player
        self.player = Player(self.screen_rect.center, self.all_sprites, self.collision_sprite)
        

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.done = True

    def update(self, dt):
        self.all_sprites.update(dt)
        self.camera.update(self.player.rect)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        for sprite in self.all_sprites:
            surface.blit(sprite.image, self.camera.apply(sprite.rect))
        custom_cursor(surface)
                              