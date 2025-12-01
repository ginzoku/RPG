# -*- coding: utf-8 -*-

MONSTER_ACTIONS = {
    "normal_attack": {
        "name": "攻撃",
        "type": "attack",
        "intent_type": "attack",
        "damage_type": "physical",
        "power": 1.0,  # モンスターの基本攻撃力に対する倍率
        "message": "{monster_name}の{action_name}！"
    },
    "strong_attack": {
        "name": "強攻撃",
        "type": "attack",
        "intent_type": "attack",
        "damage_type": "physical",
        "power": 1.5,
        "message": "{monster_name}の{action_name}！"
    },
    "debilitating_strike": {
        "name": "衰弱攻撃",
        "type": "attack_debuff",
        "intent_type": "attack_debuff",
        "damage_type": "physical",
        "power": 0.8, # 攻撃倍率
        "effect": "weak", # 状態異常ID
        "effect_power": 1, # 1ターン付与
        "message": "{monster_name}の{action_name}！"
    },
    "fire_spell": {
        "name": "炎の呪文",
        "type": "attack",
        "intent_type": "attack",
        "damage_type": "magical",
        "power": 15, # 固定ダメージ
        "message": "{monster_name}は{action_name}を唱えた！"
    },
    "wait": {
        "name": "様子を見る",
        "type": "wait",
        "intent_type": "unknown",
        "message": "{monster_name}は様子を見ている..."
    }
}