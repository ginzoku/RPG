# -*- coding: utf-8 -*-
from ..config import settings

STATUS_EFFECTS = {
    "vulnerable": {
        "name": "無防備",
        "icon": "V",
        "type": "incoming_damage_modifier",
        "value": 1.5,
        "color": settings.ORANGE,
        "is_debuff": True,
        "description": "受けるダメージが1.5倍になる"
    },
    "weak": {
        "name": "衰弱",
        "icon": "W",
        "type": "outgoing_damage_modifier",
        "value": 0.8,
        "color": settings.LIGHT_GRAY,
        "is_debuff": True,
        "description": "与えるダメージが20%減少する"
    },
    "regeneration": {
        "name": "再生",
        "icon": "R",
        "type": "end_of_turn_heal",
        "value": 5,  # ターン終了時に5回復
        "color": settings.GREEN,
        "is_debuff": False,
        "description": "ターン終了時にHPが5回復する"
    },
    "poison": {
        "name": "毒",
        "icon": "P",
        "type": "end_of_turn_damage",
        "value": 5,
        "color": settings.PURPLE,
        "is_debuff": True,
        "description": "ターン終了時に5ダメージを受ける"
    },
    "barrier": {
        "name": "バリア",
        "icon": "B",
        "type": "defense_buff",
        "value": 10,
        "color": settings.CYAN,
        "is_debuff": False,
        "turns": -1,
        "removal_condition": "on_damage_taken",
        "description": "防御力を10得る。ダメージを受けると解除される。"
    },
    "focus": {
        "name": "集中",
        "icon": "F",
        "type": "outgoing_damage_modifier",
        "value": 2.0,
        "color": settings.LIGHT_BLUE,
        "is_debuff": False,
        "turns": -1,
        "removal_condition": "on_debuff_received",
        "description": "与えるダメージが2倍になる。デバフ効果を受けると解除される。"
    }
}