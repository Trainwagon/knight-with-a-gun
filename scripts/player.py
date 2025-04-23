from scripts.AssetLoader import AssetLoader
import pygame

asset_loader = AssetLoader()

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # load frames
        self.idle_side_frames = asset_loader.load_animation("data", "images", "entities", "player", "idle_side")
        self.run_side_frames = asset_loader.load_animation("data", "images", "entities", "player", "run_side")
        self.idle_up_frames = asset_loader.load_animation("data", "images", "entities", "player", "idle_side")
        self.run_up_frames = asset_loader.load_animation("data", "images", "entities", "player", "run_up")
        

        # flipped ver
        self.flipped_run_side_frames = [pygame.transform.flip(frame, True, False) for frame in self.run_side_frames]
        self.flipped_idle_side_frames = [pygame.transform.flip(frame, True, False) for frame in self.idle_side_frames]

        # set initial image 
        self.image = self.idle_side_frames[0]
        self.rect = self.image.get_frect(center= pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
        self.previous_frames = self.idle_side_frames

        # animation state
        self.current_frame = 0
        self.animation_speed = 0.2
        self.time_accumulator = 0
        self.facing_left = False

        # movement
        self.direction = pygame.Vector2()
        self.speed = 100
        # self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        # flip img tergantung input
        if self.direction.x < 0:
            self.facing_left = True
        elif self.direction.x > 0:
            self.facing_left = False
        # self.direction = self.direction.normalize()if self.direction else self.direction


    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        # self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        # self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def update(self, dt):
        self.input()
        self.move(dt)

         # Choose animation frames
        is_moving = self.direction.length_squared() != 0
        if is_moving:
            current_frames = self.flipped_run_side_frames if self.facing_left else self.run_side_frames
        else:
            current_frames = self.flipped_idle_side_frames if self.facing_left else self.idle_side_frames

        # reset index
        if current_frames is not self.previous_frames:
            self.current_frame = 0
            self.previous_frames = current_frames

        # Immediately update the image to match direction
        self.image = current_frames[self.current_frame]

        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.time_accumulator = 0
            self.current_frame = (self.current_frame + 1) % len(current_frames)


            