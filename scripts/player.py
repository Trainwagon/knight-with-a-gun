import pygame
from math import atan2, degrees
from scripts.AssetLoader import AssetLoader
from scripts.dodge_roll import DodgeRoll
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, water_sprites, camera):
        super().__init__(groups)
        
        # load animation frames for player
        asset_loader = AssetLoader()
        self.idle_side_frames = asset_loader.load_animation("data", "images", "entities", "player", "idle_side")
        self.run_side_frames = asset_loader.load_animation("data", "images", "entities", "player", "run_side")
        self.idle_up_frames = asset_loader.load_animation("data", "images", "entities", "player", "idle_side")  # placeholder for now
        self.run_up_frames = asset_loader.load_animation("data", "images", "entities", "player", "run_up")
        
        self.camera = camera

        self.shoot_sound = pygame.mixer.Sound(join('data', 'sound', 'sfx', 'shoot.wav'))
        self.shoot_sound.set_volume(0.4)
        self.hurt_sound = pygame.mixer.Sound(join('data', 'sound', 'sfx', 'hurt.wav'))
        self.hurt_sound.set_volume(1)

        # load rifle image
        self.rifle_image = asset_loader.load_image("data", "images", "guns", "rifle.png")
        self.rifle = self.rifle_image.copy()

        # make flipped versions of side animations
        self.flipped_run_side_frames = [pygame.transform.flip(f, True, False) for f in self.run_side_frames]
        self.flipped_idle_side_frames = [pygame.transform.flip(f, True, False) for f in self.idle_side_frames]

        # set starting image and rect
        self.image = self.idle_side_frames[0]
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-8, -6)
        self.previous_frames = self.idle_side_frames
        self.rifle_offset = pygame.Vector2(30, 0)
        self.shoot_direction = pygame.Vector2(1, 0)

        # track where rifle tip is in world space
        self.rifle_tip_world_position = self.rect.center

        # animation stuff
        self.current_frame = 0
        self.animation_speed = 0.2
        self.time_accumulator = 0
        self.facing_left = False

        # movement settings
        self.direction = pygame.Vector2()
        self.speed = 100
        self.normal_speed = 100
        self.collision_sprites = collision_sprites
        self.water_sprites = water_sprites
        self.water_speed = 50

        # gun shoot cooldown
        self.can_shoot = True  # Changed from False to True to allow shooting after init
        self.shoot_time = 0
        self.gun_cooldown = 150  # ms

        # delay to avoid instant shooting after spawn
        self.entry_delay = 500
        self.entry_timer = pygame.time.get_ticks()

        # setup dodge roll
        self.dodge_roll = DodgeRoll(self)
        
        # Player health and damage effects
        self.max_health = 100
        self.health = self.max_health
        self.invincible = False
        self.invincibility_duration = 1000  # ms
        self.invincibility_timer = 0
        self.flash_duration = 0.1
        self.flash_timer = 0
        self.flashing = False
        
        # Create a group for player bullets
        self.bullets = pygame.sprite.Group()

    def take_damage(self, damage):
        # Don't take damage during dodge roll
        if self.dodge_roll.is_rolling or self.invincible:
            return False
            
        self.health -= damage
        
        # Play sound
        self.hurt_sound.play()

        # Screenshake
        self.camera.start_screen_shake(duration=10, intensity=5)
        self.invincible = True
        self.invincibility_timer = pygame.time.get_ticks()
        
        # Visual feedback
        self.flashing = True
        self.flash_timer = 0
        
        return self.health <= 0  # Return True if player is dead

    def input(self):
        keys = pygame.key.get_pressed()

        # if rolling, skip movement
        if self.dodge_roll.is_rolling:
            self.dodge_roll.handle_input(keys)
            return

        # get direction from wasd
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        # flip sprite based on input
        if self.direction.x < 0:
            self.facing_left = True
        elif self.direction.x > 0:
            self.facing_left = False

        # check for dodge roll
        self.dodge_roll.handle_input(keys)

    def move(self, dt):
        # slow down if in water
        in_water = any(sprite.rect.colliderect(self.hitbox_rect) for sprite in self.water_sprites)
        self.speed = self.water_speed if in_water else self.normal_speed

        # apply movement and check for collisions
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def update_rifle(self, camera):
        # get mouse pos in screen space
        mouse_pos = pygame.mouse.get_pos()

        # get player center in screen space
        player_screen_pos = camera.apply(self.rect).center

        # find direction to mouse
        direction = pygame.Vector2(mouse_pos) - pygame.Vector2(player_screen_pos)

        if direction.length_squared() > 0:
            self.shoot_direction = direction.normalize()

            # get tip of rifle in world space
            rifle_tip_screen = player_screen_pos + self.shoot_direction * 15
            self.rifle_tip_world_position = (
                self.rect.centerx + (rifle_tip_screen[0] - player_screen_pos[0]),
                self.rect.centery + (rifle_tip_screen[1] - player_screen_pos[1])
            )

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def get_event(self):
        current_time = pygame.time.get_ticks()

        # wait before player can shoot
        if current_time - self.entry_timer < self.entry_delay:
            return

        # left mouse click to shoot
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            bullet = Bullet(self.rifle_tip_world_position, self.shoot_direction, [self.groups()[0], self.bullets])
            self.camera.start_screen_shake(duration=5, intensity=2)
            self.shoot_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def draw_rifle(self, surface, camera):
        # rotate rifle image to match mouse direction
        angle = degrees(atan2(self.shoot_direction.x, self.shoot_direction.y)) - 90
        rotated_rifle = pygame.transform.rotate(self.rifle, angle)

        # get screen pos of rifle tip
        rifle_screen_pos = camera.apply(pygame.Rect(self.rifle_tip_world_position, (0, 0))).topleft

        # draw the rifle
        rifle_rect = rotated_rifle.get_rect(center=rifle_screen_pos)
        surface.blit(rotated_rifle, rifle_rect)

    def update(self, dt):
        self.gun_timer()
        self.input()
        self.dodge_roll.update(dt)

        if not self.dodge_roll.is_rolling:
            self.move(dt)

        self.update_rifle(self.camera)
        self.get_event()

        # Choose animation frame
        is_moving = self.direction.length_squared() != 0
        if is_moving:
            current_frames = self.flipped_run_side_frames if self.facing_left else self.run_side_frames
        else:
            current_frames = self.flipped_idle_side_frames if self.facing_left else self.idle_side_frames

        # Reset frame index when switching animation
        if not self.dodge_roll.is_rolling:
            if current_frames is not self.previous_frames:
                self.current_frame = 0
                self.previous_frames = current_frames

        # Set current frame
        self.image = current_frames[self.current_frame]

        # Update frame timing
        self.time_accumulator += dt
        if self.time_accumulator >= self.animation_speed:
            self.time_accumulator = 0
            self.current_frame = (self.current_frame + 1) % len(current_frames)
            
        # Update bullets
        self.bullets.update(dt)
        
        # Update invincibility
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincibility_timer >= self.invincibility_duration:
                self.invincible = False
                self.flashing = False
                
        # Update flash timer
        if self.flashing:
            self.flash_timer += dt
            if self.flash_timer >= self.flash_duration:
                self.flash_timer = 0  # Reset timer but keep flashing while invincible

    def draw(self, surface, camera):
        # Draw roll trail if rolling
        self.dodge_roll.draw_roll_effect(surface, camera)
        draw_rect = self.rect.copy()

        # Add bounce effect while rolling
        if self.dodge_roll.roll_height_modifier != 0:
            draw_rect.y += self.dodge_roll.roll_height_modifier

        # Draw player sprite with flash effect if hit
        if self.flashing and int(self.flash_timer * 15) % 2 == 0:
            # Create a white version of the current frame for the flash effect
            white_image = self.image.copy()
            white_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(white_image, camera.apply(self.rect))
        else:
            surface.blit(self.image, camera.apply(self.rect))
            
        # Draw rifle
        self.draw_rifle(surface, camera)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups):
        super().__init__(groups)
        self.image = pygame.Surface((6, 6))
        self.image.fill("yellow")
        self.rect = self.image.get_frect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.speed = 400
        self.velocity = direction * self.speed
        self.damage = 15  # Damage value for player bullets

    def update(self, dt):
        # move the bullet
        movement = self.velocity * dt
        self.rect.centerx += movement.x
        self.rect.centery += movement.y
        # remove bullet after sometimes
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()