
from math import sqrt
import pygame

from core import MOB_SIZE, SOLDIER_SIZE
import core as c
from colors import colors
from functions import collision_list, distance
import level
from bullets import SlowBullet


def render_mob_header(surf, entity, header_size=50):
    size = entity.life * header_size / entity.max_life
    pygame.draw.rect(surf, colors['header']['bkg'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-10, header_size, 5))
    pygame.draw.rect(surf, colors['header']['life'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-10, size, 5))
    if entity.slow_timer != 0:
        size = entity.slow_timer * header_size / SlowBullet.effect_time
        pygame.draw.rect(surf, colors['header']['slow'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-5, size, 2))


class Mob():
    def __init__(self, path):
        self.rect = pygame.FRect(path[0][0] - MOB_SIZE//2, path[0][1] - MOB_SIZE//2, MOB_SIZE, MOB_SIZE)
        self.max_life = self.life
        self.path = path.copy()
        self.path_index = 0
        self.targeted = []
        self.tower_targeted = []
        self.normal_velocity = self.velocity
        self.slow_timer = 0
        self.collided = None
        self.timer = 0
    
    @property
    def life(self):
        return self._life
    
    @life.setter
    def life(self, value):
        self._life = value
        if self._life <= 0:
            level.gold += self.ret
            self.remove()
    
    def remove(self):
        for bullet in self.targeted:
            bullet.remove_target()
        for tower in self.tower_targeted:
            tower.remove_target()
        if self.collided is not None:
            self.collided.target = None
        c.mobs.remove(self)
    
    def update(self):
        # slow / freeze effect
        if self.slow_timer != 0:
            self.slow_timer -= c.dt
            if self.slow_timer <= 0:
                self.slow_timer = 0
                self.velocity = self.normal_velocity
        
        # solider collisions
        if self.collided is None:
            hit_list = collision_list(self, c.soldiers)
            for soldier in hit_list:
                if not soldier.moving and soldier.target is None:
                    self.collided = soldier
                    soldier.target = self
                    break
        
        # attack cooldown
        if self.timer > 0:
            self.timer += c.dt
            if self.timer > self.attack_rate:
                self.timer = 0
        
        # attack soldier
        if self.timer == 0 and self.collided is not None:
            self.collided.life -= self.damage
            self.timer = 1
        
        # follow the path
        speed = self.velocity * c.dt / 1000
        if self.collided is None:
            if self.path_index < len(self.path) - 1:
                target_x, target_y = self.path[self.path_index + 1]
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                distance = sqrt(dx ** 2 + dy ** 2)
                if distance < speed:
                    self.path_index += 1
                else:
                    self.rect.move_ip(dx / distance * speed, dy / distance * speed)
            else:
                # return False to despawn at the end of the path
                return False
        
        # return True to don't instant despawn
        return True
    
    def slow_effect(self, speed, time):
        self.velocity = speed
        self.slow_timer = time


class GoblinMob(Mob):
    _life = 60
    velocity = 20
    ret = 30
    damage = 10
    attack_rate = 2200


class OrcMob(Mob):
    _life = 80
    velocity = 20
    ret = 40
    damage = 15
    attack_rate = 2200


class Soldier():
    def __init__(self, x, y, tower, life, damage, attack_rate, velocity, regeneration, color):
        self.rect = pygame.Rect(x, y, SOLDIER_SIZE, SOLDIER_SIZE)
        self.velocity = velocity
        self._life = life
        self.max_life = life
        self.damage = damage
        self.attack_rate = attack_rate
        self.color = color
        self.tower = tower
        self.slow_timer = 0
        self.motion = [0, 0]
        self.target = None
        self.moving = False
        self.timer = 0
        self.regeneration = regeneration
    
    @property
    def life(self):
        return self._life
    
    @life.setter
    def life(self, value):
        self._life = value
        if self._life <= 0:
            self.remove()
        
    def update(self):
        if self.motion != [0, 0]:
            if self.target is not None:
                self.target.collided = None
                self.target = None
            
            self.moving = True
            self.rect.x += self.motion[0]
            self.rect.y += self.motion[1]
            if distance(self.tower, self) >= self.tower.soldier_range:
                self.rect.x -= self.motion[0]
                self.rect.y -= self.motion[1]
        else:
            self.moving = False
        self.motion = [0, 0]
        
        if self.life < self.max_life and not self.moving and self.target is None:
            self.life += self.regeneration
        
        if self.target is not None:
            if self.timer == 0:
                self.timer = 1
                self.attack()
        
        if self.timer > 0:
            self.timer += c.dt
            if self.timer > self.attack_rate:
                self.timer = 0
        
    def attack(self):
        self.target.life -= self.damage
    
    def remove(self):
        if self.target is not None:
            self.target.collided = None
        self.tower.dead_soldier(self)
        c.soldiers.remove(self)
    
    def move(self):
        if c.keys[pygame.K_z]:
            self.motion[1] -= self.velocity
        if c.keys[pygame.K_s]:
            self.motion[1] += self.velocity
        if c.keys[pygame.K_q]:
            self.motion[0] -= self.velocity
        if c.keys[pygame.K_d]:
            self.motion[0] += self.velocity
