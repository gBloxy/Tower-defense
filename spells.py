import pygame
from math import pi, sqrt, cos, sin
from random import uniform
from types import SimpleNamespace

import core as c
from functions import distance_mouse, rgb
from colors import colors
from bullets import ExplosiveBullet
from entities import Golem

def FireSpell(radius, explosion_radius, damage, number):
    for i in range(number):
        angle = uniform(0, 2 * pi)
        r = radius * sqrt(uniform(0, 1))
        pos = (c.mouse_pos[0] + r * cos(angle), c.mouse_pos[1] + r * sin(angle))
        bullet = ExplosiveBullet(*pos, SimpleNamespace(targeted=[]), damage, explosion_radius, None, colors['explosion'][0].values(), colors['explosion'][0].values(), SimpleNamespace(level=0))
        bullet.explode()
        c.bullets.append(bullet)
        
class Spell():
    
    duration = 0
        
    def cast(self, tower):
        ...
        
    def render(self):
        ...
        
class Blizzard(Spell):
    
    duration = 5000
    radius = 60
    def __init__(self):
        self.duration = 0
        self.pos = None

    def update(self):
        if self.duration != 0:
            self.duration -= c.dt
        if self.duration <= 0:
            self.duration = 0
            self.render()
    
    def cast(self, tower):
        damage = 20
        freeze_time = 5000
        self.duration = freeze_time
        self.pos = c.mouse_pos
        for mob in c.mobs:
            d = distance_mouse(mob)
            if d <= self.radius:
                mob.life -= damage
                mob.slow_effect(0, freeze_time)
    
    def render(self):
        surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        color = 'lightblue'
        pygame.draw.circle(surface, rgb(color, 120), (self.radius, self.radius), self.radius)
        surface.blit(surface, (self.pos[0] - self.radius, self.pos[1] - self.radius))
        
class Lightning(Spell):
    
    def cast (self, tower):
        damage = 100
        radius = 30
        for mob in c.mobs:
            d = distance_mouse(mob)
            if d <= radius:
                mob.life -= damage
                mob.slow_effect(0, 250)
       
class GolemSpell(Spell):
    
    def cast(self, tower):
        if tower.soldiers[4] != None:
            tower.soldiers[4].death()
        tower.soldiers[4] = Golem(
            (c.mouse_pos[0] - c.SOLDIER_SIZE, c.mouse_pos[1] - c.SOLDIER_SIZE), tower,
            300, 60, 2200, 1, 0,  colors['soldier']['golem'])
        c.soldiers.append(tower.soldiers[4])

class Rage(Spell):
    
    def cast(self, tower):
        radius = 90
        rage_duration = 5000
        #for tower in towers:
         #   d = distance_spell(tower)
          #  if d <= radius:
           #     tower.rage = True
        for soldier in c.soldiers:
            d = distance_mouse(soldier)
            if d <= radius:
                soldier.rage_timer = rage_duration
                soldier.rage = True