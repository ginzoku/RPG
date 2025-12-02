# -*- coding: utf-8 -*-
from ..config import settings

STATUS_EFFECTS = {
    "vulnerable": {
        "name": "無防備",
        "icon": "🛡️",
        "description": "受けるダメージが50%増加する。",
        "type": "incoming_damage_modifier",
        "value": 1.5,
        "color": settings.ORANGE,
        "is_debuff": True,
    },
    "weak": {
        "name": "衰弱",
        "icon": "⚔️",
        "description": "与えるダメージが20%減少する。",
        "type": "outgoing_damage_modifier",
        "value": 0.8,
        "color": settings.LIGHT_GRAY,
        "is_debuff": True,
    },
    "regeneration": {
        "name": "再生",
        "icon": "❤️",
        "description": "ターン終了時にHPが5回復する。",
        "type": "end_of_turn_heal",
        "value": 5,  # ターン終了時に5回復
        "color": settings.GREEN,
        "is_debuff": False,
    },
    "poison": {
        "name": "毒",
        "icon": "☠️",
        "description": "ターン開始時にスタック分のダメージを受ける。ターン終了時にスタックが1減少する。",
        "type": "start_of_turn_damage",
        "value": 1, # 1スタックあたりのダメージ
        "color": (128, 0, 128), # 紫
        "is_debuff": True,
    }
}