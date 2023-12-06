import pygame
from math import pi, sqrt, cos, sin
from random import uniform
from types import SimpleNamespace

import core as c
from functions import distance_mouse, rgb
from colors import colors
from bullets import ExplosiveBullet
from entities import Golem


class Spell():
    duration = 0
    def cast(self, tower):
        ...
        
    def render(self):
        ...


def FireSpell(radius, explosion_radius, damage, number):
    for i in range(number):
        angle = uniform(0, 2 * pi)
        r = radius * sqrt(uniform(0, 1))
        pos = (c.mouse_pos[0] + r * cos(angle), c.mouse_pos[1] + r * sin(angle))
        bullet = ExplosiveBullet(*pos, SimpleNamespace(targeted=[]), damage, explosion_radius, None, colors['explosion'][0]['color1'], colors['explosion'][0]['color2'], SimpleNamespace(level=0))
        bullet.explode()
        c.bullets.append(bullet)


class Blizzard(Spell):
    radius = 60
    damage = 20
    freeze_time = 5000
    def __init__(self, tower):
        self.pos = None
        c.spells.append(self)
        
        self.duration = self.freeze_time
        self.pos = c.mouse_pos
        for mob in c.mobs:
            d = distance_mouse(mob)
            if d <= self.radius:
                mob.life -= self.damage
                mob.slow_effect(0, self.freeze_time)

    def update(self):
        self.duration -= c.dt
        if self.duration <= 0:
            c.spells.remove(self)
    
    def render(self, surf):
        surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, rgb('lightblue', 120), (self.radius, self.radius), self.radius)
        surf.blit(surface, (self.pos[0] - self.radius, self.pos[1] - self.radius))


class Lightning(Spell):
    damage = 100
    radius = 30
    def __init__(self, tower):
        for mob in c.mobs:
            d = distance_mouse(mob)
            if d <= self.radius:
                mob.life -= self.damage
                mob.slow_effect(0, 250)


class GolemSpell(Spell):
    def __init__(self, tower):
        if tower.soldiers[4] != None:
            tower.soldiers[4].death()
        tower.soldiers[4] = Golem(
            (c.mouse_pos[0] - c.SOLDIER_SIZE, c.mouse_pos[1] - c.SOLDIER_SIZE), tower,
            300, 60, 2200, 1, 0,  colors['soldier']['golem'])
        c.soldiers.append(tower.soldiers[4])


class Rage(Spell):
    radius = 90
    rage_duration = 5000
    def __init__(self, tower):
        #for tower in towers:
         #   d = distance_spell(tower)
          #  if d <= radius:
           #     tower.rage = True
        for soldier in c.soldiers:
            d = distance_mouse(soldier)
            if d <= self.radius:
                soldier.rage_timer = self.rage_duration
                soldier.rage = True
