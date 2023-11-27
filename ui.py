
import pygame

import core as c
from colors import colors
from towers import BaseTower, ExplosiveTower, RapidFireTower, SoldierTower
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
        self.ui_order = [BaseTower, RapidFireTower, ExplosiveTower, SoldierTower]
        self.obj = None
        # self.elements = {}
        # self.current_elements = []
        # self.pos = []
        self.ui = {'textures': {}}
        self.hovered = None
        self.init_ui_elements()
        
    def init_ui_elements(self):
        # circle
        circle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(circle, rgb('black', 50), (self.radius, self.radius), self.radius, 2)
        self.ui['textures']['circle'] = circle
        # backgrounds
        self.background = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.background_hovered = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.background, rgb('black', 100), pygame.Rect(0, 0, 30, 30), border_radius=4)
        pygame.draw.rect(self.background_hovered, rgb('gray', 100), pygame.Rect(0, 0, 30, 30), border_radius=4)
        # slot elements
        self.elements['slot'] = []
        for i in range(4):
            self.elements['slot'].append({})
            obj = self.ui_order[i]
            bkg = self.background.copy()
            bkg_hovered = self.background_hovered.copy()
            pygame.draw.circle(bkg, colors['towers'][obj.__name__]['levels'][0],
                               (bkg.get_width()/2, bkg.get_height()/2), bkg.get_width()/2-2)
            pygame.draw.circle(bkg_hovered, colors['towers'][obj.__name__]['levels'][0],
                               (bkg.get_width()/2, bkg.get_height()/2), bkg.get_width()/2-2)
            self.elements['slot'][i]['normal']  = bkg
            self.elements['slot'][i]['hovered'] = bkg_hovered
            self.elements['slot'][i]['price']   = self.fonts['cost'].render(str(obj.price), True, 'yellow')
        
    def set_tower_ui(self, tower):
        self.reset_ui()
        self.obj = tower
        
    def set_slot_ui(self, slot):
        self.reset_ui()
        self.obj = slot
        for i in range(4):
            x, y = self.relative_pos[i]
            pos = (slot.rect.centerx + x, slot.rect.centery + y)
            self.current_elements.append((self.elements['slot'][i]['normal'], pos))
            self.current_elements.append((self.elements['slot'][i]['price'], (pos[0], pos[1]+12)))
            rect = pygame.Rect(0, 0, 30, 30)
            rect.center = pos
            self.pos.append(rect)
        
    def reset_ui(self):
        self.obj = None
        self.current_elements = []
        
    def update(self):
        if self.obj is not None:
            if distance_point(self.obj.rect.center, c.mouse_pos) > self.radius+5:
                self.reset_ui()
            else:
                for rect in self.pos:
                    if is_rect_hovered(rect):
                        ...
        
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
            blit_center(surf, self.circle, self.obj.rect.center)
            for e in self.current_elements:
                blit_center(surf, e[0], e[1])
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
