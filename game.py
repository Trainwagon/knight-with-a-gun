import pygame
import math, random, os, sys

from pytmx.util_pygame import load_pygame

# scripts dir
from scripts.player import Player
from scripts.settings import *


class Game:
    def __init__(self, screen, states, start_state):
        # setup
        self.clock = pygame.time.Clock()
        self.done = False
        self.screen = screen
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]

        # setup fps
        font_path = os.path.join('data', 'homespun.ttf')
        self.font = pygame.font.Font(font_path, 16)
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.1f}", False, (255, 255, 255))  # Putih
        self.screen.blit(fps_text, (10, 10))  # posisi di pojok kiri atas

    def event_loop(self):
         for event in pygame.event.get():
            self.state.get_event(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): # ganti ini nanti kalo udah ada menu escape jangan buat quit
                pygame.quit()
                sys.exit()

    def flip_state(self):
        current_state = self.state_name
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        persistent = self.state.persist
        self.state = self.states[self.state_name]
        self.state.startup(persistent)

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(dt)

    def draw(self):
        self.state.draw(self.screen)

        # FPS Counter
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {math.floor(fps)}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))

    def run(self):
        while not self.done:
            # delta time for fps independence
            dt = self.clock.tick(FPS) / 1000

            # event loop
            self.event_loop()
            self.update(dt)
            self.draw()
            
            # update
            pygame.display.update()


