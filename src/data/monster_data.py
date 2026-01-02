# -*- coding: utf-8 -*-

MONSTERS = {
    "slime": {
        "name": "スライム",
        "max_hp": 30,
        "max_mp": 0,
        "attack_power": 0,
        "actions": ["normal_attack", "normal_attack", "wait"],
        "gold": 5,
        "image": "src/res/monster/test_monster.png",
        "description": "小さくて柔らかいスライム。攻撃力は低いが数で押してくる。"
    },
    "goblin": {
        "name": "ゴブリン",
        "max_hp": 50,
        "attack_power": 0,
        "actions": ["normal_attack", "strong_attack", "debilitating_strike"],
        "gold": 10,
        "image": "src/res/monster/test_monster.png",
        "description": "好戦的なゴブリン。素早く斬りかかってくる。"
    },
    "venom_spider": {
        "name": "ヴェノムスパイダー",
        "max_hp": 45,
        "attack_power": 0,
        "actions": ["normal_attack", "poison_bite"],
        "gold": 12,
        "image": "src/res/monster/test_monster.png",
        "description": "毒を持つクモ。噛まれると毒状態になるので注意。"
    },
    "mage": {
        "name": "魔法使い",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["normal_attack", "fire_spell"],
        "gold": 15,
        "image": "src/res/monster/test_monster.png",
        "description": "魔力を使って攻撃する魔法使い。遠距離から強力な魔法を放つ。"
    },
    "shadow_eye": {
        "name": "シャドウアイ",
        "max_hp": 60,
        "attack_power": 0,
        "actions": ["normal_attack", "mind_crush", "mind_crush"],
        "gold": 20,
        "image": "src/res/monster/test_monster.png",
        "description": "闇に潜む目のような存在。精神を攻撃してくる危険な相手。"
    },
    "mysterious_being": {
        "name": "謎の存在",
        "max_hp": 100,
        "attack_power": 0, # 会話だけでなく、一応攻撃もできるようにしておく
        "actions": ["trigger_conversation", "inflict_hand_curse"], # 会話アクションを優先的に出すため複数回指定
        "gold": 50,
        "image": "src/res/monster/test_monster.png",
        "description": "正体不明の存在。会話で不可思議な影響を与えることがある。"
    }
    ,
    "test_messenger": {
        "name": "使者の亡霊",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    
    
    "Android": {
        "name": "アンドロイド",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "イェンダーによって作られた試験用アンドロイド。\n +\
                        いくつかの拷問用の搾精器具が内蔵されており、\n +\
                        頭部には唇、胸部には大型の乳房型機関が格納されている。"
    },
    "Breast_Machine_Giga": {
        "name": "ブレストマシン・ギガ",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "巨大な胸部を複数備えた搾精特化兵器。\n +\
                        吸引によって胸部に対象を固定し、包み込んで搾精を行う他、\n +\
                        粘度の高いミルクは侵入者を夢見心地に堕とす。"
    },
    "Cultist": {
        "name": "カルティスト",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "異星の神の信者。\n +\
                        神への供物として精液をささげるため、\n +\
                        同調の儀式や搾精生物によって精を搾り取る。"
    },
    "Dragon": {
        "name": "ドラゴン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "現世で最上位に存在する強力な魔物。\n +\
                        雌しか存在しないため、常につがいとなる雄を求めている。\n +\
                        魔力量に比例して胸が大きく発達する"
    },
    "Dragon_Princess": {
        "name": "ドラゴン・プリンセス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "ドラゴン族でも特に強力な王女の個体。\n +\
                        持ち前の爆乳とフェロモンに多くの男が犠牲になった。\n +\
                        高飛車な性格で、全ての雄を見下している。"
    },
    "Elder_Witch": {
        "name": "エルダー・ウィッチ",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Fairy": {
        "name": "フェアリー",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Ghost": {
        "name": "ゴースト",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
        "Gigantess": {
        "name": "ギガンテス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Hobgoblin": {
        "name": "ホブゴブリン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Imp": {
        "name": "インプ",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Jester": {
        "name": "ジェスター",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Kobold": {
        "name": "コボルド",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Kobold_Leader": {
        "name": "コボルドリーダー",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Lilith": {
        "name": "リリス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Legion": {
        "name": "レギオン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Minotauros": {
        "name": "ミノタウロス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Nipple_Eater": {
        "name": "ナイトメアマシーン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Orc": {
        "name": "オーク",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Phantom": {
        "name": "ファントム",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Queen_Succubus": {
        "name": "クイーンサキュバス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Rogue": {
        "name": "ローグ",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Succubus": {
        "name": "サキュバス",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Twins_Left": {
        "name": "ツインズ・レフト",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Twins_Right": {
        "name": "ツインズ・ライト",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Tamamo": {
        "name": "タマモ",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Unknown": {
        "name": "アンノウン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Unicorn": {
        "name": "ユニコーン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Black_Unicorn": {
        "name": "ブラックユニコーン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Variant": {
        "name": "ヴァリアント",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Writhing_One": {
        "name": "ライジングワン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "イェンダーの魔術師が呼び出した異星からの存在。\n +\
                        変異した肉体を使用して襲い掛かってくる。\n +\
                        自身の肉体から触手を分離することも可能なようだ。"
    },
    "Xeroc": {
        "name": "ゼロック",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "物まねの怪物。普段は宝箱に化けている。\n +\
                        罠にかかった冒険者に対して襲いかかるが、\n +\
                        その際にはダンジョンにいる最も強力な存在を真似るという。"
    },
    "Young_Dragon": {
        "name": "ヤングドラゴン",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "比較的低位に属するドラゴンの子供。\n +\
                        火炎などの強力な攻撃はまだ行えないが、\n +\
                        光り輝く財宝類は既に大好きなようだ。"
    },
    "Zombie_Master": {
        "name": "ゾンビマスター",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "使者の亡霊。テスト用の会話トリガーを持つ。"
    },
    "Yendor_Wizard_of_Dungeon": {
        "name": "イェンダーの魔術師",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "ついに正体を現した不死の力を求める魔術師。\n +\
                        様々な魔術や異星の儀式、機械技術までをも研究し、\n +\
                        不死の力を手に入れたといわれる狂人。\n +\
                        その目的は、この世界を掌握することただ一つである。"
    },
    "Shopper_1": {
        "name": "店主ちゃん1号",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "ダンジョンの中でけなげに店を営む少女。\n +\
                        侵入者相手に商売しているだけあって、\n +\
                        並みのモンスターよりも強いらしい。"
    },
    "Shopper_2": {
        "name": "店主ちゃん2号",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "ダンジョンの中でけなげに店を営む少女。\n +\
                        より恐ろしく厳しい2層に適応するために、 \n +\
                        毎日の鍛錬は欠かさないらしい。"
    },
    "Shopper_3": {
        "name": "店主ちゃん3号",
        "max_hp": 40,
        "attack_power": 0,
        "actions": ["trigger_test_choice_conversation", "wait"],
        "gold": 0,
        "image": "src/res/monster/test_monster.png",
        "description": "ダンジョンの中でけなげに店を営む少女。\n +\
                        最深部でも生き残るために厳しい鍛錬を積んだ結果、\n +\
                        そろそろ人間かどうか怪しくなってきたらしい。"
    },
}
