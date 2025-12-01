# -*- coding: utf-8 -*-
from ..config import settings

STATUS_EFFECTS = {
    "vulnerable": {
        "name": "無防備",
        "type": "incoming_damage_modifier",
        "value": 1.5,
        "color": settings.ORANGE,
        "is_debuff": True,
    },
    "weak": {
        "name": "衰弱",
        "type": "outgoing_damage_modifier",
        "value": 0.8,
        "color": settings.LIGHT_GRAY,
        "is_debuff": True,
    },
    "regeneration": {
        "name": "再生",
        "type": "end_of_turn_heal",
        "value": 5,  # ターン終了時に5回復
        "color": settings.GREEN,
        "is_debuff": False,
    }
}