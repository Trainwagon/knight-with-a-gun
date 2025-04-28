import pygame

class Camera:
    def __init__(self, width, height, offset_limit=50, smoothing=0.1):
        self.width = width
        self.height = height
        self.offset_limit = offset_limit
        self.smoothing = smoothing

        self.offset = pygame.Vector2()
        self.target_offset = pygame.Vector2()
    
    def update(self, target_rect):
        # mouse pos
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_center = pygame.Vector2(self.width // 2, self.height // 2)
        mouse_direction = pygame.Vector2(mouse_x, mouse_y) - screen_center

        # offset limits
        if mouse_direction.length() > self.offset_limit:
            mouse_direction = mouse_direction.normalize() * self.offset_limit

        self.target_offset = mouse_direction

        self.offset += (self.target_offset - self.offset) * self.smoothing

    def apply(self, target_rect):
        return target_rect.move(-self.offset.x, -self.offset.y)