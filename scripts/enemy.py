import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))  # merah
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.speed = 50
        self.shoot_timer = 0

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

        # bounce kalau nyentuh pinggiran screen
        if self.rect.left <= 0 or self.rect.right >= 400:
            self.direction.x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= 224:
            self.direction.y *= -1

    def shoot(self, bullet_group):
        bullet = Bullet(self.rect.center, random.uniform(-1,1), random.uniform(-1,1))
        bullet_group.add(bullet)

    def update(self, dt, bullet_group):
        self.move(dt)
        self.shoot_timer += dt
        if self.shoot_timer >= 2:  # setiap 2 detik nembak
            self.shoot(bullet_group)
            self.shoot_timer = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, dir_x, dir_y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 0))  # kuning
        self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.Vector2(dir_x, dir_y).normalize() * 150

    def update(self, dt):
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        # kalau keluar layar, hapus
        if (self.rect.right < 0 or self.rect.left > 400 or
            self.rect.bottom < 0 or self.rect.top > 224):
            self.kill()
