
from core import _


DEV_MOD = 0
DEBUG_MOD = 0


gold = 100000 if DEV_MOD else 140
life = 100 if DEV_MOD else 3


Map = [ # 15 cols 10 rows
    [_, _, _, 2, _, 4, _, 4, _, 4, _, 4, _, _, _],
    [_, 4, _, 1, _, _, _, _, _, _, _, _, _, _, _],
    [_, 4, _, 1, 1, 1, 1, 1, 1, 1, 1, 1, _, 4, _],
    [_, _, _, _, _, _, _, _, _, _, _, 1, _, _, _],
    [2, 1, 1, 1, _, 4, _, 4, _, 4, _, 1, _, 4, _],
    [_, _, _, 1, _, _, _, _, _, _, _, 1, _, _, _],
    [_, 4, _, 1, 1, 1, 1, 1, 1, 1, 1, 1, _, 4, _],
    [_, _, _, _, _, _, _, _, _, 1, _, _, _, _, _],
    [_, _, _, 4, _, 4, _, 4, _, 1, _, 4, _, _, _],
    [_, _, _, _, _, _, _, _, _, 3, _, _, _, _, _]
]


_paths = [(0, 0, [(8, 6)]), (1, 0, [(10, 6)])]


# wave_configuration = [
#     [
#      {'enemy': GoblinMob, 'quantity': 3, 'time': 5500, 'initial': 2500, 'path': 0},
#      {'enemy': GoblinMob, 'quantity': 2, 'time': 5500, 'initial': 4000, 'path': 1}
#      ],
#     [
#      {'enemy': GoblinMob, 'quantity': 8, 'time': 4500 , 'initial': 2500},
#      {'enemy': GoblinMob, 'quantity': 8, 'time': 4500 , 'initial': 2500},
#      {'enemy': OrcMob,    'quantity': 3, 'time': 10000, 'initial': 4500}
#      ]
# ]
