
import pygame
from types import SimpleNamespace
from math import sqrt

from core import TILE_SIZE, SOLDIER_SIZE
import core as c
from colors import colors
from functions import distance, concatenate, is_hovered, rgb
from bullets import BaseBullet, ExplosiveBullet, RayBullet, SlowBullet
from spells import Blizzard, Lightning, GolemSpell, Rage
from entities import Soldier
import level


def build_tower(slot, tower):
    if level.gold >= tower.price:
        level.gold -= tower.price
        c.slots.remove(slot)
        c.towers.append(tower(slot.x, slot.y))
        return True
    else:
        return False
    
    
def render_tower_kills(surf, tower, header_size=50):
    if tower.kill_count >= tower.spell_kills:
        pygame.draw.circle(surf, colors['spell_charge']['spell_ready'], tower.rect.center, tower.rect.width/2 + 3)
    if is_hovered(tower):
        size = tower.kill_count * header_size / tower.spell_kills
        if tower.level >= 3:
            if tower.kill_count > tower.spell_kills:
                size = header_size
            pygame.draw.rect(surf, colors['spell_charge']['bar'], pygame.Rect(tower.rect.centerx-header_size//2, tower.rect.bottom+10, header_size, 5))
            pygame.draw.rect(surf, colors['spell_charge']['kills'], pygame.Rect(tower.rect.centerx-header_size//2, tower.rect.bottom+10, size, 5))




def upgrade_tower(tower, tower_level=None):
    if tower.level < 2:
        if level.gold >= tower.upgrade_price[tower.level]:
            level.gold -= tower.upgrade_price[tower.level]
            tower.upgrade()
            return True
    else:
        if level.gold >= tower.upgrade_price[tower_level]:
            level.gold -= tower.upgrade_price[tower_level]
            tower.upgrade(tower_level+1)
            return True
    return False


def render_tower_range(surf, tower):
    surface = pygame.Surface((tower.fire_range*2, tower.fire_range*2), pygame.SRCALPHA)
    color = rgb(colors['towers']['range'], 150)
    pygame.draw.circle(surface, color, (surface.get_width()/2, surface.get_height()/2), tower.fire_range, 7)
    surf.blit(surface, (tower.rect.centerx - tower.fire_range, tower.rect.centery - tower.fire_range))


class Slot():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.x = x
        self.y = y


class Tower():
    price = 0
    upgrade_price = [0]
    kill_count = 0
    spell_kills = 1
    spell = None
    spell_radius = 60
    spell_color = None
    def __init__(self, x, y):
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.timer = 0
        self.target = None
        self.level = 0
        self.hovered_color = colors['towers'][self.__class__.__name__]['hovered']
        self.colors = colors['towers'][self.__class__.__name__]['levels']
        self.bullet_color = colors['bullets'][self.__class__.__name__]
        self.color = self.colors[self.level]
        self.can_shoot = True
        
    def upgrade(self, level=None):
        if level is not None:
            self.level = level
        else:
            self.level += 1
        for attr in self.upgrade_dict[self.level]:
            setattr(self, attr, self.upgrade_dict[self.level][attr])
        self.color = self.colors[self.level]
        
    def update(self):
        if self.target is not None:
            if not self.entity_in_range(self.target):
                self.target.tower_targeted.remove(self)
                self.remove_target()
        
        if self.target is None:
            distances = self.mobs_in_range()
            if distances:
                self.target = distances[min(distances)]
                self.target.tower_targeted.append(self)
        
        if self.can_shoot and self.target is not None:
            self.shoot()
            self.can_shoot = False
        
        if self.can_shoot == False:
            self.timer += c.dt
            if self.timer >= self.firerate:
                self.timer = 0
                self.can_shoot = True
        
    def entity_in_range(self, mob):
        d = distance(self, mob)
        if d > self.fire_range:
            return False
        else:
            return True
        
    def mobs_in_range(self):
        distances = {}
        for mob in c.mobs:
            d = distance(self, mob)
            if d < self.fire_range:
                distances[d] = mob
        return distances
        
    def remove_target(self):
        self.target = None
        
    def shoot(self):
        ...


class BaseTower(Tower):
    price = 100
    damage = 20
    firerate = 2000
    fire_range = 120
    upgrade_price = [120, 150, 200, 200]
    bullet_velocity = 4
    bullet = BaseBullet
    
    def __init__(self, x, y):
        self.upgrade_dict = {
            1: {
                'damage': 30
                },
            2: {
                "damage": 50
                },
            3: {
                "bullet"     : SlowBullet,
                "spell"      : Blizzard,
                "spell_color": 'blue'
                },
            4: {
                "firerate": 4000,
                "damage": 0.5,
                "bullet": RayBullet,
                "update": self.RayUpdate,
                "remove_target": self.Ray_remove_target,
                "shoot": self.shoot_ray,
                "target": None
                }
            }
        super().__init__(x, y)
        self.shooting = False
        self.ray = None
        
    def Ray_remove_target(self):
        self.target = None
        self.remove_ray()
        
    def remove_ray(self):
        try:
            c.bullets.remove(self.ray)
        except Exception as ray_crash:
            print(ray_crash)
        self.shooting = False
        self.ray = None
        
    def RayUpdate(self):
        if self.target is not None:
            if not self.entity_in_range(self.target):
                self.target.tower_targeted.remove(self)
                self.remove_target()
        
        if self.target is None:
            distances = self.mobs_in_range()
            if distances:
                self.target = distances[min(distances)]
                self.target.tower_targeted.append(self)
        
        if self.target is not None and not self.shooting:
            self.ray = self.shoot()
            self.shooting = True
    
    def shoot_ray(self):
        bullet = self.bullet(
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color, self)
        c.bullets.append(bullet)
        return bullet
        
    def shoot(self):
        c.bullets.append(self.bullet(
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color, self))


class ExplosiveTower(Tower):
    price = 120
    damage = 50
    firerate = 4000
    fire_range = 100
    explosion_radius = 50
    upgrade_price = [160, 200, 250, 250]
    bullet = ExplosiveBullet
    exp_color1, exp_color2 = colors['explosion'][0]['color1'], colors['explosion'][0]['color2']
    upgrade_dict = {
        1: {
            'damage': 90,
            'explosion_radius': 60
            },
        2: {
            'damage': 120,
            'explosion_radius': 70
            },
        3: {
            'firerate': 5000,
            'damage': 200,
            'explosion_radius': 100,
            'bullet_color': None,
            'spell': Lightning,
            'spell_color': colors['towers']['ExplosiveTower']['spell1']
            },
        4: {
            'firerate': 1000,
            'damage': 35,
            'fire_range': 140,
            'explosion_radius': 140
            }
        }
    
    def upgrade(self, level=None):
        super().upgrade(level)
        if self.level == 3 or self.level == 4:
            self.exp_color1 = colors['explosion'][self.level]['color1']
            self.exp_color2 = colors['explosion'][self.level]['color2']
            if self.level == 4:
                self.shoot = self.shoot_lvl4
    
    def shoot_lvl4(self):
        target = SimpleNamespace(targeted=[])
        bullet = self.bullet(
            self.rect.centerx, self.rect.centery,
            target, self.damage, self.explosion_radius,
            self.bullet_color, self.exp_color1, self.exp_color2, self
            )
        bullet.explode()
        c.bullets.append(bullet)
    
    def shoot(self):
        c.bullets.append(self.bullet(
            self.rect.centerx, self.rect.centery,
            self.target, self.damage, self.explosion_radius,
            self.bullet_color, self.exp_color1, self.exp_color2, self
            ))


class RapidFireTower(Tower):
    price = 100
    damage = 8
    firerate = 1000
    fire_range = 160
    upgrade_price = [120, 150, 200, 200]
    bullet_velocity = 5
    upgrade_dict = {
        1: {
            'damage': 10
            },
        2: {
            "damage": 15
            },
        3: {
            'fire_range': 140,
            'firerate': 500,
            'damage': 20
            },
        4: {
            'fire_range': 240,
            'firerate': 2500,
            'damage': 80,
            'bullet_velocity': 8
            }
        }
    
    def shoot(self):
        c.bullets.append(BaseBullet(
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color, self))


class SoldierTower(Tower):
    price = 100
    damage = 10
    respawn = 8000
    number = 1
    velocity = 1
    soldier_range = 120
    life = 60
    attack_rate = 1600
    life_regeneration = 0.1
    upgrade_price = [120, 150, 200, 200]
    upgrade_dict = {
        1: {
            'damage': 15,
            'life': 80,
            'number': 2
            },
        2: {
            'life': 100,
            'attack_rate': 1400,
            'number': 3
            },
        3: {
            'number': 4,
            'life': 150,
            "spell_radius": 20,
            "spell_color": colors['towers']['SoldierTower']['spell1'],
            "spell": GolemSpell
            },
        4: {
            'number': 4,
            'soldier_range': 150,
            'attack_rate': 800,
            'velocity': 2,
            "spell_color": colors['towers']['SoldierTower']['spell2'],
            "spell": Rage
            }
        }
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.fire_range = self.soldier_range
        self.soldiers = {0: None, 1: None, 2: None, 3: None, 4:None}
        self.selected_soldier = None
        self.respawn_timer = 0
        self.respawn_list = []
        
        distances = {}
        for pos in concatenate(*c.point_paths):
            dx = pos[0] - self.rect.centerx
            dy = pos[1] - self.rect.centery
            distances[sqrt(dx**2 + dy**2)] = pos
        nearest_pos = distances[min(distances)]
        
        self.pos = [
            (nearest_pos[0] - SOLDIER_SIZE - SOLDIER_SIZE//2, nearest_pos[1] - SOLDIER_SIZE - SOLDIER_SIZE//2),
            (nearest_pos[0] + SOLDIER_SIZE - SOLDIER_SIZE//2, nearest_pos[1] - SOLDIER_SIZE - SOLDIER_SIZE//2),
            (nearest_pos[0] - SOLDIER_SIZE - SOLDIER_SIZE//2, nearest_pos[1] + SOLDIER_SIZE - SOLDIER_SIZE//2),
            (nearest_pos[0] + SOLDIER_SIZE - SOLDIER_SIZE//2, nearest_pos[1] + SOLDIER_SIZE - SOLDIER_SIZE//2)
            ]
        
        for i in range(self.number):
            self.add_soldier(i)
    
    def upgrade(self, level=None):
        super().upgrade(level)
        self.respawn_list = []
        self.respawn_timer = 0
        for i in range(self.number):
            # respawn dead soldier with new attr
            if self.soldiers[i] is None:
                self.add_soldier(i)
            else:
                # update / restore alive soldier attr
                self.soldiers[i].life = self.life
                self.soldiers[i].max_life = self.life
                self.soldiers[i].damage = self.damage
                self.soldiers[i].attack_rate = self.attack_rate
                self.soldiers[i].velocity = self.velocity
                self.soldiers[i].color = colors['soldier']['normal']
        self.fire_range = self.soldier_range
    
    def add_soldier(self, index):
        self.soldiers[index] = Soldier(
            *self.pos[index], self, self.life, self.damage, self.attack_rate,
            self.velocity, self.life_regeneration, colors['soldier']['normal'])
        c.soldiers.append(self.soldiers[index])
    
    def dead_soldier(self, soldier):
        for s in self.soldiers.items():
            if s[1] == soldier:
                key = s[0]
                break
        self.pos[key] = soldier.rect.topleft
        self.soldiers[key] = None
        self.respawn_list.append(key)
        
    def dead_golem(self, golem):
        c.soldiers.remove(golem)
        for s in self.soldiers.items():
            if s[1] == golem:
                key = s[0]
                break
        self.soldiers[key] = None
    
    def update(self):
        # change selected soldier when hovered
        if is_hovered(self):
            if c.keys[pygame.K_1]:
                self.selected_soldier = self.soldiers[0]
            elif c.keys[pygame.K_2]:
                self.selected_soldier = self.soldiers[1]
            elif c.keys[pygame.K_3]:
                self.selected_soldier = self.soldiers[2]
            elif c.keys[pygame.K_4]:
                self.selected_soldier = self.soldiers[3]
            elif c.keys[pygame.K_4]:
                self.selected_soldier = self.soldiers[4]
            # move it
            if self.selected_soldier is not None:
                self.selected_soldier.move()
        
        # check for respawn
        if self.respawn_list and self.respawn_timer == 0:
            self.respawn_timer = 1
        if self.respawn_timer > 0:
            self.respawn_timer += c.dt
            if self.respawn_timer > self.respawn:
                self.respawn_timer = 0
                self.add_soldier(self.respawn_list[0])
                self.respawn_list.pop(0)
        
        # update alive soldiers
        for soldier in self.soldiers.values():
            if soldier is not None:
                soldier.update()
