
import pygame
from types import SimpleNamespace
from math import atan2, cos, sin

import core as c
from functions import rgb, distance


class Bullet():
    dispawn = 10000
    def __init__(self, x, y, target, damage, speed, color, parent=None):
        self.parent = parent
        self.target = target
        self.target.targeted.append(self)
        self.rect = pygame.Rect(x, y, c.BULLET_SIZE, c.BULLET_SIZE)
        self.rect.center = (x, y)
        self.have_target = True
        self.timer = self.dispawn
        self.damage = damage
        self.color = color
        self.velocity = speed
        
    def get_angle(self): # rads = atan2(dy, dx)
        return atan2(self.target.rect.centery - self.rect.centery, self.target.rect.centerx - self.rect.centerx)
    
    def remove_target(self):
        rect = self.target.rect
        self.target = SimpleNamespace(rect=rect)
        self.have_target = False
        
    def update(self):
        ...
    
    def render(self, surf):
        pygame.draw.circle(surf, self.color, self.rect.center, self.rect.width/2)


class BaseBullet(Bullet):
    def update(self):
        rads = self.get_angle()
        self.rect.x += cos(rads) * self.velocity
        self.rect.y += sin(rads) * self.velocity
        
        if self.rect.colliderect(self.target.rect):
            if self.have_target:
                self.target.life -= self.damage
            else:
                c.crashed_bullets.append(self)
            c.bullets.remove(self)
        
        elif not self.have_target:
            for mob in c.mobs:
                if self.rect.colliderect(mob.rect):
                    mob.life -= self.damage
                    c.bullets.remove(self)
                    break


class ExplosiveBullet(Bullet):
    explosion_time = 300
    velocity = 3
    def __init__(self, x, y, target, damage, range_, color, color1, color2):
        super().__init__(x, y, target, damage, self.velocity, color)
        self.range = range_
        self.timer = self.explosion_time
        self.exploding = False
        self.color = color
        self.color1 = color1
        self.color2 = color2
    
    def update(self):
        if not self.exploding:
            rads = self.get_angle()
            self.rect.x += cos(rads) * self.velocity
            self.rect.y += sin(rads) * self.velocity
            if self.rect.colliderect(self.target.rect):
                self.explode()
        else:
            self.timer -= c.dt
            if self.timer <= 0:
                c.bullets.remove(self)
    
    def explode(self):
        self.exploding = True
        for mob in c.mobs:
            if distance(self, mob) <= self.range:
                mob.life -= self.damage
        
    def render(self, surf):
        if not self.exploding:
            if self.color is not None:
                pygame.draw.circle(surf, self.color, self.rect.center, self.rect.width/2)
        else:
            surface = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
            color = rgb(self.color1, 150)
            pygame.draw.circle(surface, color, (surface.get_width()/2, surface.get_height()/2), self.range)
            color = rgb(self.color2, 150)
            pygame.draw.circle(surface, color, (surface.get_width()/2, surface.get_height()/2), self.range/2)
            surf.blit(surface, (self.rect.centerx - self.range, self.rect.centery - self.range))


class SlowBullet(Bullet):
    effect_time = 3000
    reduced_velocity = 1
    def update(self):
        rads = self.get_angle()
        self.rect.x += cos(rads) * self.velocity
        self.rect.y += sin(rads) * self.velocity
        
        if self.rect.colliderect(self.target.rect):
            if self.have_target:
                self.impact(self.target)
            else:
                c.crashed_bullets.append(self)
            c.bullets.remove(self)
        
        elif not self.have_target:
            for mob in c.mobs:
                if self.rect.colliderect(mob.rect):
                    self.impact(mob)
                    c.bullets.remove(self)
                    break
    
    def impact(self, mob):
        mob.life -= self.damage
        mob.slow_effect(self.reduced_velocity, self.effect_time)


class RayBullet(Bullet):
    ray_size = 6
    def update(self):
        self.target.life -= self.damage
    
    def render(self, surf):
        pygame.draw.line(surf, self.color, self.rect.center, self.target.rect.center, self.ray_size)
