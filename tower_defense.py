
from math import cos, sin, sqrt, atan2, pi
from random import uniform
from types import SimpleNamespace
from sys import exit
import pygame
pygame.init()


WIN_SIZE = [600, 400]

TILE_SIZE = 40
BULLET_SIZE = TILE_SIZE//5
MOB_SIZE = TILE_SIZE//2.5 # 2
SOLDIER_SIZE = TILE_SIZE//3.5 # 3


window = pygame.display.set_mode(WIN_SIZE)
clock = pygame.time.Clock()

life_font = pygame.font.SysFont('arial', 30)
game_over_font = pygame.font.SysFont('impact', 80)

_ = 0

ADJACENTS = [
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1)
]

# CONFIGURATION ---------------------------------------------------------------

colors = {
    'UI': {
        'life': 'red',
        'gold': 'yellow',
        'over': 'red'
        },
    'map': {
        0: 'chartreuse2',  # grass
        1: (155, 118, 83), # path
        2: 'orange',       # spawn
        3: 'whitesmoke',   # flag
        4: 'chartreuse2',  # slot
        },
    'debug': 'black', # target line
    'header': {
        'life': 'darkgreen',
        'bkg' : 'indianred3',
        'slow': 'lightblue'
        },
    'slots': {
        'normal': 'gray',
        'hovered': 'lightgray'
        },
    'bullets': {
        'crashed'       : 'goldenrod4',
        'BaseTower'     : 'mediumblue',
        'ExplosiveTower': 'darkgoldenrod',
        'RapidFireTower': 'whitesmoke',
        'SoldierTower'  : None
        },
    'mobs': 'red',
    'soldier': {
        'selected': 'blue',
        'normal'  : 'darkgray'
        },
    'explosion': {
        0: { # fire
            'color1': 'orange2',
            'color2': 'orangered3'
            },
        3: { # lightning
            'color1': 'cyan',
            'color2': 'azure1'
            },
        4: { # super fire
            'color1': 'orange2',
            'color2': 'orange3'
            }
        },
    'towers': {
        'range'  : 'lightgreen',
        'default': 'black',
        'Tower': { # default
            'hovered': 'darkgray',
            'levels' : ['black']
            },
        'BaseTower': {
            'hovered': 'dodgerblue',
            'levels' : ['blue', 'dodgerblue4', 'darkblue', 'cadetblue1', 'lightsteelblue3']
            },
        'ExplosiveTower': {
            'hovered': 'gold1',
            'levels' : ['red1', 'crimson', 'darkred', 'cyan', 'orangered3']
            },
        'RapidFireTower': {
            'hovered': 'dodgerblue',
            'levels' : ['thistle2', 'violet', 'orchid3', 'ivory', 'mediumorchid4']
            },
        'SoldierTower': {
            'hovered': 'dodgerblue',
            'levels' : ['darkgray', 'lightgray', 'brown', 'red', 'yellow']
            }
        }
}


# FUNCTIONS -------------------------------------------------------------------

def close():
    pygame.quit()
    exit()


def rgb(color_name: str, alpha: int = 255):
    color = pygame.Color(color_name)
    return [color.r, color.g, color.b, alpha]


