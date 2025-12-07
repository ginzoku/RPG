# -*- coding: utf-8 -*-

ACTIONS = {
    "slash": {
        "name": "斬りつけ",
        "cost": 1,
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 7, "hits": 1}
        ]
    },
    "strong_slash": {
        "name": "強斬り",
        "cost": 2,
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 23, "hits": 1}
        ]
    },
    "fire_ball": {
        "name": "ファイア",
        "cost": 2,
        "description": "敵に{power}の魔法ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 16, "hits": 1}
        ]
    },
    "guard": {
        "name": "防御",
        "cost": 1,
        "description": "次に受けるダメージを{power}軽減する。",
        "effects": [
            {"type": "gain_defense", "target_scope": "self", "power": 10}
        ]
    },
    "heal_light": {
        "name": "小ヒール",
        "cost": 1,
        "target_scope": "self",
        "description": "HPを8回復する。",
        "effects": [
            {"type": "heal", "power": 8}
        ]
    },
    "pass": {
        "name": "パス",
        "cost": 0,
        "description": "何もせずにターンを終了する。",
        "effects": [{"type": "pass"}]
    },
    "expose_weakness": {
        "name": "弱点暴露",
        "cost": 1,
        "description": "敵に「無防備」を{power}ターン付与する。\n(受けるダメージが1.5倍になる)",
        "effects": [
            {"type": "apply_status", "target_scope": "single", "status_id": "vulnerable", "turns": 2}
        ]
    },
    "healing_light": {
        "name": "癒やしの光",
        "cost": 2,
        "description": "自分に「再生」を{power}ターン付与する。\n(ターン終了時にHPが5回復)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "regeneration", "turns": 3}
        ]
    },
    "poison_sting": {
        "name": "毒針",
        "cost": 1,
        "description": "敵に「毒」を{power}ターン付与する。\n(ターン終了時にHPが5減少)",
        "effects": [
            {"type": "apply_status", "target_scope": "single", "status_id": "poison", "turns": 3}
        ]
    },
    "apply_barrier": {
        "name": "バリア展開",
        "cost": 2,
        "description": "「バリア」を永続的に展開する。\n(ダメージを受けると解除)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "barrier", "turns": -1}
        ]
    },
    "apply_focus": {
        "name": "集中",
        "cost": 1,
        "description": "「集中」状態になり、次の攻撃を強化する。\n(デバフを受けると解除)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "focus", "turns": -1}
        ]
    },
    "draw_card": {
        "name": "ドロー",
        "cost": 1,
        "description": "カードを{power}枚引く。",
        "effects": [
            {"type": "draw_card", "target_scope": "self", "power": 2}
        ]
    },
    "obliterate": {
        "name": "消滅",
        "cost": 3,
        "exhaust": True,
        "description": "敵に{power}の物理ダメージを与える。このカードは廃棄される。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 30, "hits": 1}
        ]
    },
    "multi_slash": {
        "name": "乱れ斬り",
        "cost": 2,
        "description": "敵単体に{power}の物理ダメージを3回与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 8, "hits": 3}
        ]
    },
    "sweep": {
        "name": "薙ぎ払い",
        "cost": 2,
        "description": "敵全体に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "all", "power": 12, "hits": 1}
        ]
    },
    "meteor": {
        "name": "流星群",
        "cost": 3,
        "description": "敵全体に{power}の魔法ダメージを2回与える。",
        "effects": [
            {"type": "damage", "target_scope": "all", "power": 10, "hits": 2}
        ]
    },
    "forbidden_pact": {
        "name": "禁断の契約",
        "cost": 1,
        "exhaust": True,
        "description": "攻撃力と防御力が永続的に5、最大マナが1増える。ターン終了時に10のHPを失うようになる（防御不可）。",
        "effects": [
            {"type": "stat_change", "target_scope": "self", "stat": "attack_power", "value": 5},
            {"type": "stat_change", "target_scope": "self", "stat": "defense_power", "value": 5},
            {"type": "stat_change", "target_scope": "self", "stat": "max_mana", "value": 1},
            {"type": "apply_permanent_effect", "target_scope": "self", "effect_id": "blood_pact"}
        ]
    },
    "trigger_conversation": {
        "name": "会話イベント発生",
        "cost": 0,
        "description": "会話イベントを発生させる。",
        "effects": [
            {"type": "conversation_event", "conversation_id": "monster_battle_intro_conversation"}
        ]
    }
}