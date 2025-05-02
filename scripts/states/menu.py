import pygame
from .base import BaseState

class Menu(BaseState):
    def __init__(self):
        super().__init__()
        self.background = pygame.image.load(self.background_path).convert_alpha()
        self.active_index = 0
        self.options = ['Start Game', "Quit Game"]
        self.next_state = "GAMEPLAY"

    def render_text(self, index):
        if index == self.active_index:
            color = (255, 255, 255)
            alpha = 255
        else:
            color = (255, 255, 255)
            alpha = 120
         # Render text ke Surface
        text_surf = self.font.render(self.options[index], True, color).convert_alpha()
        text_surf.set_alpha(alpha)
        return text_surf
    
    def get_text_pos(self, text, index):
        # x = self.screen_rect.centerx
        # y = self.screen_rect.centery + index * 20  # range between options (x) px
        # return text.get_rect(center=(x, y))
        margin_x = 30
        margin_y = self.screen_rect.height - (len(self.options) - index) * 50
        return text.get_rect(topleft=(margin_x, margin_y))
    
    def handle_action(self):
        if self.active_index == 0:
            self.done = True
        elif self.active_index == 1:
            self.quit = True

    def get_event(self, event):
            pygame.mouse.set_visible(True)
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for index, option in enumerate(self.options):
                    text_render = self.render_text(index)
                    text_rect = self.get_text_pos(text_render, index)
                    if text_rect.collidepoint(mouse_pos):
                        self.active_index = index
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_action()

    def draw(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.background, (0, 0))
        for index, option in enumerate(self.options):
            text_render = self.render_text(index)
            text_rect = self.get_text_pos(text_render, index)
            surface.blit(text_render, text_rect)

            # Tambah cursor panah di option yang aktif
            if index == self.active_index:
                cursor = self.font.render(">", True, (255, 255, 255))
                cursor_rect = cursor.get_rect()
                cursor_rect.midright = (text_rect.left - 10, text_rect.centery)
                surface.blit(cursor, cursor_rect)
                