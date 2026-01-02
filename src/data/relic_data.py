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
    },
    "shield_of_timing": {
        "name": "タイミングの盾",
        "description": "戦闘の3ターン目に防御を18得る。",
        "color": settings.BLUE,
        "effects": [
            {"type": "gain_defense_on_turn", "value": 18, "turn": 3}
        ]
    },
    "mana_exchange_amulet": {
        "name": "マナ交換の護符",
        "description": "最大マナが1増加する。自身の攻撃力が1減少し、敵全体の攻撃力が1増加する。",
        "color": settings.YELLOW,
        "effects": [
            {"type": "stat_change", "stat": "max_mana", "value": 1},
            # {"type": "stat_change", "stat": "attack_power", "value": -1}, # 自身に適用
            {"type": "enemy_stat_change", "stat": "attack_power", "value": 1} # 敵全体に適用
        ]
    }
    ,
    "blood_moon_charm": {
        "name": "ブラッドムーンの護符",
        "description": "最初の3回の戦闘開始時に、出現した敵全てのHPを1にする。3回使用すると無効化される。",
        "color": settings.DARK_RED if hasattr(settings, 'DARK_RED') else settings.RED,
        "effects": [
            {"type": "reduce_enemies_to_one_on_battle_start", "uses": 3}
        ]
    }
}