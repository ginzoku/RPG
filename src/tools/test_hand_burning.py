# -*- coding: utf-8 -*-
"""
簡易テスト: hand_burning_curse が手札にあるとターン終了時に10ダメージを受けることを確認する
実行方法:
    python -m src.tools.test_hand_burning
"""

from ..components.character import Character
from ..components.deck_manager import DeckManager


def run_test():
    # プレイヤーを作成
    player = Character(name="Tester", max_hp=100, max_mp=3, attack_power=0, x=0, y=0, character_type='player')

    # デッキマネージャを作成してカードを手札に追加
    dm = DeckManager()
    # テスト用に手札を空にしてから追加
    dm.hand = []

    # hand_burning_curse を一時的カードとして手札に追加
    dm.add_card_to_hand('hand_burning_curse', temporary=True)

    print(f"Before end of turn: player HP = {player.current_hp}")

    # ターン終了時効果を適用
    dm.apply_hand_end_of_turn_effects(player)

    print(f"After end of turn: player HP = {player.current_hp}")

    expected = 90
    if player.current_hp == expected:
        print("TEST PASS: hand_burning_curse dealt 10 damage as expected.")
        return 0
    else:
        print(f"TEST FAIL: expected HP {expected}, got {player.current_hp}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_test())
