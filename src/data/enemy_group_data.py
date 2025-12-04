# -*- coding: utf-8 -*-
from ..config import settings

ENEMY_POSITIONS = {
    1: [(settings.SCREEN_WIDTH - 200, settings.SCREEN_HEIGHT // 2 - 100)],
    2: [(settings.SCREEN_WIDTH - 200, settings.SCREEN_HEIGHT // 2 - 100),
        (settings.SCREEN_WIDTH - 400, settings.SCREEN_HEIGHT // 2 - 100)],
    3: [(settings.SCREEN_WIDTH - 200, settings.SCREEN_HEIGHT // 2 - 100),
        (settings.SCREEN_WIDTH - 400, settings.SCREEN_HEIGHT // 2 - 100),
        (settings.SCREEN_WIDTH - 600, settings.SCREEN_HEIGHT // 2 - 100)],
}

ENEMY_GROUPS = {
    "two_slimes": [
        {"id": "slime", "pos_index": 0},
        {"id": "slime", "pos_index": 1},
    ],
    "goblin_and_slime": [
        {"id": "goblin", "pos_index": 0},
        {"id": "slime", "pos_index": 1},
    ],
    "goblin_duo": [
        {"id": "goblin", "pos_index": 0},
        {"id": "goblin", "pos_index": 1},
    ],
    "spider_duo": [
        {"id": "venom_spider", "pos_index": 0},
        {"id": "venom_spider", "pos_index": 1},
    ],
    "slime_trio": [
        {"id": "slime", "pos_index": 0},
        {"id": "slime", "pos_index": 1},
        {"id": "slime", "pos_index": 2},
    ],
    "shadow_eye_solo": [
        {"id": "shadow_eye", "pos_index": 0},
    ],
    "conversation_test_group": [
        {"id": "mysterious_being", "pos_index": 0},
    ]
}