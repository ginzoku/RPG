# -*- coding: utf-8 -*-

MONSTER_ACTIONS = {
    "goblin_attack": {
        "name": "殴りかかる",
        "message": "{monster_name}の「{action_name}」！",
        "type": "attack",
        "power": 1.0,
        "intent_type": "attack",
    },
    "slime_tackle": {
        "name": "体当たり",
        "message": "{monster_name}の「{action_name}」！",
        "type": "attack",
        "power": 0.8,
        "intent_type": "attack",
    },
    "poison_splash": {
        "name": "毒液",
        "message": "{monster_name}は「{action_name}」を放った！",
        "type": "attack_debuff",
        "power": 0.5, # 攻撃力は低い
        "intent_type": "attack_debuff",
        "effects": [
            {"type": "apply_status", "status_id": "poison", "turns": 3}
        ]
    },
    "mind_crush": {
        "name": "精神破壊",
        "message": "{monster_name}は「{action_name}」を唱えた！",
        "type": "debuff",
        "intent_type": "debuff",
        "effects": [
            {"type": "sanity_damage", "value": 10}
        ]
    }
}