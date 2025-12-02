# -*- coding: utf-8 -*-

MONSTERS = {
    "goblin": {
        "name": "ゴブリン",
        "max_hp": 20,
        "attack_power": 5,
        "actions": ["goblin_attack"]
    },
    "slime": {
        "name": "スライム",
        "max_hp": 15,
        "attack_power": 3,
        "actions": ["slime_tackle"]
    },
    "poison_slime": {
        "name": "ポイズンスライム",
        "max_hp": 22,
        "attack_power": 2,
        "actions": ["poison_splash"]
    },
    "specter": {
        "name": "亡霊",
        "max_hp": 25,
        "attack_power": 0, # 物理攻撃はしない
        "actions": ["mind_crush"]
    }
}