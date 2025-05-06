import pygame
from scripts.collision import Sprite, CollisionSprite
from scripts.AssetLoader import AssetLoader
from scripts.settings import *
import math
import random

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, player):
        super().__init__(groups)
        
        # Core attributes
        self.pos = pygame.math.Vector2(pos)
        self.collision_sprites = collision_sprites
        self.player = player
        
        # Animation setup
        self.asset_loader = AssetLoader()
        self.animations = {
            'idle': self.asset_loader.load_animation('data', 'images', 'entities', 'enemy', 'boss_eye_idle'),
            'defensive': self.asset_loader.load_animation('data', 'images', 'entities', 'enemy', 'boss_eye_defensive'),
            'chargeup': self.asset_loader.load_animation('data', 'images', 'entities', 'enemy', 'boss_eye_chargeup'),
            'attack_eye': self.asset_loader.load_animation('data', 'images', 'entities', 'enemy', 'boss_eye_attack_w_eye'),
            'attack_hands': self.asset_loader.load_animation('data', 'images', 'entities', 'enemy', 'boss_eye_attack_w_hands'),
        }
        
        # Animation state
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15
        
        # Initialize image and rect
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.hitbox = self.rect.inflate(-20, -20)  # Smaller hitbox for more forgiving collisions
        
        # Boss stats
        self.max_health = 1000
        self.health = self.max_health
        self.speed = 100  # Increased from 1.5 to 60 units per second
        self.attack_cooldown = 1000  # milliseconds - reduced cooldown
        self.last_attack_time = 0
        self.last_movement_time = 0
        self.movement_cooldown = 1500  # Time between movement decisions in ms
        
        # Chase behavior
        self.chase_player = False
        self.chase_chance = 0.6  # 60% chance to chase player when choosing movement
        self.attack_during_chase = True  # Can attack while chasing
        
        # Attack patterns
        self.bullets = pygame.sprite.Group()
        self.attack_patterns = ['eye_barrage', 'hand_sweep', 'bullet_hell']
        self.current_pattern = None
        self.pattern_timer = 0
        
        # Boss states
        self.states = {
            'idle': self.idle_state,
            'defensive': self.defensive_state,
            'charging': self.charging_state,
            'attacking': self.attacking_state,
            'chasing': self.chasing_state,  # New chasing state
        }
        self.current_state = 'idle'
        self.state_timer = 0
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.moving = False
        self.target_pos = None
        self.phase = 1  # Boss can have multiple phases based on health
        
        # Flash effect when taking damage
        self.flash_duration = 0.1
        self.flash_timer = 0
        self.flashing = False
        
        # Attack success tracking
        self.consecutive_attacks = 0
        self.max_consecutive_attacks = 3  # Max attacks before forced movement
        
        # Force initial movement immediately
        self.decide_new_movement()
        
    def decide_new_movement(self):
        """Choose a new target position for the boss to move to"""
        screen_width, screen_height = WIDTH, HEIGHT
        margin = 100  # Stay away from edges
        
        # Decide whether to chase player
        if random.random() < self.chase_chance:
            self.chase_player = True
            self.current_state = 'chasing'
            return
        else:
            self.chase_player = False
        
        # Choose a random point within screen bounds but use the full arena
        target_x = random.randint(margin, screen_width - margin)
        target_y = random.randint(margin, screen_height - margin)
        self.target_pos = pygame.math.Vector2(target_x, target_y)
        
        # Calculate direction to target
        direction_vector = self.target_pos - self.pos
        if direction_vector.length() > 0:
            self.direction = direction_vector.normalize()
            self.moving = True
            
        # Set the last movement time
        self.last_movement_time = pygame.time.get_ticks()
        
    def take_damage(self, damage):
        self.health -= damage
        
        # Activate flash effect
        self.flashing = True
        self.flash_timer = 0
        
        # Enter defensive state occasionally when hit, but with lower probability
        if random.random() < 0.1 and self.current_state not in ['defensive', 'charging']:  # Reduced from 0.3 to 0.1
            self.current_state = 'defensive'
            self.state = 'defensive'
            self.frame_index = 0
            self.state_timer = 0
        
        # Phase transition at 50% health
        if self.health <= self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.speed *= 1.5
            self.attack_cooldown *= 0.7
            self.chase_chance += 0.2  # More aggressive in phase 2
            
            # Special effect for phase transition
            self.current_state = 'defensive'
            self.state = 'defensive'
            self.frame_index = 0
            self.state_timer = 0
            
            # Spawn a ring of bullets to signal phase change
            for angle in range(0, 360, 15):
                self.shoot_bullet(angle)
        
        if self.health <= 0:
            # Death effect - spawn bullets in all directions
            for angle in range(0, 360, 10):
                self.shoot_bullet(angle)
            self.kill()
            return True  # Boss is defeated
        return False
    
    def idle_state(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to move again
        if not self.moving or current_time - self.last_movement_time > self.movement_cooldown:
            self.decide_new_movement()
        
        # Move if we're in moving state
        if self.moving:
            # Calculate distance to target
            distance_to_target = (self.target_pos - self.pos).length()
            
            # If we've reached the target (or close enough), stop moving
            if distance_to_target < 5:
                self.moving = False
            else:
                # Move towards target
                movement = self.direction * self.speed * dt
                self.pos += movement
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                self.hitbox.center = self.rect.center
        
        # Check if it's time to attack
        if current_time - self.last_attack_time > self.attack_cooldown:
            # After multiple consecutive attacks, force movement
            if self.consecutive_attacks >= self.max_consecutive_attacks:
                self.consecutive_attacks = 0
                self.decide_new_movement()
            else:
                self.current_state = 'charging'
                self.state = 'chargeup'
                self.frame_index = 0
                self.state_timer = 0
    
    def chasing_state(self, dt):
        """New state that makes the boss chase the player"""
        # Update target position to chase player
        self.target_pos = pygame.math.Vector2(self.player.rect.center)
        
        # Calculate direction to player
        direction_vector = self.target_pos - self.pos
        if direction_vector.length() > 0:
            self.direction = direction_vector.normalize()
        
        # Move towards player at a slightly reduced speed for balance
        move_speed = self.speed * 0.8
        movement = self.direction * move_speed * dt
        self.pos += movement
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center
        
        # Check if we should attack while chasing
        current_time = pygame.time.get_ticks()
        if self.attack_during_chase and current_time - self.last_attack_time > self.attack_cooldown:
            self.current_state = 'charging'
            self.state = 'chargeup'
            self.frame_index = 0
            self.state_timer = 0
            
        # Randomly decide to stop chasing
        if random.random() < 0.01:  # 1% chance per frame to stop chasing
            self.chase_player = False
            self.current_state = 'idle'
    
    def defensive_state(self, dt):
        # When taking damage, boss might go into defensive mode
        self.state_timer += dt
        
        if self.state_timer >= 0.7:  # Reduced from 1.5 to 0.7 seconds
            self.current_state = 'idle'
            self.state = 'idle'
            self.state_timer = 0
    
    def charging_state(self, dt):
        # Charge up before attacking
        self.state_timer += dt
        
        if self.state_timer >= 0.5:  # Reduced from 2.0 to 0.5 seconds
            self.current_state = 'attacking'
            
            # Choose an attack pattern
            self.current_pattern = random.choice(self.attack_patterns)
            
            # Set appropriate animation based on attack pattern
            if self.current_pattern == 'eye_barrage':
                self.state = 'attack_eye'
            elif self.current_pattern in ['hand_sweep', 'bullet_hell']:
                self.state = 'attack_hands'
                
            self.frame_index = 0
            self.state_timer = 0
            self.last_attack_time = pygame.time.get_ticks()
            self.consecutive_attacks += 1  # Track consecutive attacks
    
    def attacking_state(self, dt):
        self.state_timer += dt
        
        # Execute different attack patterns
        if self.current_pattern == 'eye_barrage':
            self.eye_barrage_attack(dt)
        elif self.current_pattern == 'hand_sweep':
            self.hand_sweep_attack(dt)
        elif self.current_pattern == 'bullet_hell':
            self.bullet_hell_attack(dt)
        
        # After attack duration, go back to idle
        attack_duration = 1.5  # Reduced from 3.0 to 1.5 seconds
        if self.state_timer >= attack_duration:
            # After attack, decide whether to keep attacking or move
            if random.random() < 0.7:  # 70% chance to continue attacking
                self.current_state = 'idle'  # Will quickly transition to charging again
            else:
                # Force movement after attack sequence
                self.consecutive_attacks = 0
                self.current_state = 'idle'
                self.decide_new_movement()
            
            self.state = 'idle'
            self.state_timer = 0
    
    def eye_barrage_attack(self, dt):
        # Always shoot directly at player position for more accurate tracking
        if random.random() < 0.25:  # Increased from 0.2 to 0.25
            self.shoot_at_player()
    
    def hand_sweep_attack(self, dt):
        # Sweep bullets in an arc, always centered on player
        if random.random() < 0.15:  # Increased from 0.1 to 0.15
            angle_spread = 60  # degrees
            
            # Continuously update center angle to track player movement
            center_angle = math.degrees(math.atan2(
                self.player.rect.centery - self.rect.centery,
                self.player.rect.centerx - self.rect.centerx
            ))
            
            for i in range(-2, 3):
                angle = center_angle + (i * angle_spread / 4)
                self.shoot_bullet(angle)
    
    def bullet_hell_attack(self, dt):
        # Spray bullets in all directions
        if random.random() < 0.12:  # Increased from 0.1 to 0.12
            for angle in range(0, 360, 30):
                offset_angle = angle + random.uniform(-5, 5)  # Add slight randomness
                self.shoot_bullet(offset_angle)
    
    def shoot_at_player(self):
        # Calculate angle to player's current position
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        angle = math.degrees(math.atan2(dy, dx))
        
        # Add slight randomness for difficulty control
        angle += random.uniform(-3, 3)  # Reduced spread from -5,5 to -3,3 for more accuracy
        self.shoot_bullet(angle)
        
        # In phase 2, shoot an additional bullet with prediction
        if self.phase >= 2 and random.random() < 0.4:
            # Try to predict where player will be
            player_velocity = getattr(self.player, 'direction', pygame.math.Vector2(0, 0))
            if player_velocity.length() > 0:
                prediction_factor = 30  # How far ahead to predict
                predicted_pos = pygame.math.Vector2(
                    self.player.rect.centerx + player_velocity.x * prediction_factor,
                    self.player.rect.centery + player_velocity.y * prediction_factor
                )
                
                # Calculate angle to predicted position
                pred_dx = predicted_pos.x - self.rect.centerx
                pred_dy = predicted_pos.y - self.rect.centery
                pred_angle = math.degrees(math.atan2(pred_dy, pred_dx))
                
                self.shoot_bullet(pred_angle)
    
    def shoot_bullet(self, angle):
        Bullet(
            self.rect.center, 
            angle, 
            self.bullets, 
            self.collision_sprites,
            self.phase
        )
    
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt * 60
        
        # Loop the animation
        if self.frame_index >= len(self.animations[self.state]):
            if self.state in ['attack_eye', 'attack_hands', 'chargeup']:
                self.frame_index = len(self.animations[self.state]) - 1
            else:
                self.frame_index = 0
        
        self.image = self.animations[self.state][int(self.frame_index)]
        
        # Update flash timer
        if self.flashing:
            self.flash_timer += dt
            if self.flash_timer >= self.flash_duration:
                self.flashing = False
                self.flash_timer = 0
    
    def update(self, dt):
        # Execute current state behavior
        self.states[self.current_state](dt)
        
        # Update animation
        self.animate(dt)
        
        # Update bullets
        self.bullets.update(dt)
    
    def draw(self, surface, camera):
        # Draw boss with flash effect if getting hit
        if self.flashing and int(self.flash_timer * 15) % 2 == 0:
            # Create a white version of the current frame for the flash effect
            white_image = self.image.copy()
            white_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(white_image, camera.apply(self.rect))
        else:
            surface.blit(self.image, camera.apply(self.rect))
            
        # Draw bullets with trail effects
        for bullet in self.bullets:
            bullet.draw(surface, camera)        


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, collision_sprites, phase=1):
        super().__init__(groups)
        
        # Store collision sprites
        self.collision_sprites = collision_sprites
        
        # Create bullet image with trail effect - size adjusted for better matching
        bullet_size = 8  # Reduced from 12 to 8 for better size ratio with player
        self.image = pygame.Surface((bullet_size, bullet_size), pygame.SRCALPHA)
        
        # Different bullet colors based on phase
        if phase == 1:
            self.color = (255, 0, 0)  # Red bullets for phase 1
            self.trail_color = (255, 100, 0)  # Orange trail
        else:
            self.color = (255, 0, 255)  # Purple bullets for phase 2
            self.trail_color = (200, 0, 255)  # Light purple trail
            
        # Draw the bullet with a glow effect
        center_point = bullet_size // 2
        glow_radius = bullet_size // 2  # Full radius for glow
        core_radius = bullet_size // 3  # Core is 2/3 the size of the glow
        
        pygame.draw.circle(self.image, self.trail_color, (center_point, center_point), glow_radius)  # Outer glow
        pygame.draw.circle(self.image, self.color, (center_point, center_point), core_radius)  # Core
        
        # Position and movement
        self.rect = self.image.get_frect(center=pos)
        # Create a smaller hitbox to match visible bullet core
        self.hitbox = self.rect.inflate(-2, -2)
        self.pos = pygame.math.Vector2(pos)
        self.spawn_time = pygame.time.get_ticks()
        
        # Convert angle to radians for direction calculation
        angle_rad = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        
        # Bullet attributes
        self.speed = 55 * (1 + 0.5 * (phase - 1))  # Increased from 100 to 150
        self.damage = 10 * phase  # More damage in later phases
        self.lifetime = 0
        self.max_lifetime = 10  # Seconds
        
        # Trail effect
        self.trail_positions = []
        self.max_trail_length = 5
    
    def update(self, dt):
        # Store previous position for trail
        if len(self.trail_positions) >= self.max_trail_length:
            self.trail_positions.pop(0)
        self.trail_positions.append(self.pos.copy())
        
        # Move bullet
        movement = self.direction * self.speed * dt
        self.pos += movement
        self.rect.center = self.pos
        self.hitbox.center = self.pos  # Update hitbox position as well
        
        # Check for collisions with walls using hitbox instead of rect
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                self.kill()
                break
        
        # Update lifetime and kill if exceeded
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            self.kill()
    
    def draw(self, surface, camera):
        # Draw trail
        for i, pos in enumerate(self.trail_positions):
            # Calculate alpha for fading trail
            alpha = int(255 * (i / len(self.trail_positions)) * 0.5)
            # Calculate size for shrinking trail
            size = int(4 * (i / len(self.trail_positions)))
            
            # Create trail surface
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            trail_color_with_alpha = (*self.trail_color, alpha)
            pygame.draw.circle(trail_surf, trail_color_with_alpha, (size, size), size)
            
            # Draw trail
            trail_rect = trail_surf.get_frect(center=pos)
            surface.blit(trail_surf, camera.apply(trail_rect))