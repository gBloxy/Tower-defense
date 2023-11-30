# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:00:18 2023

@author: gaspa
"""

import pygame
import random as rd

pygame.init()


def generate(x, y, depth, c):

    result = [[c, (x,y)]]
    for i in range(depth):
        x = result[0][-1][0] + rd.randrange(-20,20)
        y = result[0][-1][1] + rd.randrange(2,15)
        result[0].append((x, y))

        if rd.randrange(0,100) < 5:
            result.extend(generate(x, y, depth-i, c+i))

    return result

depth = rd.randrange(50, 80)
result = generate(400, 0, depth, 0)

screen = pygame.display.set_mode((800, 600))

screen.fill((0,0,0))

for line in result:
    depth = line[0]
    line = line[1:]
    for n, (point1, point2) in enumerate(zip(line, line[1:]), depth):
        c = 200-2*n
        # pygame.draw.aaline(screen, (c,c,c), point1, point2, 1)
        pygame.draw.line(screen, (c,c,c), point1, point2, 12-n//6)

pygame.display.flip()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()