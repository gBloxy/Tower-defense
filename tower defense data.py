# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 10:35:42 2023

@author: gaspardcasamento
"""

init gold 140
init life 3

BaseTower

    cost :     100 gld
    dmg :      20  pv
    firerate : 2   s
    range :    120 px
    bullet :   BaseBullet
    bullet speed : 4
    
    upgrade  120 gld :
        dmg : 30
    
    upgrade2 150 gld :
        dmg :   50
    
    upgrade3 ... gld :
        bullet : SlowBullet
    
    upgrade4 ... gld:
        firerate : 4000 s
        dmg : 1 pv
        bullet : RayBullet
        update : RayUpdate

ExplosiveTower

    cost :     120 gld
    dmg :      50  pv
    firerate : 4   s
    range :    100 px
    explosion radius : 50 px
    bullet speed : 3
    
    upgrade 160 gld :
        dmg : 90 pv
        explosion radius : 60 px
    
    upgrade2 200 gld :
        dmg : 120 pv
        explosion radius : 70 px
    
    upgrade3 ... gld :
        firerate : 5000 s
        dmg : 200 pv
        explosion radius : 100 px
        invisible bullets
    
    upgrade4 ... gld :
        firerate : 1000 s
        dmg : 35 pv
        range 160 px
        explosion radius : 160 px

RapidFireTower

    cost :     100 gld
    dmg :      8  pv
    firerate : 1   s
    range :    160 px
    bullet :   BaseBullet
    bullet speed : 5
    
    upgrade  120 gld :
        dmg : 10 pv
    
    upgrade2 150 gld :
        dmg : 15 pv
    
    upgrade3 ... gld :
        range :    140 px
        dmg :      20  pv
        firerate : 0.5 s
    
    upgrade4 ... gld :
        range :    240 px
        dmg :      80  pv
        firerate : 2.5 s
        bullet speed : 8

SoldierTower

    cost :     100 gld
    range :    120 px
    respawn : 8000 s
    number : 2 soldiers
    soldier :
        velocity 1 px
        dmg :  10 pv
        life : 60 pv
        attack rate : 1600
    
    upgrade 120 gld :
        dmg :  15 pv
        life : 80 pv
    
    upgrade2 150 gld :
        life : 100 pv
        attack rate : 1400 s
    
    upgrade3 ... gld :
        number : 4
    
    upgrade4 ... gld :
        range : 150 px
        life : 120
        attack rate : 800 s
        velocity : 2 px

Ennemies :
    velocity : 2 loop
    return : 30 gld
    life : 60 pv
