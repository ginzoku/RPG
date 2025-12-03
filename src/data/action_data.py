# -*- coding: utf-8 -*-

ACTIONS = {
    "slash": {
        "name": "斬りつけ",
        "cost": 1,
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target": "enemy", "damage_type": "physical", "power": 7}
        ]
    },
    "strong_slash": {
        "name": "強斬り",
        "cost": 2,
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target": "enemy", "damage_type": "physical", "power": 23}
        ]
    },
    "fire_ball": {
        "name": "ファイア",
        "cost": 2,
        "description": "敵に{power}の魔法ダメージを与える。",
        "effects": [
            {"type": "damage", "target": "enemy", "damage_type": "magical", "power": 16}
        ]
    },
    "guard": {
        "name": "防御",
        "cost": 1,
        "description": "次に受けるダメージを{power}軽減する。",
        "effects": [
            {"type": "gain_defense", "target": "self", "power": 10}
        ]
    },
    "pass": {
        "name": "パス",
        "cost": 0,
        "description": "何もせずにターンを終了する。",
        "effects": []
    },
    "expose_weakness": {
        "name": "弱点暴露",
        "cost": 1,
        "description": "敵に「無防備」を{power}ターン付与する。\n(受けるダメージが1.5倍になる)",
        "effects": [
            {"type": "apply_status", "target": "enemy", "status_id": "vulnerable", "turns": 2}
        ]
    },
    "healing_light": {
        "name": "癒やしの光",
        "cost": 2,
        "description": "自分に「再生」を{power}ターン付与する。\n(ターン終了時にHPが5回復)",
        "effects": [
            {"type": "apply_status", "target": "self", "status_id": "regeneration", "turns": 3}
        ]
    },
    "poison_sting": {
        "name": "毒針",
        "cost": 1,
        "description": "敵に「毒」を{power}ターン付与する。\n(ターン終了時にHPが5減少)",
        "effects": [
            {"type": "apply_status", "target": "enemy", "status_id": "poison", "turns": 3}
        ]
    },
    "apply_barrier": {
        "name": "バリア展開",
        "cost": 2,
        "description": "「バリア」を永続的に展開する。\n(ダメージを受けると解除)",
        "effects": [
            {"type": "apply_status", "target": "self", "status_id": "barrier", "turns": -1}
        ]
    },
    "apply_focus": {
        "name": "集中",
        "cost": 1,
        "description": "「集中」状態になり、次の攻撃を強化する。\n(デバフを受けると解除)",
        "effects": [
            {"type": "apply_status", "target": "self", "status_id": "focus", "turns": -1}
        ]
    },
    "draw_card": {
        "name": "ドロー",
        "cost": 1,
        "description": "カードを{power}枚引く。",
        "effects": [
            {"type": "draw_card", "power": 2}
        ]
    },
    "obliterate": {
        "name": "消滅",
        "cost": 3,
        "exhaust": True,
        "description": "敵に{power}の物理ダメージを与える。このカードは廃棄される。",
        "effects": [
            {"type": "damage", "target": "enemy", "damage_type": "physical", "power": 30}
        ]
    }
}