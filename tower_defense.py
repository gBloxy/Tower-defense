
import pygame
pygame.init()

import core as c
from core import TILE_SIZE, WIN_SIZE
from functions import close, is_hovered, is_clicked
from map import init_map
from colors import colors
import level
from towers import BaseTower, ExplosiveTower, RapidFireTower, SoldierTower, render_tower_range
from entities import GoblinMob, render_mob_header
from spells import FireSpell
from ui import UI


window = pygame.display.set_mode(WIN_SIZE)
clock = pygame.time.Clock()


spawn_frequency = 5500 # ms
max_spawn_frequency = 1400 # ms
timer = 0
spell_timer = 0
gld_msg_timer = 0


# GAMELOOP --------------------------------------------------------------------

try:
    ui = UI()
    init_map()
    while True:
        c.dt = clock.tick(30)
        events = pygame.event.get()
        c.click = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                c.click = True
            elif e.type == pygame.QUIT:
                close()
        c.keys = pygame.key.get_pressed()
        if c.keys[pygame.K_ESCAPE]:
            close()
        c.mouse_pos = pygame.mouse.get_pos()
        window.fill('white')
        
        # DEV MOD tools
        if level.DEV_MOD:
            for mob in c.mobs:
                if is_clicked(mob):
                    mob.remove()
            if c.keys[pygame.K_RIGHT]:
                for p in c.paths:
                    c.mobs.append(GoblinMob(*c.spawns[0], p))
                pygame.time.wait(200)
            if c.keys[pygame.K_UP]:
                spawn_frequency -= 120
            if c.keys[pygame.K_DOWN]:
                spawn_frequency += 120
            if c.keys[pygame.K_LEFT]:
                print(clock.get_fps())
        
        # spawn new mob
        if not c.game_over:
            timer += c.dt
            if timer > spawn_frequency:
                timer = 0
                if spawn_frequency > max_spawn_frequency:
                    spawn_frequency -= 120
                    if spawn_frequency < max_spawn_frequency:
                        spawn_frequency == max_spawn_frequency
                c.mobs.append(GoblinMob(*c.spawns[0], c.paths[0]))
                c.mobs.append(GoblinMob(*c.spawns[0], c.paths[1]))
        
        # render map
        for y, row in enumerate(level.Map):
            for x, tile in enumerate(row):
                pygame.draw.rect(window, colors['map'][tile], pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # update slots
        for slot in c.slots:
            pygame.draw.circle(window, colors['slots']['normal'], slot.rect.center, TILE_SIZE//2)
            if not c.game_over and is_hovered(slot):
                if slot != ui.obj:
                    ui.set_slot_ui(slot)
                pygame.draw.circle(window, colors['slots']['hovered'], slot.rect.center, TILE_SIZE//2)
                if c.keys[pygame.K_1]:
                    if level.gold >= BaseTower.price:
                        level.gold -= BaseTower.price
                        ui.set_message(BaseTower.price)
                        c.slots.remove(slot)
                        c.towers.append(BaseTower(slot.x, slot.y))
                elif c.keys[pygame.K_2]:
                    if level.gold >= ExplosiveTower.price:
                        level.gold -= ExplosiveTower.price
                        ui.set_message(ExplosiveTower.price)
                        c.slots.remove(slot)
                        c.towers.append(ExplosiveTower(slot.x, slot.y))
                elif c.keys[pygame.K_3]:
                    if level.gold >= RapidFireTower.price:
                        level.gold -= RapidFireTower.price
                        ui.set_message(RapidFireTower.price)
                        c.slots.remove(slot)
                        c.towers.append(RapidFireTower(slot.x, slot.y))
                elif c.keys[pygame.K_4]:
                    if level.gold >= SoldierTower.price:
                        level.gold -= SoldierTower.price
                        ui.set_message(SoldierTower.price)
                        c.slots.remove(slot)
                        c.towers.append(SoldierTower(slot.x, slot.y))
        
        # update and render towers
        for tower in c.towers:
            pygame.draw.circle(window, tower.color, tower.rect.center, tower.rect.width/2)
            if not c.game_over:
                if is_clicked(tower):
                    if tower.level < 2:
                        if level.gold >= tower.upgrade_price[tower.level]:
                            level.gold -= tower.upgrade_price[tower.level]
                            ui.set_message(tower.upgrade_price[tower.level])
                            tower.upgrade()
                if is_hovered(tower):
                    if ui.obj != tower:
                        ui.set_tower_ui(tower)
                    if tower.level == 2:
                        if c.keys[pygame.K_1]:
                            if level.gold >= tower.upgrade_price[2]:
                                level.gold -= tower.upgrade_price[2]
                                ui.set_message(tower.upgrade_price[2])
                                tower.upgrade(3)
                        elif c.keys[pygame.K_2]:
                            if level.gold >= tower.upgrade_price[3]:
                                level.gold -= tower.upgrade_price[3]
                                ui.set_message(tower.upgrade_price[3])
                                tower.upgrade(4)
                    pygame.draw.circle(window, tower.hovered_color, tower.rect.center, tower.rect.width/2)
                    render_tower_range(window, tower)
                tower.update()
            if level.DEBUG_MOD and tower.target is not None:
                pygame.draw.line(window, colors['debug'], tower.rect.center, tower.target.rect.center, 2)
        
        # render crashed c.bullets
        for bullet in c.crashed_bullets:
            bullet.timer -= c.dt
            if bullet.timer <= 0:
                c.crashed_bullets.remove(bullet)
            else:
                pygame.draw.circle(window, colors['bullets']['crashed'], bullet.rect.center, bullet.rect.width/2)
        
        # spell
        if spell_timer != 0:
            spell_timer += c.dt
            if spell_timer >= 2000:
                spell_timer = 0
        elif c.keys[pygame.K_SPACE]:
            FireSpell(radius=45, explosion_radius=40, damage=100, number=4)
            spell_timer = 1
        
        # update and render bullets
        for bullet in c.bullets:
            if not c.game_over:
                bullet.update()
            bullet.render(window)
        
        # update and render c.mobs
        for mob in c.mobs:
            if not c.game_over:
                if not mob.update():
                    mob.remove()
                    level.life -= 1
                    # life checking
                    if level.life == 0:
                        c.game_over = True
            pygame.draw.circle(window, colors['mobs'], mob.rect.center, mob.rect.width/2)
            render_mob_header(window, mob)
        
        # render soldier
        for soldier in c.soldiers:
            if is_hovered(soldier.tower) and soldier == soldier.tower.selected_soldier:
                pygame.draw.rect(window, colors['soldier']['selected'], soldier.rect)
            else:
                pygame.draw.rect(window, soldier.color, soldier.rect)
            render_mob_header(window, soldier, header_size=35)
        
        ui.update()
        ui.render(window)
        pygame.display.flip()

except Exception as exc:
    pygame.quit()
    raise exc
