from pathlib import Path
import pygame

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