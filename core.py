
WIN_SIZE = [600, 400]

TILE_SIZE = 40
BULLET_SIZE = TILE_SIZE//5
MOB_SIZE = TILE_SIZE//2.5 # 2
SOLDIER_SIZE = TILE_SIZE//3.5 # 3


_ = 0

ADJACENTS = [
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1)
]


game_over = False

click = False
right_click = False
mouse_pos = (0, 0)
keys = []
dt = 0


tile_paths = []
point_paths = []
paths = []

slots = []
spawns = []
flags = []

mobs = []
towers = []
bullets = []
crashed_bullets = []
soldiers = []
