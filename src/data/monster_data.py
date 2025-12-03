# -*- coding: utf-8 -*-

MONSTERS = {
    "slime": {
        "name": "スライム",
        "max_hp": 30,
        "max_mp": 0,
        "attack_power": 0,
        "actions": ["normal_attack", "normal_attack", "wait"],
        "gold": 5
    },
    "goblin": {
        "name": "ゴブリン",
        "max_hp": 50,
        "attack_power": 0,
        "actions": ["normal_attack", "strong_attack", "debilitating_strike"],
        "gold": 10
    },
    "venom_spider": {
        "name": "ヴェノムスパイダー",
        "max_hp": 45,
        "attack_power": 0,
        "actions": ["normal_attack", "poison_bite"],
        "gold": 12
    },
    "mage": {
        "name": "魔法使い",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["normal_attack", "fire_spell"],
        "gold": 15
    },
    "shadow_eye": {
        "name": "シャドウアイ",
        "max_hp": 60,
        "attack_power": 0,
        "actions": ["normal_attack", "mind_crush", "mind_crush"],
        "gold": 20
    }
}