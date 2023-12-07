
from json import load
from os import listdir


DEV_MOD = 1
DEBUG_MOD = 0


Map = [[]]
_paths = []


def load_level(level_name):
    from map import load_map
    global Map, _paths, gold, life
    with open('levels\\'+level_name) as file:
        data = load(file)
        _paths = data['paths']
        gold = data['gold'] if not DEV_MOD else 100000
        life = data['life'] if not DEV_MOD else 100
        Map = load_map(data['map'])


def get_levels():
    levels = []
    for file_name in listdir('levels\\'):
        if file_name.startswith('level'):
            with open('levels\\'+file_name) as file:
                data = load(file)
            levels.append((file_name, data))
    return levels
