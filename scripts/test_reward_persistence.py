# -*- coding: utf-8 -*-
"""
Simple test to check victory reward persistence.
Run from workspace root:
    python scripts/test_reward_persistence.py

This script:
- creates a fake battle_scene with a DeckManager
- calls VictoryRewardScene.finish(chosen_card_id)
- checks that the card was added to the deck_manager's discard pile
- simulates a new battle by replacing deck_manager with a fresh DeckManager
- checks whether the previously added card remains
"""
import sys
import os
# ensure workspace root is on sys.path so `src` package imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.components.deck_manager import DeckManager
from src.scenes.victory_reward_scene import VictoryRewardScene

class DummyBattleScene:
    def __init__(self):
        self.deck_manager = DeckManager()
        # simple player stub with master_deck support
        class P:
            pass
        self.player = P()
        # no master_deck initially
        self.player.master_deck = None


def run_test():
    fake_battle = DummyBattleScene()
    print("Initial deck size:", len(fake_battle.deck_manager.deck))
    print("Initial discard size:", len(fake_battle.deck_manager.discard_pile))

    scene = VictoryRewardScene(fake_battle)
    card_to_add = 'fire_ball'
    print("Adding card via VictoryRewardScene.finish() ->", card_to_add)
    scene.finish(card_to_add)

    print("After finish - discard pile:", fake_battle.deck_manager.discard_pile)
    added = card_to_add in fake_battle.deck_manager.discard_pile
    print("Card added to discard pile?:", added)
    print("Player master_deck after finish:", getattr(fake_battle.player, 'master_deck', None))

    # simulate starting a new battle which calls reset and reinitializes deck_manager
    print('\nSimulating new battle reset (replacing deck_manager)')
    fake_battle.deck_manager = DeckManager()
    print("After reset - discard pile:", fake_battle.deck_manager.discard_pile)
    print("New deck (after reset) contains card?:", card_to_add in fake_battle.deck_manager.deck)
    print("Player master_deck still contains card?:", card_to_add in getattr(fake_battle.player, 'master_deck', []))

if __name__ == '__main__':
    run_test()
