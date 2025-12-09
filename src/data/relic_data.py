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
    },
    "cursed_armor": {
        "name": "呪われた鎧",
        "description": "ターン開始時に5ダメージを受ける。ターン終了時に10の防御を得る。",
        "color": settings.PURPLE,
        "effects": [
            {"type": "take_damage_on_turn_start", "value": 5},
            {"type": "gain_defense_on_turn_end", "value": 10}
        ]
    },
    "poison_orb": {
        "name": "毒のオーブ",
        "description": "ターン終了時、敵全体に1ダメージを与え、毒を1付与する。",
        "color": settings.GREEN,
        "effects": [
            {"type": "damage_all_enemies_on_turn_end", "value": 1},
            {"type": "apply_poison_to_all_enemies_on_turn_end", "value": 1}
        ]
    }
}