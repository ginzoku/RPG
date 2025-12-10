# -*- coding: utf-8 -*-
"""
テスト: `test_choice_conversation` の両選択肢を実行して効果が即時適用されるか確認する
実行:
    python -m src.tools.test_conversation_testchoice
"""
import pygame
from ..components.character import Character
from ..components.deck_manager import DeckManager
from ..scenes.conversation_scene import ConversationScene


class DummyEnemyManager:
    def __init__(self):
        self.enemies = []


class DummyBattleScene:
    def __init__(self):
        self.enemy_manager = DummyEnemyManager()
        self.deck_manager = DeckManager()


def run_choice_a_test():
    pygame.init()
    player = Character(name="TesterA", max_hp=100, max_mp=3, attack_power=0, x=0, y=0, character_type='player')
    battle = DummyBattleScene()

    finished = {'called': False, 'effects': None}
    def on_finish(effects):
        finished['called'] = True
        finished['effects'] = effects

    conv = ConversationScene(player, 'test_choice_conversation', on_finish, battle_scene=battle)
    conv.current_event_index = 0
    conv._show_current_event()
    conv.selected_choice_index = 0
    before_hp = player.current_hp
    conv._process_choice()
    after_hp = player.current_hp
    has_curse = 'hand_burning_curse' in battle.deck_manager.hand
    pygame.quit()
    print('Choice A -> HP before:', before_hp, 'after:', after_hp, 'curse_in_hand:', has_curse)
    return after_hp == before_hp - 5 and has_curse


def run_choice_b_test():
    pygame.init()
    player = Character(name="TesterB", max_hp=100, max_mp=3, attack_power=0, x=0, y=0, character_type='player')
    battle = DummyBattleScene()

    finished = {'called': False, 'effects': None}
    def on_finish(effects):
        finished['called'] = True
        finished['effects'] = effects

    conv = ConversationScene(player, 'test_choice_conversation', on_finish, battle_scene=battle)
    conv.current_event_index = 0
    conv._show_current_event()
    conv.selected_choice_index = 1
    before_sanity = player.current_sanity
    conv._process_choice()
    after_sanity = player.current_sanity
    has_weak = ('weak' in player.status_effects and player.status_effects.get('weak', 0) > 0)
    pygame.quit()
    print('Choice B -> sanity before:', before_sanity, 'after:', after_sanity, 'weak_present_guess:', has_weak)
    return after_sanity == (before_sanity - 10 if before_sanity is not None else before_sanity) and has_weak


def run_test():
    a_ok = run_choice_a_test()
    b_ok = run_choice_b_test()
    if a_ok and b_ok:
        print('TEST PASS: both choice effects applied as specified.')
        return 0
    else:
        print('TEST FAIL: one or more choices did not apply as expected. A_ok=', a_ok, 'B_ok=', b_ok)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_test())
