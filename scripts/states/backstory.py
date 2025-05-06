import pygame
from .base import BaseState
import os

class Backstory(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "MENU"
        self.time_active = 0
        
        # Font setup
        try:
            self.font = pygame.font.Font(self.font_path, 20)
        except:
            self.font = pygame.font.Font(None, 20)
        
        # Typewriter settings
        self.typing_speed = 0.04  # seconds per character
        self.time_per_char = 0.04
        self.time_since_last_char = 0
        self.current_line_index = 0
        self.current_char_index = 0
        self.finished_typing = False
        
        # The backstory text as a list of lines
        self.lines = [
            "Finally, after a long journey...",
            "I've come to the end of this hell.",
            # "",
            # "The ancient eye that haunts these lands",
            # "has taken everything from me.",
            # "",
            # "With nothing but my sword and gun,",
            # "I stand ready for the final battle.",
            # "",
            # "This ends today.",
            # "",
            "[Press SPACE to continue]"
        ]
        
        # Pre-render complete lines for faster display
        self.rendered_lines = []
        self.line_positions = []
        
        for i, line in enumerate(self.lines):
            rendered = self.font.render(line, True, (255, 255, 255))
            self.rendered_lines.append(rendered)
            pos_y = self.screen_rect.height // 3 + i * 30
            self.line_positions.append((self.screen_rect.centerx - rendered.get_width() // 2, pos_y))
    
    def startup(self, persistent):
        self.persist = persistent
        # Reset typewriter
        self.time_active = 0
        self.time_since_last_char = 0
        self.current_line_index = 0
        self.current_char_index = 0
        self.finished_typing = False
    
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # If still typing, finish typing immediately
                if not self.finished_typing:
                    self.finished_typing = True
                    self.current_line_index = len(self.lines)
                # If already finished typing, proceed to next state
                else:
                    self.done = True
    
    def update(self, dt):
        self.time_active += dt
        
        if not self.finished_typing:
            self.time_since_last_char += dt
            
            # Time to show next character
            if self.time_since_last_char >= self.time_per_char:
                self.time_since_last_char = 0
                
                # Advance to next character
                self.current_char_index += 1
                
                # If reached end of current line
                if self.current_line_index < len(self.lines) and self.current_char_index > len(self.lines[self.current_line_index]):
                    self.current_line_index += 1
                    self.current_char_index = 0
                
                # If we've typed all lines
                if self.current_line_index >= len(self.lines):
                    self.finished_typing = True
    
    def draw(self, surface):
        # Fill with black background
        surface.fill((0, 0, 0))
        
        # If typing is finished, show all lines
        if self.finished_typing:
            for i, line in enumerate(self.rendered_lines):
                surface.blit(line, self.line_positions[i])
        else:
            # Draw completed lines
            for i in range(self.current_line_index):
                surface.blit(self.rendered_lines[i], self.line_positions[i])
            
            # Draw current line in progress
            if self.current_line_index < len(self.lines):
                current_text = self.lines[self.current_line_index][:self.current_char_index]
                current_render = self.font.render(current_text, True, (255, 255, 255))
                pos_x = self.screen_rect.centerx - self.rendered_lines[self.current_line_index].get_width() // 2
                pos_y = self.line_positions[self.current_line_index][1]
                surface.blit(current_render, (pos_x, pos_y))