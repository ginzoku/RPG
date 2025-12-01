# -*- coding: utf-8 -*-

ACTIONS = {
    "slash": {
        "name": "斬りつけ",
        "type": "attack",
        "damage_type": "physical",
        "power": 7, # 基本威力
        "cost": 1,
        "description": "敵に{power}の物理ダメージを与える。",
    },
    "strong_slash": {
        "name": "強斬り",
        "type": "attack",
        "damage_type": "physical",
        "power": 23, # 基本威力
        "cost": 2,
        "description": "敵に{power}の物理ダメージを与える。",
    },
    "fire_ball": {
        "name": "ファイア",
        "type": "attack",
        "damage_type": "magical",
        "power": 16,  # 固定ダメージ
        "cost": 2,
        "description": "敵に{power}の魔法ダメージを与える。",
    },
    "guard": {
        "name": "防御",
        "type": "skill",
        "power": 10,  # 次に受けるダメージをこの値だけ減らす
        "cost": 1,
        "description": "次に受けるダメージを{power}軽減する。",
    },
    "pass": {
        "name": "パス",
        "type": "skill",
        "cost": 0,
        "description": "何もせずにターンを終了する。",
    },
    "expose_weakness": {
        "name": "弱点暴露",
        "type": "skill",
        "target": "enemy",
        "effect": "vulnerable", # 状態異常ID
        "power": 2, # 2ターン付与
        "cost": 1,
        "description": "敵に「無防備」を{power}ターン付与する。\n(受けるダメージが1.5倍になる)",
    },
    "healing_light": {
        "name": "癒やしの光",
        "type": "skill",
        "target": "self",
        "effect": "regeneration",
        "power": 3, # 3ターン付与
        "cost": 2,
        "description": "自分に「再生」を{power}ターン付与する。\n(ターン終了時にHPが5回復)",
    },
    "draw_card": {
        "name": "ドロー",
        "type": "skill",
        "power": 2, # 2枚ドロー
        "cost": 1,
        "description": "カードを{power}枚引く。",
    }
}