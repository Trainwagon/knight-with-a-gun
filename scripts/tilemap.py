from pytmx.util_pygame import load_pygame
import pygame
from scripts.settings import TILE_SIZE
from scripts.collision import CollisionSprite
from scripts.collision import Sprite

class TileMap:
    def __init__(self, filename, all_sprites, collision_sprites):
        self.tmx_data = load_pygame(filename)
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites

        self.load_collision_layer('Collisions')
        self.load_sprite_layers([
            'Lowest',
            'Below',
            'Ground',
            'Outer',
            'Walls',
            'Env'
        ])

    def load_collision_layer(self, layer_name):
        for obj in self.tmx_data.get_layer_by_name(layer_name):
            surf = pygame.Surface((obj.width, obj.height))
            CollisionSprite((obj.x, obj.y), surf, self.collision_sprites)

    def load_sprite_layers(self, layer_names):
        for layer_name in layer_names:
            for x, y, image in self.tmx_data.get_layer_by_name(layer_name).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)