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
    },
    "weak": {
        "name": "衰弱",
        "icon": "W",
        "type": "outgoing_damage_modifier",
        "value": 0.8,
        "color": settings.LIGHT_GRAY,
        "is_debuff": True,
    },
    "regeneration": {
        "name": "再生",
        "icon": "R",
        "type": "end_of_turn_heal",
        "value": 5,  # ターン終了時に5回復
        "color": settings.GREEN,
        "is_debuff": False,
    },
    "poison": {
        "name": "毒",
        "icon": "P",
        "type": "end_of_turn_damage",
        "value": 5,
        "color": settings.PURPLE,
        "is_debuff": True,
    }
}