# -*- coding: utf-8 -*-
"""
簡易統合テスト: 会話の選択肢を選ぶと効果が即時適用され、会話が指定の次のイベントにジャンプすることを確認する
実行:
    python -m src.tools.test_conversation_choice_flow
"""
import pygame

from ..components.character import Character
from ..scenes.conversation_scene import ConversationScene


class DummyEnemyManager:
    def __init__(self):
        self.enemies = []


class DummyBattleScene:
    def __init__(self):
        self.enemy_manager = DummyEnemyManager()
        self.deck_manager = None


def run_test():
    # pygame のフォント等を使うビューの初期化のため pygame を初期化する
    pygame.init()

    player = Character(name="Tester", max_hp=100, max_mp=3, attack_power=0, x=0, y=0, character_type='player')
    battle = DummyBattleScene()

    finished = {'called': False, 'effects': None}

    def on_finish(effects):
        finished['called'] = True
        finished['effects'] = effects

    conv = ConversationScene(player, 'monster_battle_intro_conversation', on_finish, battle_scene=battle)

    # 会話イベントの3番目(インデックス2)が選択肢を含むのでそこに移動
    conv.current_event_index = 2
    conv._show_current_event()

    # 一番目の選択肢(攻撃する)を選択して処理
    conv.selected_choice_index = 0
    before_hp = player.current_hp
    conv._process_choice()
    after_hp = player.current_hp

    print(f"Player HP before: {before_hp}, after choice: {after_hp}")
    print(f"Conversation moved to event index: {conv.current_event_index}")
    print(f"Result effects: {conv.result_effects}")

    ok = True
    # 攻撃する選択肢はplayerに15ダメージを与える
    if after_hp != before_hp - 15:
        print("TEST FAIL: expected player to take 15 damage from choice effect.")
        ok = False

    # 会話は next_event_index にジャンプしているはず
    if conv.current_event_index != 3:
        print("TEST FAIL: expected conversation to jump to event index 3.")
        ok = False

    if ok:
        print("TEST PASS: choice applied immediate effect and conversation continued as expected.")
        pygame.quit()
        return 0
    else:
        pygame.quit()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_test())
