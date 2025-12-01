# -*- coding: utf-8 -*-
from ..config import settings

RELICS = {
    "red_stone": {
        "name": "赤い石",
        "description": "攻撃力が1上昇する。",
        "color": settings.RED,
        "effects": [
            {"type": "stat_change", "stat": "attack_power", "value": 1}
        ]
    }
}