
import pygame

import core as c
from colors import colors
from towers import Slot, BaseTower, ExplosiveTower, RapidFireTower, SoldierTower, LaserTower, build_tower, upgrade_tower
from functions import rgb, distance_point, is_rect_hovered, blit_center
import level


class UI():
    def __init__(self):
        self.fonts = {
            'life': pygame.font.SysFont('arial', 30),
            'gold': pygame.font.SysFont('arial', 30),
            'gold_msg': pygame.font.SysFont('arial', 24),
            'game_over': pygame.font.SysFont('impact', 80),
            'cost': pygame.font.SysFont('impact', 15)
            }
        self.gold_message = None
        self.gold_timer = 0
        self.gold_message_duration = 4000 # ms
        self.radius = 50
        self.relative_pos = [(0, -45), (45, 0), (0, 45), (-45, 0)]
        self.order_tower = [BaseTower, RapidFireTower, ExplosiveTower, SoldierTower]
        self.order_keys = [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]
        self.obj = None
        self.ui = {'textures': {}, 'current': []}
        self.hovered = None
        self.locked = False
        self.init_ui_elements()
        
    def init_ui_elements(self):
        # circle
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(circle, rgb('black', 50), (self.radius, self.radius), self.radius, 2)
        self.ui['textures']['circle'] = circle
        # backgrounds
        background = pygame.Surface((30, 30), pygame.SRCALPHA)
        background_hovered = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(background, rgb('black', 100), pygame.Rect(0, 0, 30, 30), border_radius=4)
        pygame.draw.rect(background_hovered, rgb('black', 40), pygame.Rect(0, 0, 30, 30), border_radius=4)
        self.ui['textures']['bkg'] = background
        self.ui['textures']['bkg_hovered'] = background_hovered
        
    def set_tower_ui(self, tower):
        if not self.locked and tower.level < tower.max_level:
            self.reset_ui()
            self.obj = tower
            if tower.level == 2:
                for i in range(2):
                    x, y = self.relative_pos[1 if i == 0 else 3]
                    pos = (tower.rect.centerx + x, tower.rect.centery + y)
                    rect = pygame.Rect(0, 0, 30, 30)
                    rect.center = pos
                    price = self.fonts['cost'].render(str(tower.upgrade_price[tower.level+i]), True, 'yellow')
                    color = colors['towers'][tower.__class__.__name__]['levels'][tower.level+1+i]
                    self.ui['current'].append([rect, self.ui['textures']['bkg'], price, color])
            else:
                x, y = self.relative_pos[0]
                pos = (tower.rect.centerx + x, tower.rect.centery + y)
                rect = pygame.Rect(0, 0, 30, 30)
                rect.center = pos
                price = self.fonts['cost'].render(str(tower.upgrade_price[tower.level]), True, 'yellow')
                color = colors['towers'][tower.__class__.__name__]['levels'][tower.level+1]
                self.ui['current'].append([rect, self.ui['textures']['bkg'], price, color])
        
    def set_slot_ui(self, slot):
        if not self.locked:
            self.reset_ui()
            self.obj = slot
            for i in range(4):
                x, y = self.relative_pos[i]
                pos = (slot.rect.centerx + x, slot.rect.centery + y)
                rect = pygame.Rect(0, 0, 30, 30)
                rect.center = pos
                tower = self.order_tower[i]
                price = self.fonts['cost'].render(str(self.order_tower[i].price), True, 'yellow')
                self.ui['current'].append([rect, self.ui['textures']['bkg'], price, colors['towers'][tower.__name__]['levels'][0]])
        
    def reset_ui(self):
        self.obj = None
        self.hovered = None
        self.locked = False
        self.ui['current'] = []
        
    def mouse_out(self):
        if distance_point(self.obj.rect.center, c.mouse_pos) > self.radius and self.hovered is None:
            return True
        else:
            return False
        
    def execute(self):
        if self.obj.__class__.__name__ == Slot.__name__:
            if build_tower(self.obj, self.order_tower[self.hovered]):
                self.set_message(self.order_tower[self.hovered].price)
                self.reset_ui()
        else:
            l = self.obj.level
            if upgrade_tower(self.obj, self.hovered+2):
                self.set_message(self.obj.upgrade_price[l])
                self.reset_ui()
    
    def select(self, index):
        self.ui['current'][index][1] = self.ui['textures']['bkg_hovered']
        if self.hovered is not None:
            self.ui['current'][self.hovered][1] = self.ui['textures']['bkg']
        self.hovered = index
        
    def update(self):
        # tower / slot ui update
        if self.obj is not None:
            # check for remove
            if self.mouse_out() and not self.locked:
                self.reset_ui()
            else:
                # lock system
                if c.right_click:
                    self.locked = not self.locked
                # button action
                if (c.keys[pygame.K_RETURN] or c.click) and self.hovered is not None:
                    self.execute()
                # check hovered button
                hovered = False
                for e in self.ui['current']:
                    index = self.ui['current'].index(e)
                    if is_rect_hovered(e[0]) or c.keys[self.order_keys[index]]:
                        hovered = True
                        if self.hovered != index:
                            self.select(index)
                # unselect when no button hovered
                if not hovered and self.hovered is not None:
                    self.ui['current'][self.hovered][1] = self.ui['textures']['bkg']
                    self.hovered = None
        # gold mesage update
        if self.gold_timer != 0:
            self.gold_timer += c.dt
            if self.gold_timer > self.gold_message_duration:
                self.reset_gold_message()
    
    def set_message(self, gold: int):
        self.gold_message = '-'+str(gold)
        self.gold_timer = 1
    
    def reset_gold_message(self):
        self.gold_timer = 0
        self.gold_message = None
        
    def render(self, surf):
        # render tower ui
        if self.obj is not None:
            blit_center(surf, self.ui['textures']['circle'], self.obj.rect.center)
            for e in self.ui['current']:
                surf.blit(e[1], e[0])
                pygame.draw.circle(surf, e[3], e[0].center, 12)
                blit_center(surf, e[2], (e[0].centerx, e[0].centery+12))
        
        # render life and gold
        surf.blit(self.fonts['life'].render(str(level.life), True, colors['UI']['life']), (8, 5))
        image = self.fonts['gold'].render(str(level.gold), True, colors['UI']['gold'])
        surf.blit(image, (c.WIN_SIZE[0] - image.get_width() - 12, 5))
        # render gold message
        if self.gold_timer != 0:
            image = self.fonts['gold_msg'].render(self.gold_message, True, colors['UI']['gold_msg'])
            surf.blit(image, (c.WIN_SIZE[0] - image.get_width() - 12, 35))
        # render game over indication
        if c.game_over:
            blit_center(surf, self.fonts['game_over'].render('GAME OVER', True, colors['UI']['over']), (c.WIN_SIZE[0]/2, c.WIN_SIZE[1]/2))
