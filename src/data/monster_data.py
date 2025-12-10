# -*- coding: utf-8 -*-

MONSTERS = {
    "slime": {
        "name": "スライム",
        "max_hp": 30,
        "max_mp": 0,
        "attack_power": 0,
        "actions": ["normal_attack", "normal_attack", "wait"],
        "gold": 5,
        "image": "src/res/monster/test_monster.png"
    },
    "goblin": {
        "name": "ゴブリン",
        "max_hp": 50,
        "attack_power": 0,
        "actions": ["normal_attack", "strong_attack", "debilitating_strike"],
        "gold": 10,
        "image": "src/res/monster/test_monster.png"
    },
    "venom_spider": {
        "name": "ヴェノムスパイダー",
        "max_hp": 45,
        "attack_power": 0,
        "actions": ["normal_attack", "poison_bite"],
        "gold": 12,
        "image": "src/res/monster/test_monster.png"
    },
    "mage": {
        "name": "魔法使い",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["normal_attack", "fire_spell"],
        "gold": 15,
        "image": "src/res/monster/test_monster.png"
    },
    "shadow_eye": {
        "name": "シャドウアイ",
        "max_hp": 60,
        "attack_power": 0,
        "actions": ["normal_attack", "mind_crush", "mind_crush"],
        "gold": 20,
        "image": "src/res/monster/test_monster.png"
    },
    "mysterious_being": {
        "name": "謎の存在",
        "max_hp": 100,
        "attack_power": 0, # 会話だけでなく、一応攻撃もできるようにしておく
        "actions": ["trigger_conversation", "inflict_hand_curse"], # 会話アクションを優先的に出すため複数回指定
        "gold": 50,
        "image": "src/res/monster/test_monster.png"
    }
    ,
    "test_messenger": {
        "name": "使者の亡霊",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png"
    }
}