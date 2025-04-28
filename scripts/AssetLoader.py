from pathlib import Path
import pygame
from os.path import join

class AssetLoader:
    def __init__(self):
        # find the root folder based from this dir
        self.base_path = Path(__file__).parent.parent
        self.cache = {}

    def load_image(self, *path_parts):
        """
        Load 1 image. Path parts bisa banyak (folder-folder).
        """
        full_path = self.base_path.joinpath(*path_parts)
        if full_path not in self.cache:
            self.cache[full_path] = pygame.image.load(str(full_path)).convert_alpha()
        return self.cache[full_path]
    
    def load_animation(self, *path_parts):
        """
        Load images from 1 folder (for animation).
        """
        frames = []
        folder_path = self.base_path.joinpath(*path_parts)
        for img_file in sorted(folder_path.glob("*.png")):
            frames.append(self.load_image(*folder_path.parts[len(self.base_path.parts):], img_file.name))
        return frames
    

cursor_img = None  # cache global biar load sekali saja

def custom_cursor(screen):
    global cursor_img
    pygame.mouse.set_visible(False)

    if cursor_img is None:
        cursor_img = pygame.image.load(join('data', 'images', 'crosshair.png')).convert_alpha()
        cursor_img.set_alpha(150)

    cursor_rect = cursor_img.get_frect(center=pygame.mouse.get_pos())
    screen.blit(cursor_img, cursor_rect)