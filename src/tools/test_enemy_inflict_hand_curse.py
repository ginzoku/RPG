# -*- coding: utf-8 -*-
"""
簡易テスト: モンスターアクション 'inflict_hand_curse' がプレイヤーの手札に
一時的な 'hand_burning_curse' を追加することを確認する

実行:
    python -m src.tools.test_enemy_inflict_hand_curse
"""
from ..components.character import Character
from ..components.deck_manager import DeckManager
from ..components.action_handler import ActionHandler


def run_test():
    player = Character(name="Player", max_hp=50, max_mp=3, attack_power=0, x=0, y=0, character_type='player')
    deck_manager = DeckManager()
    # 空手札にする
    deck_manager.hand = []

    # モンスターを擬似的に作成
    monster = Character(name="Monster", max_hp=30, max_mp=0, attack_power=5, x=0, y=0, character_type='monster')

    # MONSTER_ACTIONS 内の 'inflict_hand_curse' を呼び出す
    ActionHandler.execute_monster_action(monster, [player], 'inflict_hand_curse', deck_manager)

    print(f"Hand after action: {deck_manager.hand}")
    if 'hand_burning_curse' in deck_manager.hand:
        print("TEST PASS: hand_burning_curse was added to player's hand.")
        return 0
    else:
        print("TEST FAIL: hand_burning_curse was not added.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(run_test())
