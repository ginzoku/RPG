# -*- coding: utf-8 -*-

MONSTER_ACTIONS = {
    "normal_attack": {
        "name": "攻撃",
        "intent_type": "attack",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target": "player", "damage_type": "physical", "power": 1.0}
        ]
    },
    "strong_attack": {
        "name": "強攻撃",
        "intent_type": "attack",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target": "player", "damage_type": "physical", "power": 1.5}
        ]
    },
    "debilitating_strike": {
        "name": "衰弱攻撃",
        "intent_type": "attack_debuff",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target": "player", "damage_type": "physical", "power": 0.8},
            {"type": "apply_status", "target": "player", "status_id": "weak", "turns": 1}
        ]
    },
    "poison_bite": {
        "name": "毒咬",
        "intent_type": "attack_debuff",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target": "player", "damage_type": "physical", "power": 0.7},
            {"type": "apply_status", "target": "player", "status_id": "poison", "turns": 3}
        ]
    },
    "fire_spell": {
        "name": "炎の呪文",
        "intent_type": "attack",
        "message": "{monster_name}は{action_name}を唱えた！",
        "effects": [
            {"type": "damage", "target": "player", "damage_type": "magical", "power": 15}
        ]
    },
    "wait": {
        "name": "様子を見る",
        "intent_type": "unknown",
        "message": "{monster_name}は様子を見ている...",
        "effects": []
    },
    "mind_crush": {
        "name": "精神攻撃",
        "intent_type": "sanity_attack", # 正気度攻撃用のインテントタイプ
        "message": "{monster_name}の{action_name}！不気味な視線が精神を蝕む...！",
        "effects": [
            {"type": "sanity_damage", "target": "player", "power": 10}
        ]
    }
}