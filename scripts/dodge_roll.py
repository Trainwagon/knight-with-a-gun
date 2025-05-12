import pygame
from math import sin
from os.path import join

class DodgeRoll:
    def __init__(self, player):
        self.player = player
        
        # basic roll setup
        self.is_rolling = False
        self.roll_direction = pygame.Vector2()
        self.roll_speed = 250  # faster than normal movement
        self.roll_duration = 0.5  # how long the roll lasts (in seconds)
        self.roll_time = 0
        self.roll_cooldown = 0.2  # delay before player can roll again
        self.roll_cooldown_timer = 0
        self.can_roll = True  # is the roll available?
        
        # invincibility while rolling
        self.invincible = False
        self.invincibility_duration = 0.5  # matches the roll duration
        
        # for slight vertical bounce effect
        self.roll_height_modifier = 0
        
        # initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # load dodge sound once
        self.dodge_sound = pygame.mixer.Sound("data/sound/sfx/dodge.wav")
        self.dodge_sound.set_volume(0.1) 

    def start_roll(self, direction):
        # can't start roll if already rolling or on cooldown
        if not self.can_roll or self.is_rolling:
            return False
            
        # normalize direction input
        if direction.length_squared() > 0:
            self.roll_direction = direction.normalize()
        else:
            # no input, roll based on player facing
            self.roll_direction = pygame.Vector2(1, 0)
            if self.player.facing_left:
                self.roll_direction.x = -1
                
        # start rolling
        self.is_rolling = True
        self.invincible = True
        self.roll_time = 0
        self.can_roll = False
        self.roll_cooldown_timer = 0
        
        self.player.direction = self.roll_direction.copy()

        # play sound
        self.dodge_sound.play()
        
        return True
        
    def update(self, dt):
        # handle cooldown after roll
        if not self.can_roll and not self.is_rolling:
            self.roll_cooldown_timer += dt
            if self.roll_cooldown_timer >= self.roll_cooldown:
                self.can_roll = True
        
        # if not rolling, nothing else to do
        if not self.is_rolling:
            return
            
        # update roll timer
        self.roll_time += dt
        
        # get roll progress (0 to 1)
        progress = min(self.roll_time / self.roll_duration, 1.0)
        
        # smooth roll using sin curve to ease in/out roll
        speed_factor = sin(progress * 3.14)
        current_roll_speed = self.roll_speed * speed_factor
        
        # move player based on direction and speed
        movement = self.roll_direction * current_roll_speed * dt
        

        original_direction = self.player.direction.copy()
        self.player.direction = self.roll_direction.copy()

        # Apply movement with collision checks
        self.player.hitbox_rect.x += movement.x
        self.player.collision('horizontal')
        self.player.hitbox_rect.y += movement.y
        self.player.collision('vertical')
        
        self.player.direction = original_direction

        # Update the player's visible rect to match the hitbox
        self.player.rect.center = self.player.hitbox_rect.center
        
        # bounce effect (optional visual polish)
        self.roll_height_modifier = -4 * sin(progress * 3.14)
        
        # end the roll if time is up
        if progress >= 1.0:
            self.end_roll()
            
    def end_roll(self):
        # stop rolling and reset variables
        self.is_rolling = False
        self.roll_height_modifier = 0
        
        # cooldown starts now
        self.roll_cooldown_timer = 0
        
    def draw_roll_effect(self, surface, camera):
        # only draw effect if rolling
        if not self.is_rolling:
            return
            
        # fade trail based on time
        alpha = int(255 * (1 - self.roll_time / self.roll_duration))
        if alpha <= 0:
            return
            
        # create transparent trail surface
        trail_surf = pygame.Surface((self.player.rect.width, self.player.rect.height), pygame.SRCALPHA)
        trail_surf.fill((255, 255, 255, alpha))  # white with fading alpha
        
        # get player position on screen
        screen_pos = camera.apply(self.player.rect)
        
        # offset trail behind player
        offset = self.roll_direction * -10
        trail_pos = (screen_pos.x + offset.x, screen_pos.y + offset.y)
        
        # draw the trail
        surface.blit(trail_surf, trail_pos)
        
    def handle_input(self, keys):
        # ignore input if already rolling
        if self.is_rolling:
            return
            
        # check if roll key is pressed and rolling is allowed
        if keys[pygame.K_LSHIFT] and self.can_roll:
            # get direction from movement keys
            direction = pygame.Vector2(
                int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            )
            
            if direction.length_squared() > 0:
                self.start_roll(direction)
            else:
                # no movement input, roll based on facing
                direction = pygame.Vector2(-1 if self.player.facing_left else 1, 0)
                self.start_roll(direction)

