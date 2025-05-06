import pygame
from .base import BaseState
class Tutorial(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MENU"
        
        self.color = (255,255,255)
        self.full_text = [
        "W A S D To MOVE",

        "Left Click To SHOOT",

        "LSHIFT To DODGE",

        "[Press SPACE to go back]"
        ]
        self.rendered_lines = []
        self.current_line_index = len(self.full_text)
        self.line_positions = []
        for i, line in enumerate(self.full_text):
            rendered = self.font.render(line, False, self.color)
            self.rendered_lines.append(rendered)
            pos_y = self.screen_rect.height // 3 + i * 30
            self.line_positions.append((self.screen_rect.centerx - rendered.get_width() // 2, pos_y))

    
    def startup(self, persistent):
        self.persist = persistent

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.done = True

    def draw(self, surface):
        surface.fill((0,0,0))
        for i in range(self.current_line_index):
            surface.blit(self.rendered_lines[i], self.line_positions[i])