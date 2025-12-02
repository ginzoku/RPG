# -*- coding: utf-8 -*-

ENEMY_GROUPS = {
    "goblin_duo": [
        {"id": "goblin", "pos_index": 0},
        {"id": "goblin", "pos_index": 1},
    ],
    "slime_trio": [
        {"id": "slime", "pos_index": 0},
        {"id": "slime", "pos_index": 1},
        {"id": "slime", "pos_index": 2},
    ],
    "poison_slime_single": [
        {"id": "poison_slime", "pos_index": 0},
    ]
}

ENEMY_POSITIONS = {
    1: [(600, 250)],
    2: [(550, 250), (700, 250)],
    3: [(500, 250), (650, 250), (800, 250)],
}