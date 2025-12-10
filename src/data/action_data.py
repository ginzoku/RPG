# -*- coding: utf-8 -*-

ACTIONS = {
    "slash": {
        "card_id": "slash",
        "name": "斬りつけ",
        "cost": 1,
        "rarity": "common",
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 7, "hits": 1}
        ]
    },
    "strong_slash": {
        "card_id": "strong_slash",
        "name": "強斬り",
        "cost": 2,
        "rarity": "uncommon",
        "description": "敵に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 23, "hits": 1}
        ]
    },
    "fire_ball": {
        "card_id": "fire_ball",
        "name": "ファイア",
        "cost": 2,
        "rarity": "uncommon",
        "description": "敵に{power}の魔法ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 16, "hits": 1}
        ]
    },
    "guard": {
        "card_id": "guard",
        "name": "防御",
        "cost": 1,
        "rarity": "common",
        "description": "次に受けるダメージを{power}軽減する。",
        "effects": [
            {"type": "gain_defense", "target_scope": "self", "power": 10}
        ]
    },
    "heal_light": {
        "card_id": "heal_light",
        "name": "小ヒール",
        "cost": 1,
        "rarity": "common",
        "target_scope": "self",
        "description": "HPを8回復する。",
        "effects": [
            {"type": "heal", "power": 8}
        ]
    },
    "pass": {
        "card_id": "pass",
        "name": "パス",
        "cost": 0,
        "rarity": "common",
        "description": "何もせずにターンを終了する。",
        "effects": [{"type": "pass"}]
    },
    "expose_weakness": {
        "card_id": "expose_weakness",
        "name": "弱点暴露",
        "cost": 1,
        "rarity": "uncommon",
        "description": "敵に「無防備」を{power}ターン付与する。\n(受けるダメージが1.5倍になる)",
        "effects": [
            {"type": "apply_status", "target_scope": "single", "status_id": "vulnerable", "turns": 2}
        ]
    },
    "healing_light": {
        "card_id": "healing_light",
        "name": "癒やしの光",
        "cost": 2,
        "rarity": "uncommon",
        "description": "自分に「再生」を{power}ターン付与する。\n(ターン終了時にHPが5回復)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "regeneration", "turns": 3}
        ]
    },
    "poison_sting": {
        "card_id": "poison_sting",
        "name": "毒針",
        "cost": 1,
        "rarity": "uncommon",
        "description": "敵に「毒」を{power}ターン付与する。\n(ターン終了時にHPが5減少)",
        "effects": [
            {"type": "apply_status", "target_scope": "single", "status_id": "poison", "turns": 3}
        ]
    },
    "apply_barrier": {
        "card_id": "apply_barrier",
        "name": "バリア展開",
        "cost": 2,
        "rarity": "rare",
        "description": "「バリア」を永続的に展開する。\n(ダメージを受けると解除)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "barrier", "turns": -1}
        ]
    },
    "apply_focus": {
        "card_id": "apply_focus",
        "name": "集中",
        "cost": 1,
        "rarity": "rare",
        "description": "「集中」状態になり、次の攻撃を強化する。\n(デバフを受けると解除)",
        "effects": [
            {"type": "apply_status", "target_scope": "self", "status_id": "focus", "turns": -1}
        ]
    },
    "draw_card": {
        "card_id": "draw_card",
        "name": "ドロー",
        "cost": 1,
        "rarity": "common",
        "description": "カードを{power}枚引く。",
        "effects": [
            {"type": "draw_card", "target_scope": "self", "power": 2}
        ]
    },
    "obliterate": {
        "card_id": "obliterate",
        "name": "消滅",
        "cost": 3,
        "rarity": "legend",
        "exhaust": True,
        "description": "敵に{power}の物理ダメージを与える。このカードは廃棄される。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 30, "hits": 1}
        ]
    },
    "multi_slash": {
        "card_id": "multi_slash",
        "name": "乱れ斬り",
        "cost": 2,
        "rarity": "uncommon",
        "description": "敵単体に{power}の物理ダメージを3回与える。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 8, "hits": 3}
        ]
    },
    "sweep": {
        "card_id": "sweep",
        "name": "薙ぎ払い",
        "cost": 2,
        "rarity": "uncommon",
        "description": "敵全体に{power}の物理ダメージを与える。",
        "effects": [
            {"type": "damage", "target_scope": "all", "power": 12, "hits": 1}
        ]
    },
    "meteor": {
        "card_id": "meteor",
        "name": "流星群",
        "cost": 3,
        "rarity": "rare",
        "description": "敵全体に{power}の魔法ダメージを2回与える。",
        "effects": [
            {"type": "damage", "target_scope": "all", "power": 10, "hits": 2}
        ]
    },
    "forbidden_pact": {
        "card_id": "forbidden_pact",
        "name": "禁断の契約",
        "cost": 1,
        "rarity": "legend",
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
        "card_id": "trigger_conversation",
        "name": "会話イベント発生",
        "cost": 0,
        "rarity": "legend", # 特殊なカードなのでlegendにしておく
        "description": "会話イベントを発生させる。",
        "effects": [
            {"type": "conversation_event", "conversation_id": "monster_battle_intro_conversation"}
        ]
    },
    "throwing_knife": {
        "card_id": "throwing_knife",
        "name": "投げナイフ",
        "cost": 0,
        "rarity": "common",
        "exhaust": True,
        "description": "敵に4の物理ダメージを与える。このカードは廃棄される。",
        "effects": [
            {"type": "damage", "target_scope": "single", "power": 4, "hits": 1}
        ]
    },
    "rain_of_knives": {
        "card_id": "rain_of_knives",
        "name": "ナイフの雨",
        "cost": 2,
        "rarity": "rare",
        "description": "0コスト4ダメージの「投げナイフ」を3枚手札に加える。",
        "effects": [
            {"type": "add_card_to_hand", "target_scope": "self", "card_id": "throwing_knife", "amount": 3, "temporary": True}
        ]
    },
    "research": {
        "card_id": "research",
        "name": "調査",
        "cost": 1,
        "rarity": "uncommon",
        "description": "アンコモンのカードを3枚発見し、そのうち1枚を手札に加える。",
        "effects": [
            {"type": "discover_card", "target_scope": "self", "rarity": "uncommon", "count": 3}
        ]
    }
    ,
    "hand_burning_curse": {
        "card_id": "hand_burning_curse",
        "name": "灼熱の呪い",
        "cost": 0,
        "rarity": "special",
        "unplayable": True,
        "temporary": True,
        "description": "手札にあるとターン終了時に10ダメージを受ける。一時的で使用不可。",
        "on_turn_end": [
            {"type": "damage", "target_scope": "player", "power": 10}
        ]
    }
}