def blit_center(surface, image, pos):
    surface.blit(image, (pos[0] - image.get_width()//2, pos[1] - image.get_height()//2))


def concatenate(*lists):
    all_values = []
    for l in lists:
        all_values += l
    return list(set(all_values))


def lerp(a, b, t):
    return a + t * (b - a)


def distance(tower, mob):
    return sqrt((mob.rect.centerx - tower.rect.centerx)**2 + (mob.rect.centery - tower.rect.centery)**2)


def interpolate_points(point1, point2, num_points):
    interpolated_points = []
    for i in range(num_points + 1):
        t = i / num_points
        x_t = lerp(point1[0], point2[0], t)
        y_t = lerp(point1[1], point2[1], t)
        interpolated_points.append((int(x_t), int(y_t)))
    return interpolated_points


def Parse(MAP):
    slots, spawns, flags = [], [], []
    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            if tile == 4:
                slots.append(Slot(x, y))
            elif tile == 2:
                spawns.append((x, y))
            elif tile == 3:
                flags.append((x, y))
    return slots, spawns, flags


def Path(spawn, flag, blacklist):
    tile_path, point_path, path = [], [], []
    # find the tile path position
    current = spawns[spawn]
    while current != flags[flag]:
        for (x, y) in ADJACENTS:
            pos = (current[0]+x, current[1]+y)
            tile = Map[pos[1]][pos[0]]
            if tile == 1 and pos != current and not pos in tile_path and not pos in blacklist:
                tile_path.append(current)
                current = pos
                break
            elif tile == 3:
                tile_path.append(current)
                current = pos
                tile_path.append(current)
                break
    # convert it to pixel points path
    for pos in tile_path:
        point_path.append((pos[0]*TILE_SIZE + TILE_SIZE//2, pos[1]*TILE_SIZE + TILE_SIZE//2))
    # connect it to linear pixel path
    for i in range(len(point_path) - 1):
        path.extend(interpolate_points(point_path[i], point_path[i+1], 90))
    return tile_path, point_path, path


def is_hovered(entity):
    if entity.rect.collidepoint(*mouse_pos):
        return True
    else:
        return False

def is_clicked(entity):
    if click and entity.rect.collidepoint(*mouse_pos):
        return True
    else:
        return False


def collision_list(entity, collideables):
    hit_list = []
    for e in collideables:
        if e.rect.colliderect(entity.rect):
            hit_list.append(e)
    return hit_list


def render_mob_header(entity, header_size=50):
    size = entity.life * header_size / entity.max_life
    pygame.draw.rect(window, colors['header']['bkg'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-10, header_size, 5))
    pygame.draw.rect(window, colors['header']['life'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-10, size, 5))
    if entity.slow_timer != 0:
        size = entity.slow_timer * header_size / SlowBullet.effect_time
        pygame.draw.rect(window, colors['header']['slow'], pygame.Rect(entity.rect.centerx-header_size//2, entity.rect.top-5, size, 2))


def render_tower_range(tower):
    surface = pygame.Surface((tower.fire_range*2, tower.fire_range*2), pygame.SRCALPHA)
    color = rgb(colors['towers']['range'], 150)
    pygame.draw.circle(surface, color, (surface.get_width()/2, surface.get_height()/2), tower.fire_range, 7)
    window.blit(surface, (tower.rect.centerx - tower.fire_range, tower.rect.centery - tower.fire_range))


# SPELLS ----------------------------------------------------------------------

def FireSpell(radius, explosion_radius, damage, number):
    for i in range(number):
        angle = uniform(0, 2 * pi)
        r = radius * sqrt(uniform(0, 1))
        pos = (mouse_pos[0] + r * cos(angle), mouse_pos[1] + r * sin(angle))
        bullet = ExplosiveBullet(*pos, SimpleNamespace(targeted=[]), damage, explosion_radius, None, *colors['explosion'][0].values())
        bullet.explode()
        bullets.append(bullet)


# ENTITIES CLASSES ------------------------------------------------------------

class Mob():
    def __init__(self, x, y, path):
        self.rect = pygame.Rect(x*TILE_SIZE + MOB_SIZE//2, y*TILE_SIZE + MOB_SIZE//2, MOB_SIZE, MOB_SIZE)
        self.max_life = self.life
        self.path = path.copy()
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
        global gold
        self._life = value
        if self._life <= 0:
            gold += self.ret
            self.remove()
        
    def remove(self):
        for bullet in self.targeted:
            bullet.remove_target()
        for tower in self.tower_targeted:
            tower.remove_target()
        if self.collided is not None:
            self.collided.target = None
        mobs.remove(self)
    
    def update(self):
        if self.slow_timer != 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_timer = 0
                self.velocity = self.normal_velocity
        
        if self.collided is None:
            hit_list = collision_list(self, soldiers)
            for soldier in hit_list:
                if not soldier.moving and soldier.target is None:
                    self.collided = soldier
                    soldier.target = self
                    break
        
        if self.collided is None:
            for i in range(self.velocity):
                self.rect.center = self.path[0]
                self.path.pop(0)
                if self.path == []:
                    return False
        
        if self.timer == 0 and self.collided is not None:
            self.collided.life -= self.damage
            self.timer = 1
        
        if self.timer > 0:
            self.timer += dt
            if self.timer > self.attack_rate:
                self.timer = 0
        return True
    
    def slow_effect(self, speed, time):
        self.velocity = speed
        self.slow_timer = time


class GoblinMob(Mob):
    _life = 60
    ret = 30
    velocity = 2
    damage = 10
    attack_rate = 2200


class OrcMob(Mob):
    _life = 80
    ret = 40
    velocity = 2
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
            self.timer += dt
            if self.timer > self.attack_rate:
                self.timer = 0
        
    def attack(self):
        self.target.life -= self.damage
    
    def remove(self):
        if self.target is not None:
            self.target.collided = None
        self.tower.dead_soldier(self)
        soldiers.remove(self)
    
    def move(self):
        if keys[pygame.K_z]:
            self.motion[1] -= self.velocity
        if keys[pygame.K_s]:
            self.motion[1] += self.velocity
        if keys[pygame.K_q]:
            self.motion[0] -= self.velocity
        if keys[pygame.K_d]:
            self.motion[0] += self.velocity


# SLOT CLASS ------------------------------------------------------------------

class Slot():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.x = x
        self.y = y


# BULLETS CLASSES -------------------------------------------------------------

class Bullet():
    dispawn = 10000
    def __init__(self, x, y, target, damage, speed, color, parent=None):
        self.parent = parent
        self.target = target
        self.target.targeted.append(self)
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
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
                crashed_bullets.append(self)
            bullets.remove(self)
        
        elif not self.have_target:
            for mob in mobs:
                if self.rect.colliderect(mob.rect):
                    mob.life -= self.damage
                    bullets.remove(self)
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
            self.timer -= dt
            if self.timer <= 0:
                bullets.remove(self)
    
    def explode(self):
        self.exploding = True
        for mob in mobs:
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
                crashed_bullets.append(self)
            bullets.remove(self)
        
        elif not self.have_target:
            for mob in mobs:
                if self.rect.colliderect(mob.rect):
                    self.impact(mob)
                    bullets.remove(self)
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


# TOWERS CLASSES --------------------------------------------------------------

class Tower():
    price = 0
    upgrade_price = [0]
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
            self.timer += dt
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
        for mob in mobs:
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
                "bullet": SlowBullet
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
        self.shooting = False
        bullets.remove(self.ray)
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
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color, parent=self)
        bullets.append(bullet)
        return bullet
        
    def shoot(self):
        bullets.append(self.bullet(
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color))


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
            'bullet_color': None
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
            self.bullet_color, self.exp_color1, self.exp_color2
            )
        bullet.explode()
        bullets.append(bullet)
    
    def shoot(self):
        bullets.append(self.bullet(
            self.rect.centerx, self.rect.centery,
            self.target, self.damage, self.explosion_radius,
            self.bullet_color, self.exp_color1, self.exp_color2
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
        bullets.append(BaseBullet(
            self.rect.centerx, self.rect.centery, self.target, self.damage, self.bullet_velocity, self.bullet_color))


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
            'number': 4
            },
        4: {
            'number': 4,
            'soldier_range': 150,
            'life': 120,
            'attack_rate': 800,
            'velocity': 2
            }
        }
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.fire_range = self.soldier_range
        self.soldiers = {0: None, 1: None, 2: None, 3: None}
        self.selected_soldier = None
        self.respawn_timer = 0
        self.respawn_list = []
        
        distances = {}
        for pos in concatenate(*point_paths):
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
        soldiers.append(self.soldiers[index])
    
    def dead_soldier(self, soldier):
        for s in self.soldiers.items():
            if s[1] == soldier:
                key = s[0]
                break
        self.pos[key] = soldier.rect.topleft
        self.soldiers[key] = None
        self.respawn_list.append(key)
    
    def update(self):
        # change selected soldier when hovered
        if is_hovered(self):
            if keys[pygame.K_1]:
                self.selected_soldier = self.soldiers[0]
            elif keys[pygame.K_2]:
                self.selected_soldier = self.soldiers[1]
            elif keys[pygame.K_3]:
                self.selected_soldier = self.soldiers[2]
            elif keys[pygame.K_4]:
                self.selected_soldier = self.soldiers[3]
            # move it
            if self.selected_soldier is not None:
                self.selected_soldier.move()
        
        # check for respawn
        if self.respawn_list and self.respawn_timer == 0:
            self.respawn_timer = 1
        if self.respawn_timer > 0:
            self.respawn_timer += dt
            if self.respawn_timer > self.respawn:
                self.respawn_timer = 0
                self.add_soldier(self.respawn_list[0])
                self.respawn_list.pop(0)
        
        # update alive soldiers
        for soldier in self.soldiers.values():
            if soldier is not None:
                soldier.update()


# GAME VARIABLES --------------------------------------------------------------

DEV_MOD = 1
DEBUG_MOD = 0

spawn_frequency = 5500 # ms
max_spawn_frequency = 1400 # ms
timer = 0
spell_timer = 0

gold = 100000 if DEV_MOD else 140
life = 100 if DEV_MOD else 3

game_over = False

mobs = []
slots = []
towers = []
bullets = []
crashed_bullets = []
soldiers = []

tile_paths = []
point_paths = []
paths = []


# LEVEL VARIABLES -------------------------------------------------------------

Map = [ # 15 cols 10 rows
    [_, _, _, 2, _, 4, _, 4, _, 4, _, 4, _, _, _],
    [_, 4, _, 1, _, _, _, _, _, _, _, _, _, _, _],
    [_, 4, _, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, _, 4],
    [_, _, _, _, _, _, _, _, _, _, _, _, 1, _, _],
    [2, 1, 1, 1, 1, _, 4, _, 4, _, 4, _, 1, _, 4],
    [_, _, _, _, 1, _, _, _, _, _, _, _, 1, _, _],
    [_, 4, 4, _, 1, 1, 1, 1, 1, 1, 1, 1, 1, _, 4],
    [_, _, _, _, _, _, _, _, _, 1, _, _, _, _, _],
    [_, _, _, _, 4, _, 4, 4, _, 1, _, 4, 4, _, _],
    [_, _, _, _, _, _, _, _, _, 3, _, _, _, _, _]
]

slots, spawns, flags = Parse(Map)

_paths = [(0, 0, [(8, 6)]), (1, 0, [(10, 6)])] # (spawns[nb] to flags[nb] with blacklist [(pos)])
for path in _paths:
    tiles, points, line = Path(*path)
    tile_paths.append(tiles)
    point_paths.append(points)
    paths.append(line)

# wave_configuration = [
#     [
#      {'enemy': GoblinMob, 'quantity': 3, 'time': 5500, 'initial': 2500, 'path': 0},
#      {'enemy': GoblinMob, 'quantity': 2, 'time': 5500, 'initial': 4000, 'path': 1}
#      ],
#     [
#      {'enemy': GoblinMob, 'quantity': 8, 'time': 4500 , 'initial': 2500},
#      {'enemy': GoblinMob, 'quantity': 8, 'time': 4500 , 'initial': 2500},
#      {'enemy': OrcMob,    'quantity': 3, 'time': 10000, 'initial': 4500}
#      ]
# ]


# GAMELOOP --------------------------------------------------------------------

try:
    while True:
        dt = clock.tick(30)
        events = pygame.event.get()
        click = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                click = True
            elif e.type == pygame.QUIT:
                close()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            close()
        mouse_pos = pygame.mouse.get_pos()
        window.fill('white')
        
        # DEV MOD tools
        if DEV_MOD:
            for mob in mobs:
                if is_clicked(mob):
                    mob.remove()
            if keys[pygame.K_RIGHT]:
                for p in paths:
                    mobs.append(GoblinMob(*spawns[0], p))
                pygame.time.wait(200)
            if keys[pygame.K_UP]:
                spawn_frequency -= 120
            if keys[pygame.K_DOWN]:
                spawn_frequency += 120
            if keys[pygame.K_LEFT]:
                print(clock.get_fps())
        
        # spawn new mob
        if not game_over:
            timer += dt
            if timer > spawn_frequency:
                timer = 0
                if spawn_frequency > max_spawn_frequency:
                    spawn_frequency -= 120
                    if spawn_frequency < max_spawn_frequency:
                        spawn_frequency == max_spawn_frequency
                mobs.append(GoblinMob(*spawns[0], paths[0]))
                mobs.append(GoblinMob(*spawns[0], paths[1]))
        
        # render map
        for y, row in enumerate(Map):
            for x, tile in enumerate(row):
                pygame.draw.rect(window, colors['map'][tile], pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # update slots
        for slot in slots:
            pygame.draw.circle(window, colors['slots']['normal'], slot.rect.center, TILE_SIZE//2)
            if not game_over and is_hovered(slot):
                pygame.draw.circle(window, colors['slots']['hovered'], slot.rect.center, TILE_SIZE//2)
                if keys[pygame.K_1]:
                    if gold >= BaseTower.price:
                        gold -= BaseTower.price
                        slots.remove(slot)
                        towers.append(BaseTower(slot.x, slot.y))
                elif keys[pygame.K_2]:
                    if gold >= ExplosiveTower.price:
                        gold -= ExplosiveTower.price
                        slots.remove(slot)
                        towers.append(ExplosiveTower(slot.x, slot.y))
                elif keys[pygame.K_3]:
                    if gold >= RapidFireTower.price:
                        gold -= RapidFireTower.price
                        slots.remove(slot)
                        towers.append(RapidFireTower(slot.x, slot.y))
                elif keys[pygame.K_4]:
                    if gold >= SoldierTower.price:
                        gold -= SoldierTower.price
                        slots.remove(slot)
                        towers.append(SoldierTower(slot.x, slot.y))
        
        # update and render towers
        for tower in towers:
            pygame.draw.circle(window, tower.color, tower.rect.center, tower.rect.width/2)
            if not game_over:
                if is_clicked(tower):
                    if tower.level < 2:
                        if gold >= tower.upgrade_price[tower.level]:
                            gold -= tower.upgrade_price[tower.level]
                            tower.upgrade()
                if is_hovered(tower):
                    if tower.level == 2:
                        if keys[pygame.K_1]:
                            if gold >= tower.upgrade_price[2]:
                                gold -= tower.upgrade_price[2]
                                tower.upgrade(3)
                        elif keys[pygame.K_2]:
                            if gold >= tower.upgrade_price[3]:
                                gold -= tower.upgrade_price[3]
                                tower.upgrade(4)
                    pygame.draw.circle(window, tower.hovered_color, tower.rect.center, tower.rect.width/2)
                    render_tower_range(tower)
                tower.update()
            if DEBUG_MOD and tower.target is not None:
                pygame.draw.line(window, colors['debug'], tower.rect.center, tower.target.rect.center, 2)
        
        # render crashed bullets
        for bullet in crashed_bullets:
            bullet.timer -= dt
            if bullet.timer <= 0:
                crashed_bullets.remove(bullet)
            else:
                pygame.draw.circle(window, colors['bullets']['crashed'], bullet.rect.center, bullet.rect.width/2)
        
        # spell
        if spell_timer != 0:
            spell_timer += dt
            if spell_timer >= 2000:
                spell_timer = 0
        elif keys[pygame.K_SPACE]:
            FireSpell(radius=45, explosion_radius=35, damage=100, number=3)
            spell_timer = 1
        
        # update and render bullets
        for bullet in bullets:
            if not game_over:
                bullet.update()
            bullet.render(window)
        
        # update and render mobs
        for mob in mobs:
            if not game_over:
                if not mob.update():
                    mob.remove()
                    life -= 1
                    # life checking
                    if life == 0:
                        game_over = True
            pygame.draw.circle(window, colors['mobs'], mob.rect.center, mob.rect.width/2)
            render_mob_header(mob)
        
        # render soldier
        for soldier in soldiers:
            if is_hovered(soldier.tower) and soldier == soldier.tower.selected_soldier:
                pygame.draw.rect(window, colors['soldier']['selected'], soldier.rect)
            else:
                pygame.draw.rect(window, soldier.color, soldier.rect)
            render_mob_header(soldier, header_size=35)
        
        # game over indication
        if game_over:
            blit_center(window, game_over_font.render('GAME OVER', True, colors['UI']['over']), (WIN_SIZE[0]/2, WIN_SIZE[1]/2))
        
        # display the remaining lifes and gold
        window.blit(life_font.render(str(life), True, colors['UI']['life']), (8, 5))
        gold_image = life_font.render(str(gold), True, colors['UI']['gold'])
        window.blit(gold_image, (WIN_SIZE[0] - gold_image.get_width() - 12, 5))
        
        pygame.display.flip()

except Exception as exc:
    pygame.quit()
    raise exc
