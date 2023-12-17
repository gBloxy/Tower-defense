
import pygame
pygame.font.init()

import core as c
from functions import close, blit_center
from ui import Button, ScrollArea
from level import get_levels, load_level


class MainMenu():
    def __init__(self):
        font = pygame.font.SysFont('arial', 60)
        self.title = font.render('Tower Defense', True, 'black')
        self.play_button = Button(
            x=c.WIN_SIZE[0]/2, y=175,
            text='Play',
            font=pygame.font.SysFont('impact', 50)
            )
    
    def update(self):
        global current_menu
        if self.play_button.update():
            current_menu = LevelsMenu()
        
    def render(self, win):
        blit_center(win, self.title, (c.WIN_SIZE[0]//2, 50))
        self.play_button.render(win)


class LevelsMenu():
    def __init__(self):
        self.previous_button = Button(
            x=80, y=c.WIN_SIZE[1]-50,
            text='Previous',
            font=pygame.font.SysFont('impact', 30)
            )
        self.levels_buttons = {}
        self.scroll_area = ScrollArea()
        last = None
        for level, data in get_levels():
            button = Button(
                x=c.WIN_SIZE[0]/2, y=150,
                text=data['name'],
                font=pygame.font.SysFont('impact', 30)
                )
            if last is not None:
                button.rect.left = last.rect.right + 30
            self.levels_buttons[level] = button
            self.scroll_area.add_element(button)
            last = button
        scroll = (self.scroll_area.get_element(0).rect.x - self.scroll_area.get_element(-1).rect.x) / 2
        self.scroll_area.set_scroll_value(scroll)
        
    def update(self):
        global current_menu
        if self.previous_button.update():
            current_menu = MainMenu()
        self.scroll_area.update()
        for button in self.levels_buttons:
            if self.levels_buttons[button].update():
                load_level(button)
                return True
        
    def render(self, win):
        self.previous_button.render(win)
        for button in self.levels_buttons.values():
            if button.rect.right >= 0 and button.rect.left <= c.WIN_SIZE[0]:
                button.render(win)


current_menu = MainMenu()


def run_menu(win: pygame.Surface, clock):
    while True:
        c.dt = clock.tick(30)
        events = pygame.event.get()
        c.click = False
        c.scrolling = 0
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    c.click = True
                elif e.button == 4:
                    c.scrolling = 1 # up
                elif e.button == 5:
                    c.scrolling = -1 # down
            elif e.type == pygame.QUIT:
                close()
        c.keys = pygame.key.get_pressed()
        if c.keys[pygame.K_ESCAPE]:
            close()
        c.mouse_pos = pygame.mouse.get_pos()
        win.fill('white')
        
        if current_menu.update():
            return True
        
        current_menu.render(win)
        
        pygame.display.flip()
