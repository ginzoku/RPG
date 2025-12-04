# -*- coding: utf-8 -*-

CONVERSATIONS = {
    "monster_battle_intro_conversation": { # 会話ID
        "default_background": "assets/backgrounds/forest_battle.png", # 会話イベント全体のデフォルト背景
        "events": [ # 会話の進行を示すイベントのリスト
            {"speaker": "モンスター", "text": "よくぞここまで来たな、勇者よ！"},
            {"speaker": "モンスター", "text": "だが、ここから先には一歩も行かせん！"},
            {
                "speaker": "モンスター",
                "text": "さて、どうする？",
                "choices": [
                    {
                        "text": "攻撃する",
                        "effects": [
                            {"type": "damage", "target_scope": "player", "power": 15, "hits": 1} # 例: プレイヤーにダメージ
                        ],
                        "next_event_index": 3 # 選択後の次の会話イベントのインデックス
                    },
                    {
                        "text": "様子を見る",
                        "effects": [
                            {"type": "gain_mana", "target_scope": "player", "power": 1} # 例: プレイヤーのマナ回復
                        ],
                        "next_event_index": 4
                    }
                ]
            },
            {"speaker": "モンスター", "text": "ほう、攻撃してきたか！貴様の命運もここまで！", "event_index": 3}, # "next_event_index"で指定されたジャンプ先
            {"speaker": "モンスター", "text": "様子を見るとは賢明だな。だが、いずれにせよ無駄だ！", "event_index": 4},
            {"speaker": "モンスター", "text": "さあ、決着をつけよう！"},
        ]
    },
    "npc_1_intro": {
        "default_background": None, # NPC会話には背景がない場合
        "events": [
            {"speaker": "老人", "text": "やあ、旅の者よ。"},
            {"speaker": "老人", "text": "この先には恐ろしい魔物が待ち構えておる。"},
            {"speaker": "勇者", "text": "……！"},
            {"speaker": "老人", "text": "準備は怠らんことじゃな。"},
        ]
    }
}