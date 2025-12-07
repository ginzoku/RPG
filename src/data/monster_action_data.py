# -*- coding: utf-8 -*-

MONSTER_ACTIONS = {
    "normal_attack": {
        "name": "攻撃",
        "intent_type": "attack",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 8, "hits": 1}
        ]
    },
    "strong_attack": {
        "name": "強攻撃",
        "intent_type": "attack",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 12, "hits": 1}
        ]
    },
    "debilitating_strike": {
        "name": "衰弱攻撃",
        "intent_type": "attack_debuff",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 7, "hits": 1},
            {"type": "apply_status", "target_scope": "single", "status_id": "weak", "turns": 1}
        ]
    },
    "poison_bite": {
        "name": "毒咬",
        "intent_type": "attack_debuff",
        "message": "{monster_name}の{action_name}！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 6, "hits": 1},
            {"type": "apply_status", "target_scope": "single", "status_id": "poison", "turns": 3}
        ]
    },
    "fire_spell": {
        "name": "炎の呪文",
        "intent_type": "attack",
        "message": "{monster_name}は{action_name}を唱えた！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 15, "hits": 1}
        ]
    },
    "wait": {
        "name": "様子を見る",
        "intent_type": "unknown",
        "message": "{monster_name}は様子を見ている...",
        "effects": [{"type": "pass"}]
    },
    "self_heal": {
        "name": "自己再生",
        "intent_type": "buff",
        "message": "{monster_name}は傷を再生した！",
        "effects": [
            {"type": "heal", "target_scope": "self", "power": 10}
        ]
    },
    "mind_crush": {
        "name": "精神攻撃",
        "intent_type": "sanity_attack", # 正気度攻撃用のインテントタイプ
        "message": "{monster_name}の{action_name}！不気味な視線が精神を蝕む...！",
        "effects": [
            {"type": "sanity_damage", "target_scope": "single", "power": 10, "hits": 1}
        ]
    },
    "rampage": {
        "name": "暴れまわる",
        "intent_type": "attack",
        "message": "{monster_name}は暴れまわっている！",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 4, "hits": 3}
        ]
    },
    "earthquake": {
        "name": "地震",
        "intent_type": "attack",
        "message": "{monster_name}が地面を揺らした！",
        "effects": [
            {"type": "damage", "target_scope": "all", "power": 8, "hits": 1}
        ]
    },
    "trigger_conversation": {
        "name": "奇妙なうめき声",
        "intent_type": "conversation",
        "message": "{monster_name}は奇妙なうめき声をあげている...",
        "effects": [
            {"type": "conversation_event", "conversation_id": "monster_battle_intro_conversation"}
        ]
    }
}