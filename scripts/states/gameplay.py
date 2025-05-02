import pygame
from .base import BaseState
from scripts.player import Player
from scripts.settings import *
from scripts.tilemap import TileMap
from os.path import join
from scripts.AssetLoader import custom_cursor
from scripts.camera import Camera

class Gameplay(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "GAME_OVER"
        # Sprite Group
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # load map
        self.tilemap = TileMap(filename=join('data', 'maps', '0.tmx'),
                               all_sprites=self.all_sprites,
                               collision_sprites=self.collision_sprites,
                               water_sprites=self.water_sprites)
        
        map_width = self.tilemap.tmx_data.tilewidth * self.tilemap.tmx_data.width
        map_height = self.tilemap.tmx_data.tileheight * self.tilemap.tmx_data.height
        self.camera = Camera(WIDTH, HEIGHT, map_width, map_height)

        # Player
        spawn_pos = self.tilemap.get_entity_pos('player')
        self.player = Player(spawn_pos, self.all_sprites, self.collision_sprites, self.water_sprites, self.camera)
        
        # Paksa kamera langsung ke posisi player saat awal
        self.camera.update(self.player.rect)
        
        # boss
        # boss_pos = self.tilemap.get_entity_position('Boss')
        # self.boss = Boss(boss_pos, self.all_sprites, self.collision_sprite)

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

        self.player.draw(surface, self.camera)
        custom_cursor(surface)
                              