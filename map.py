
from math import sin

import core as c
from functions import interpolate_points
from level import _paths, Map
from towers import Slot
from grass import GrassManager


wind_rotation_func = lambda x, y: int(sin(c.wt / 60 + x / 100) * 15)


def init_map():
    c.slots, c.spawns, c.flags = Parse(Map)
    for path in _paths:
        tiles, points, line = Path(*path)
        c.tile_paths.append(tiles)
        c.point_paths.append(points)
        c.paths.append(line)
    grass_manager = GrassManager('grass\\', c.TILE_SIZE, place_range=[0, 1])
    grass_manager.enable_ground_shadows(shadow_radius=4, shadow_color=(0, 0, 1), shadow_shift=(1, 2))
    place_grass(grass_manager)
    return grass_manager


def place_grass(grass_manager):
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            if tile == c._:
                grass_manager.place_tile((x, y), 50, [0, 1, 2, 3, 4, 5, 0, 1, 2, 3])


def Parse(MAP):
    slots, spawns, flags = [], [], []
    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            if tile == 4:
                slots.append(Slot(x, y))
            elif tile == 2:
                spawns.append((x, y))
            elif tile == 3:
                flags.append((x, y))
    return slots, spawns, flags


def Path(spawn, flag, blacklist):
    tile_path, point_path, path = [], [], []
    # find the tile path position
    current = c.spawns[spawn]
    while current != c.flags[flag]:
        for (x, y) in c.ADJACENTS:
            pos = (current[0]+x, current[1]+y)
            tile = Map[pos[1]][pos[0]]
            if tile == 1 and pos != current and not pos in tile_path and not pos in blacklist:
                tile_path.append(current)
                current = pos
                break
            elif tile == 3:
                tile_path.append(current)
                current = pos
                tile_path.append(current)
                break
    # convert it to pixel points path
    for pos in tile_path:
        point_path.append((pos[0]*c.TILE_SIZE + c.TILE_SIZE//2, pos[1]*c.TILE_SIZE + c.TILE_SIZE//2))
    # connect it to linear pixel path
    for i in range(len(point_path) - 1):
        path.extend(interpolate_points(point_path[i], point_path[i+1], 90))
    return tile_path, point_path, path
