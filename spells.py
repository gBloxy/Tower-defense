
from math import pi, sqrt, cos, sin
from random import uniform
from types import SimpleNamespace

import core as c
from colors import colors
from bullets import ExplosiveBullet


def FireSpell(radius, explosion_radius, damage, number):
    for i in range(number):
        angle = uniform(0, 2 * pi)
        r = radius * sqrt(uniform(0, 1))
        pos = (c.mouse_pos[0] + r * cos(angle), c.mouse_pos[1] + r * sin(angle))
        bullet = ExplosiveBullet(*pos, SimpleNamespace(targeted=[]), damage, explosion_radius, None, *colors['explosion'][0].values())
        bullet.explode()
        c.bullets.append(bullet)
