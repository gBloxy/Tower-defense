
import core as c
from functions import interpolate_points
import level
from towers import Slot


def init_map():
    c.slots, c.spawns, c.flags = Parse(level.Map)
    for path in level._paths:
        tiles, points, line = Path(*path)
        c.tile_paths.append(tiles)
        c.point_paths.append(points)
        c.paths.append(line)


def load_map(map_name):
    Map = []
    y = 0
    with open('levels\\'+map_name) as file:
        for row in file.readlines():
            Map.append([])
            for tile in row:
                if tile != '\n':
                    if tile == '_':
                        Map[y].append(c._)
                    else:
                        Map[y].append(int(tile))
            y += 1
    return Map


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
            tile = level.Map[pos[1]][pos[0]]
            if tile == 1 and pos != current and not pos in tile_path and not list(pos) in blacklist:
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
