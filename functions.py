
import pygame
from sys import exit
from math import sqrt

import core as c


def close():
    pygame.quit()
    exit()


def rgb(color_name: str, alpha: int = 255):
    color = pygame.Color(color_name)
    return [color.r, color.g, color.b, alpha]


def blit_center(surface, image, pos):
    surface.blit(image, (pos[0] - image.get_width()//2, pos[1] - image.get_height()//2))


def blit_transparent_circle(surface, color, alpha, center, radius, width=0):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, rgb(color, alpha), (radius, radius), radius, width)
    surface.blit(surf, (center[0] - radius, center[1] - radius))


def concatenate(*lists):
    all_values = []
    for l in lists:
        all_values += l
    return list(set(all_values))


def lerp(a, b, t):
    return a + t * (b - a)


def distance(tower, mob):
    return sqrt((mob.rect.centerx - tower.rect.centerx)**2 + (mob.rect.centery - tower.rect.centery)**2)


def distance_point(pos1, pos2):
    return sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def interpolate_points(point1, point2, num_points):
    interpolated_points = []
    for i in range(num_points + 1):
        t = i / num_points
        x_t = lerp(point1[0], point2[0], t)
        y_t = lerp(point1[1], point2[1], t)
        interpolated_points.append((int(x_t), int(y_t)))
    return interpolated_points


def is_hovered(entity):
    if entity.rect.collidepoint(*c.mouse_pos):
        return True
    else:
        return False


def is_rect_hovered(rect):
    if rect.collidepoint(*c.mouse_pos):
        return True
    else:
        return False


def is_clicked(entity):
    if c.click and entity.rect.collidepoint(*c.mouse_pos):
        return True
    else:
        return False


def collision_list(entity, collideables):
    hit_list = []
    for e in collideables:
        if e.rect.colliderect(entity.rect):
            hit_list.append(e)
    return hit_list
