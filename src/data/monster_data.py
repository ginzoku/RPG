# -*- coding: utf-8 -*-

MONSTERS = {
    "slime": {
        "name": "スライム",
        "max_hp": 30,
        "max_mp": 0,
        "attack_power": 8,
        "actions": ["normal_attack", "normal_attack", "wait"]
    },
    "goblin": {
        "name": "ゴブリン",
        "max_hp": 50,
        "attack_power": 12,
        "actions": ["normal_attack", "strong_attack", "debilitating_strike"]
    },
    "mage": {
        "name": "魔法使い",
        "max_hp": 40,
        "attack_power": 5,
        "actions": ["normal_attack", "fire_spell"]
    },
    "shadow_eye": {
        "name": "シャドウアイ",
        "max_hp": 60,
        "attack_power": 10,
        "actions": ["normal_attack", "mind_crush", "mind_crush"]
    }
}