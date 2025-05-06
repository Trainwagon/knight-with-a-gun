import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height, offset_limit=80, smoothing=0.15):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.offset_limit = offset_limit
        self.smoothing = smoothing

        self.offset = pygame.Vector2()
        self.target = pygame.Vector2()
        self.initialized = False  # Flag to track if we've initialized with player position
    
    def update(self, target_rect):
        # Get target center
        target_center = pygame.Vector2(target_rect.center)

        # Initialize camera position on first update
        if not self.initialized:
            # Directly set camera to player position
            self.offset = target_center - pygame.Vector2(self.width // 2, self.height // 2)
            # Clamp to map boundaries
            self.offset.x = max(0, min(self.offset.x, self.map_width - self.width))
            self.offset.y = max(0, min(self.offset.y, self.map_height - self.height))
            self.initialized = True
            return

        # Mouse position logic
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_center = pygame.Vector2(self.width // 2, self.height // 2)
        mouse_offset = pygame.Vector2(mouse_x, mouse_y) - screen_center

        if mouse_offset.length() > self.offset_limit:
            mouse_offset = mouse_offset.normalize() * self.offset_limit

        # Calculate total target offset
        desired_offset = target_center + mouse_offset - screen_center

        # Smooth follow
        self.offset += (desired_offset - self.offset) * self.smoothing

        # Clamp to map boundaries
        self.offset.x = max(0, min(self.offset.x, self.map_width - self.width))
        self.offset.y = max(0, min(self.offset.y, self.map_height - self.height))

    def apply(self, target_rect):
        return target_rect.move(-self.offset.x, -self.offset.y)