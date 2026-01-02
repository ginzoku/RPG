# -*- coding: utf-8 -*-

CONVERSATIONS = {
    "monster_battle_intro_conversation": { # 会話ID
        "default_background": "assets/backgrounds/forest_battle.png", # 会話イベント全体のデフォルト背景
        "events": [ # 会話の進行を示すイベントのリスト
            {"speaker": "モンスター", "text": "よくぞここまで来たな、勇者よ！"},
            {
                "speaker": "モンスター", "text": "だが、ここから先には一歩も行かせん！",
                "background": "assets/backgrounds/dark_forest.png"
            }, # テキストごとに背景を変更
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
            {"speaker": "モンスター", "text": "さあ、決着をつけよう！", "background": None}, # 背景を非表示にする
        ]
    },
    "npc_1_intro": {
        "default_background": None, # NPC会話には背景がない場合
        # スピーカーごとの画像パス（相対パスまたは絶対パス）。ビューが解決して読み込みます。
        "speaker_images": {
            "老人": "src/res/npc/npc.png"
        },
        "events": [
            {"speaker": "老人", "text": "やあ、旅の者よ。"},
            {"speaker": "老人", "text": "この先には恐ろしい魔物が待ち構えておる。"},
            {"speaker": "勇者", "text": "……！"},
            {"speaker": "老人", "text": "準備は怠らんことじゃな。"},
        ]
    }
    ,
    "npc_new_intro": {
        "default_background": None,
        # example: use a per-event list so the image can change by event index
        "speaker_images": {
            "旅人": [
                "src/res/npc/npc.png",
                "src/res/npc/npc.png"
            ]
        },
        "events": [
            {"speaker": "旅人", "text": "ようこそ。久しぶりに人に会ったよ。"},
            {"speaker": "旅人", "text": "ここから先は気をつけたほうがいい。さあ、気をつけて行くんだ。", "end": True}
        ]
    }
    ,
    "test_choice_conversation": {
        "default_background": None,
        "events": [
            {
                "speaker": "謎の声",
                "text": "テスト文章",
                "choices": [
                    {
                        "text": "選択肢A: 灼熱の呪縛を付与する攻撃",
                        "effects": [
                            {"type": "damage", "target_scope": "player", "power": 5, "hits": 1},
                            {"type": "add_card_to_hand", "target_scope": "player", "card_id": "hand_burning_curse", "amount": 1, "temporary": True}
                        ],
                        "next_event_index": 1
                    },
                    {
                        "text": "選択肢B: 正気度を減らしバリアを付与",
                        "effects": [
                            {"type": "apply_status", "target_scope": "player", "status_id": "weak", "turns": 1},
                            {"type": "sanity_damage", "target_scope": "player", "power": 10}
                        ],
                        "next_event_index": 2
                    }
                ]
            },
            {"speaker": "謎の声", "text": "テスト文章A", "end": True},
            {"speaker": "謎の声", "text": "テスト文章B"}
        ]
    }
}