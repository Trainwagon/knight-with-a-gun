import pygame
import math, os, sys


# scripts dir
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
        font_path = 'data/homespun.ttf'
        self.font = pygame.font.Font(font_path, 16)

    def event_loop(self):
        for event in pygame.event.get():
            self.state.get_event(event)
            if event.type == pygame.QUIT:
                self.done = True
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
    
    def reset_state(self):
        # Get the current state's persist data
        persistent = self.state.persist
        # Mark that we want to restart the current state
        persistent['restart'] = True
        # Reinitialize the current state
        self.state = self.states[self.state_name]
        self.state.startup(persistent)

    def update(self, dt):
        if self.state.quit:
            self.done = True
            pygame.quit()
            sys.exit()
        elif self.state.done:
            # Check if we need to restart the current state
            if self.state.persist.get('restart', False):
                self.reset_state()
                self.state.persist['restart'] = False
            else:
                self.flip_state()
        self.state.update(dt)

    def draw(self):
        self.state.draw(self.screen)

        # FPS Counter in top right corner
        # fps = self.clock.get_fps()
        # fps_text = self.font.render(f"FPS: {math.floor(fps)}", False, (255, 255, 255))
        # fps_rect = fps_text.get_rect(topright=(WIDTH - 10, 10))
        # self.screen.blit(fps_text, fps_rect)

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