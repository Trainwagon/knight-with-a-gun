import pygame
from .base import BaseState


class Splash(BaseState):
    def __init__(self):
        super().__init__()
        self.title_base = "Knight With A Gun"
        self.title = self.font.render(self.title_base, False, (255, 255, 255))
        self.title_rect = self.title.get_frect(center=self.screen_rect.center)
        
        self.skip_text = self.font.render("Press Space to Skip", False, (200, 200, 200))
        self.skip_rect = self.skip_text.get_rect(center=(self.screen_rect.centerx, self.screen_rect.centery + 30))

        self.next_state = "MENU"
        self.time_active = 0
        self.dot_timer = 0
        self.dot_count = 0
        
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.done = True


    def update(self, dt):
        self.time_active += dt
        self.dot_timer += dt
        
        # update loading dots every 0.5 secs
        if self.dot_timer >= 0.5:
            self.dot_timer = 0
            self.dot_count = (self.dot_count + 1) % 4 # 0,1,2,3
            loading_text = self.title_base + "." * self.dot_count
            self.title = self.font.render(loading_text, False, (255, 255, 255))
            self.title_rect = self.title.get_rect(center=self.screen_rect.center)

        # splash screen 3 seconds
        if self.time_active >= 3: 
            self.done = True
            
    def draw(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.skip_text, self.skip_rect)