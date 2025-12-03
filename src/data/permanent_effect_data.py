# -*- coding: utf-8 -*-
from ..config import settings

PERMANENT_EFFECTS = {
    "blood_pact": {
        "name": "血の契約",
        "icon": "🩸",
        "type": "end_of_turn_direct_damage",
        "value": 10,
        "color": settings.RED,
        "description": "ターン終了時に10のHPを失う（防御不可）。"
    }
}