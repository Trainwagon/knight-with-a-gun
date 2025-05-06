import pygame
import sys
from .base import BaseState
from os.path import join

class GameOver(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "GAMEPLAY"
        self.options = ["Restart", "Main Menu", "Quit"]
        self.selected_option = 0
        
        # Load font
        try:
            font_path = join('data', 'homespun.ttf')
            self.font = pygame.font.Font(font_path, 24)  # Increased font size
            self.title_font = pygame.font.Font(font_path, 36)  # Increased title font size
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
    
    def startup(self, persistent):
        self.persist = persistent
        self.selected_option = 0
        self.game_won = persistent.get('victory', False)
    
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:  # Fixed the comparison
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:  # Fixed the comparison
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.execute_option()
        
        # Handle mouse motion for menu option selection
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            menu_y_start = self.screen_rect.height // 4 + 80  # Approximate position based on title + subtitle
            for i, option in enumerate(self.options):
                # Calculate text position to check collision
                text = self.font.render(option, True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen_rect.width // 2, menu_y_start + i * 30))
                if text_rect.collidepoint(mouse_pos):
                    self.selected_option = i
        
        # Handle mouse click for option selection
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self.execute_option()
    
    def execute_option(self):
        option = self.options[self.selected_option]
        if option == "Restart":
            self.persist['restart'] = True
            self.next_state = "GAMEPLAY"
            self.done = True
        elif option == "Main Menu":
            self.next_state = "MENU"
            self.done = True
        elif option == "Quit":
            pygame.quit()
            sys.exit()
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        surface.fill((0, 0, 0))
        
        # Draw game over message
        if self.game_won:
            title = self.title_font.render("At long last...", True, (255, 215, 0))  # Gold color
            subtitle = self.font.render("You, finally escaped hell", True, (255, 255, 255))
        else:
            title = self.title_font.render("GAME OVER", True, (255, 0, 0))
            subtitle = self.font.render("You were defeated...", True, (255, 255, 255))
        
        # Center the title text
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() // 4))  # Moved up
        surface.blit(title, title_rect)
        
        # Draw subtitle
        subtitle_rect = subtitle.get_rect(center=(surface.get_width() // 2, title_rect.bottom + 20))
        surface.blit(subtitle, subtitle_rect)
        
        # Draw menu options
        menu_y_start = subtitle_rect.bottom + 30  # Reduced vertical spacing
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, menu_y_start + i * 30))  # Reduced spacing between options
            surface.blit(text, text_rect)
        
        # Draw custom cursor
        from scripts.AssetLoader import custom_cursor
        custom_cursor(surface)