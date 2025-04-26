import pygame
from .base import BaseState

class GameOver(BaseState):
    def __init__(self):
        super().__init__()
        self.title = self.font.render('Game Over', False, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.instructions = self.font.render("Press space to start again, or enter to go to the menu", False, (255, 255, 255))
        self.instructions_rect = self.instructions.get_rect(midtop=(self.screen_rect.centerx, self.screen_rect.centery + 20))

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.next_state = "MENU"
                self.done = True
            elif event.key == pygame.K_SPACE:
                self.next_state = "GAMEPLAY"
                self.done = True
            elif event.key == pygame.K_ESCAPE:
                self.quit = True


    def draw(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.instructions, self.instructions_rect)