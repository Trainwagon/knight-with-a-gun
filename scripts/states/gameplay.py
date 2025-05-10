import pygame
import sys
from .base import BaseState
from scripts.player import Player
from scripts.settings import *
from scripts.tilemap import TileMap
from os.path import join
from scripts.AssetLoader import custom_cursor
from scripts.camera import Camera
from scripts.test_boss_v6 import Boss  

class Gameplay(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "GAME_OVER"
        self.persist = {"victory": False, "restart": False}
        
        # Sprite Group
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group() 
        
        # Game state
        self.paused = False
        self.pause_options = ["Resume", "Restart", "Menu", "Quit"]
        self.selected_option = 0
        
        # Font for UI elements
        self.font_path = join('data', 'homespun.ttf')
        self.ui_font = None  # Will be initialized in startup

        # Transition effect variables
        self.transitioning = False
        self.transition_alpha = 0
        self.transition_speed = 5  # How fast the transition occurs
        
    def startup(self, persistent):
        # Background music
        pygame.mixer.music.load(join('data', 'sound', 'music', 'bg_music.wav'))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
        
        self.persist = persistent
        
        # Initialize UI font
        self.ui_font = pygame.font.Font(self.font_path, 20)
        
        # Clear any existing sprites
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.water_sprites.empty()
        self.bullets.empty()
        
        # Reset game state
        self.paused = False
        self.boss_defeated = False
        self.game_over = False
        
        # Reset transition
        self.transitioning = False
        self.transition_alpha = 0

        # load map
        self.tilemap = TileMap(filename=join('data', 'maps', '0.tmx'),
                               all_sprites=self.all_sprites,
                               collision_sprites=self.collision_sprites,
                               water_sprites=self.water_sprites)
        
        map_width = self.tilemap.tmx_data.tilewidth * self.tilemap.tmx_data.width
        map_height = self.tilemap.tmx_data.tileheight * self.tilemap.tmx_data.height
        self.camera = Camera(WIDTH, HEIGHT, map_width, map_height)

        # Player
        spawn_pos = self.tilemap.get_entity_pos('player')
        self.player = Player(spawn_pos, [self.all_sprites], self.collision_sprites, self.water_sprites, self.camera)
        
        # Force camera to player position at start
        self.camera.update(self.player.rect)
        
        # Boss - Get position from map or use default
        boss_pos = self.tilemap.get_entity_pos('boss')
        if not boss_pos:  # If no boss position in map, use center of screen
            boss_pos = (WIDTH/2, HEIGHT/1.2)
            
        # Create boss instance
        self.boss = Boss(boss_pos, [self.all_sprites], self.collision_sprites, self.player)
        
        # Game state variables
        self.boss_defeated = False
        self.game_over = False
        

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
        if self.paused:
            # Handle pause menu input
            self.handle_pause_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_pause_mouse_click(event)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                # Toggle pause state
                self.toggle_pause()
        
    def toggle_pause(self):
        self.paused = not self.paused
        # Reset selected option when opening pause menu
        if self.paused:
            self.selected_option = 0
        
    def check_collisions(self):
        # Check for player bullets hitting boss
        if hasattr(self.player, 'bullets') and hasattr(self, 'boss') and self.boss in self.all_sprites:
            for bullet in self.player.bullets:
                if self.boss.rect.colliderect(bullet.rect):
                    boss_defeated = self.boss.take_damage(bullet.damage if hasattr(bullet, 'damage') else 10)
                    bullet.kill()
                    if boss_defeated:
                        self.boss_defeated = True
                        self.start_transition()
                        
        # Check for boss bullets hitting player
        if hasattr(self.boss, 'bullets') and hasattr(self, 'player'):
            for bullet in self.boss.bullets:
                if self.player.rect.colliderect(bullet.rect):
                    player_dead = self.player.take_damage(bullet.damage if hasattr(bullet, 'damage') else 10)
                    bullet.kill()
                    if player_dead:
                        self.game_over = True
                        self.start_transition()

    def start_transition(self):
        self.transitioning = True
        self.transition_alpha = 0
    
    def update_transition(self, dt):
        if self.transitioning:
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.done = True  # Move to next state when fully faded
                pygame.mixer.music.pause()

    def update(self, dt):
        # Don't update game if paused
        if self.paused:
            return
        
        # Update transition if active
        if self.transitioning:
            self.update_transition(dt)
            return
        
        # Update all sprites
        self.all_sprites.update(dt)
        self.boss.update(dt)
        
        # Update bullets from all entities
        if hasattr(self.boss, 'bullets'):
            self.boss.bullets.update(dt)
            
        # Check for collisions
        self.check_collisions()
        
        # Update camera
        self.camera.update(self.player.rect)
        
        # Check game over conditions
        if hasattr(self.player, 'health') and self.player.health <= 0:
            self.persist['victory'] = False
            if not self.transitioning:
                self.start_transition()
            
        # Check victory condition
        if self.boss_defeated:
            self.persist['victory'] = True
            self.next_state = "GAME_OVER"
            if not self.transitioning:
                self.start_transition()

    def draw(self, surface):
        surface.fill((0, 0, 0))
        
        # Draw all sprites except boss and player
        for sprite in self.all_sprites:
            if sprite != self.boss and sprite != self.player:
                surface.blit(sprite.image, self.camera.apply(sprite.rect))
        
        # Draw player
        if hasattr(self, 'player'):
            # Check if player has its own draw method
            if hasattr(self.player, 'draw'):
                self.player.draw(surface, self.camera)
            else:
                surface.blit(self.player.image, self.camera.apply(self.player.rect))
        
        # Draw boss with special effects
        if hasattr(self, 'boss') and self.boss in self.all_sprites:
            # Check if boss has its own draw method
            if hasattr(self.boss, 'draw'):
                self.boss.draw(surface, self.camera)
            else:
                surface.blit(self.boss.image, self.camera.apply(self.boss.rect))
        
        # Draw boss health UI at the top of the screen
        if hasattr(self, 'boss') and hasattr(self.boss, 'health') and self.boss in self.all_sprites:
            self.draw_boss_health_ui(surface)
            
        if hasattr(self, 'player') and hasattr(self.boss, 'health') and self.boss in self.all_sprites:
            self.draw_health_ui(surface)
            
        # Draw pause menu if paused
        if self.paused:
            self.draw_pause_menu(surface)
        
        # Draw transition effect if active
        if self.transitioning:
            self.draw_transition(surface)

        # Draw custom cursor
        custom_cursor(surface)

    def draw_transition(self, surface):
        transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        transition_surface.fill((0, 0, 0, self.transition_alpha))
        surface.blit(transition_surface, (0, 0))

    def draw_health_ui(self, surface):
        # Draw health bar
        health_bar_width = 100
        health_ratio = self.player.health / self.player.max_health
        health_bar_fill = health_bar_width * health_ratio
        
        health_bar_pos = pygame.Rect(10, 10, health_bar_width, 15)
        
        # Health bar border
        pygame.draw.rect(surface, (0, 0, 0), health_bar_pos.inflate(4, 4))
        # Health bar background
        pygame.draw.rect(surface, (100, 0, 0), health_bar_pos)  # Dark red background
        # Health bar fill
        pygame.draw.rect(surface, (0, 255, 0), (health_bar_pos.x, health_bar_pos.y, health_bar_fill, health_bar_pos.height))  # Green health
        
    def draw_boss_health_ui(self, surface):
        # Boss name and health at top center
        boss_name = "ANCIENT EYE"
        text_surface = self.ui_font.render(boss_name, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 20))
        surface.blit(text_surface, text_rect)
        
        # Boss health bar below name
        health_bar_width = 200
        health_ratio = self.boss.health / self.boss.max_health
        health_bar_fill = health_bar_width * health_ratio
        
        health_bar_pos = pygame.Rect(WIDTH//2 - health_bar_width//2, 45, health_bar_width, 15)
        
        # Health bar border
        pygame.draw.rect(surface, (0, 0, 0), health_bar_pos.inflate(4, 4))
        # Health bar background
        pygame.draw.rect(surface, (100, 0, 0), health_bar_pos)  # Dark red background
        # Health bar fill
        pygame.draw.rect(surface, (255, 0, 0), (health_bar_pos.x, health_bar_pos.y, health_bar_fill, health_bar_pos.height))  # Bright red health
        
        # Phase indicator
        if hasattr(self.boss, 'phase') and self.boss.phase > 1:
            pygame.draw.circle(surface, (255, 0, 255), 
                            (health_bar_pos.right + 15, health_bar_pos.centery), 
                            5)  # Purple circle for phase 2
    
    def draw_pause_menu(self, surface):
        # Semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))  # Black with alpha
        surface.blit(overlay, (0, 0))
        
        # Create font for pause menu
        font_path = join('data', 'homespun.ttf')
        font = pygame.font.Font(font_path, 24)
        title_font = pygame.font.Font(font_path, 32)
        
        # Draw pause title
        title = title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4 - 10))
        surface.blit(title, title_rect)
        
        # Draw menu options
        for i, option in enumerate(self.pause_options):
            # Highlight selected option
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//3 + i * 30))
            surface.blit(text, text_rect)
    
    def handle_pause_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.choosing_sound.play()
                self.selected_option = (self.selected_option - 1) % len(self.pause_options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.choosing_sound.play()
                self.selected_option = (self.selected_option + 1) % len(self.pause_options)
            elif event.key == pygame.K_RETURN:
                self.choosing_sound.play()
                self.execute_pause_option()
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            prev_selected = self.selected_option
            for index, option in enumerate(self.pause_options):
                text_surface = self.ui_font.render(option, False, (255,255,255))
                text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//3 + index * 30))
                if text_rect.collidepoint(mouse_pos):
                    if self.selected_option != index:
                        self.selected_option = index
                        self.choosing_sound.play()
                    break
    
    def handle_pause_mouse_click(self, event):
        if event.button == 1:
            mouse_pos = event.pos
            for index, option in enumerate(self.pause_options):
                text_surface = self.ui_font.render(option, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 + index * 30))
                if text_rect.collidepoint(mouse_pos):
                    self.choosing_sound.play()
                    self.selected_option = index
                    self.execute_pause_option()
                    break
                
    
    def execute_pause_option(self):
        option = self.pause_options[self.selected_option]
        if option == "Resume":
            self.paused = False
        elif option == "Restart":
            self.persist["restart"] = True
            self.next_state = "GAMEPLAY"
            self.done = True
        elif option == "Menu":
            self.next_state = "MENU"
            pygame.mixer.music.pause()
            self.done = True
        elif option == "Quit":
            pygame.quit()
            sys.exit()