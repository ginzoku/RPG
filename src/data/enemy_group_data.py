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
    "two_slimes": {
        "enemies": [
            {"id": "slime", "pos_index": 0},
            {"id": "slime", "pos_index": 1},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "goblin_and_slime": {
        "enemies": [
            {"id": "goblin", "pos_index": 0},
            {"id": "slime", "pos_index": 1},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "goblin_duo": {
        "enemies": [
            {"id": "goblin", "pos_index": 0},
            {"id": "goblin", "pos_index": 1},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "spider_duo": {
        "enemies": [
            {"id": "venom_spider", "pos_index": 0},
            {"id": "venom_spider", "pos_index": 1},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "slime_trio": {
        "enemies": [
            {"id": "slime", "pos_index": 0},
            {"id": "slime", "pos_index": 1},
            {"id": "slime", "pos_index": 2},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "shadow_eye_solo": {
        "enemies": [
            {"id": "shadow_eye", "pos_index": 0},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    },
    "conversation_test_group": {
        "enemies": [
            {"id": "mysterious_being", "pos_index": 0},
            {"id": "mysterious_being", "pos_index": 1},
        ],
        "background": "assets/backgrounds/forest_battle.png"
    }
}