
from random import randint, choice
from math import pi, cos, sin, atan2
import pygame

import core as c
import level


PALETTE = ((255, 255, 0 ),
           (255, 173, 51),
           (247, 117, 33),
           (191, 74 , 46),
           (115, 61 , 56),
           (61 , 38 , 48))[::-1] # reverse the color order


def init_vfx():
    level.fire_mgr = FireManager(2, c.WIN_SIZE)


# SPARKS VFX ------------------------------------------------------------------

class Spark():
    def __init__(self, loc, angle, speed, color, scale=1):
        self.loc = list(loc)
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True
        
    def point_towards(self, angle, rate):
        rotate_direction = ((angle - self.angle + pi * 3) % (pi * 2)) - pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sign = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign
        
    def calculate_movement(self, dt):
        return [cos(self.angle) * self.speed * dt, sin(self.angle) * self.speed * dt]
    
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] *= friction
        self.angle = atan2(movement[1], movement[0])
        
    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]
        
        self.point_towards(pi / 2, 0.02)
        self.velocity_adjust(0.975, 0.2, 8, dt)
        # self.angle += 0.1
        
        self.speed -= 0.5
        if self.speed <= 0:
            self.alive = False
            c.sparks.remove(self)
        
    def render(self, surf):
        if self.alive:
            points = [
                [self.loc[0] + cos(self.angle) * self.speed * self.scale, self.loc[1] + sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + cos(self.angle + pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + sin(self.angle + pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + cos(self.angle - pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - sin(self.angle + pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)


# FIRE VFX --------------------------------------------------------------------

class FireParticle:
    def __init__(self, x, y, size):
        self.x, self.y = x, y
        self.maxlife = randint(13 + int(size*5), 27 + int(size*10))
        self.life = self.maxlife
        self.dir = choice((-2, -1, 1, 2))
        self.sin = randint(-10, 10)/7
        self.sinr = randint(5, 10)
        self.r = randint(0,2)
        self.ox = randint(-1, 1)
        self.oy = randint(-1, 1)


class Fire():
    def __init__(self, x, y, size, density, rise, spread, wind, duration, palette):
        self.particles = list()
        self.dead = list()
        self.j = 0
        self.x, self.y = x, y
        self.size = size
        self.density = density
        self.rise = rise
        self.spread = spread
        self.wind = wind
        self.palette = palette
        self.duration = duration
        self.alive = True


class FireManager():
    def __init__(self, res, win_size):
        self.res = res
        self.win_size = win_size
        self.bsurf = pygame.Surface((win_size[0]//res, win_size[1]//res), pygame.SRCALPHA).convert_alpha()
        self.fires = []
    
    def addFire(self, x, y, size=2.9, density=3, rise=1.25, spread=1, wind=0, duration=5000, palette=PALETTE):
        self.fires.append(Fire(x, y, size, density, rise, spread, wind, duration, palette))
    
    def update_render(self, surf, dt):
        self.bsurf.fill((0, 0, 0, 0))
        
        for fire in self.fires:
            fire.duration -= dt
            if fire.duration <= 0:
                fire.alive = False
                if not fire.particles:
                    self.fires.remove(fire)
                    continue
            
            fire.j += 1
            if fire.j > 360:
                fire.j = 0
            
            if fire.alive:
                for _ in range(round(fire.density)):
                    fire.particles.append(FireParticle(fire.x//self.res, fire.y//self.res, fire.size))
            
                pygame.draw.circle(self.bsurf, fire.palette[5], (fire.x//self.res, fire.y//self.res-2), 2, 0)
            
            for p in fire.particles:
                p.life -= 1
                if p.life == 0:
                    fire.dead.append(p)
                    continue
                
                i = int((p.life/p.maxlife)*6)
                
                p.y -= fire.rise
                p.x += ((p.sin * sin(fire.j/(p.sinr)))/2) * fire.spread + fire.wind
                
                if not randint(0, 5):
                    p.r += 0.88
                    
                x, y = p.x, p.y
                
                x += p.ox*(5-i)
                y += p.oy*(5-i)
                
                alpha = 255
                if p.life < p.maxlife/4:
                    alpha = int((p.life/p.maxlife)*255)
                
                pygame.draw.circle(self.bsurf, fire.palette[i] + (alpha,), (x, y), p.r, 0)
                
                if i == 0:
                    pygame.draw.circle(self.bsurf, (0, 0, 0, 0), (x+randint(-1, 1), y-4), p.r*(((p.maxlife-p.life)/p.maxlife)/0.88), 0)
                else:
                    pygame.draw.circle(self.bsurf, fire.palette[i-1] + (alpha,), (x+randint(-1, 1), y-3), p.r/1.5, 0)
            
            for p in fire.dead:
                fire.particles.remove(p)
            fire.dead.clear()
        
        surf.blit(pygame.transform.scale(self.bsurf, self.win_size), (0, 0))
