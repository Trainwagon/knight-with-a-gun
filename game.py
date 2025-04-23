import pygame
import math, random, os, sys

from pytmx.util_pygame import load_pygame

# scripts dir
from scripts.player import Player
from scripts.settings import *

class Game():
    def __init__(self):
        # setup
        pygame.init()
        pygame.display.set_caption('Cursed Arcade')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT),
                                              pygame.FULLSCREEN|pygame.SCALED)
        self.clock = pygame.time.Clock()

        self.player = Player(pos=(WIDTH // 2, HEIGHT // 2))
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

    def run(self):
        while True:
            # delta time for fps independence
            dt = self.clock.tick(FPS) / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): # ganti ini nanti kalo udah ada menu escape jangan buat quit
                    pygame.quit()
                    sys.exit()
            
            # update
            self.all_sprites.update(dt)
            # draw
            self.screen.fill((30, 30, 30))  # background color
            self.all_sprites.draw(self.screen)
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()

