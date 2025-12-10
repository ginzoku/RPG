# -*- coding: utf-8 -*-
"""
テスト: 敵のアクションで会話が発生し、BattleScene.start_conversation によって
ConversationScene が生成され、その `source_enemy` が正しく渡されることを確認する
実行:
    python -m src.tools.test_enemy_conversation_flow
"""
import pygame
from ..components.character import Character
from ..components.monster import Monster
from ..scenes.battle_scene import BattleScene


def run_test():
    pygame.init()
    player = Character(name="Player", max_hp=100, max_mp=3, attack_power=0, x=0, y=0, character_type='player', max_sanity=100)
    battle = BattleScene(player)

    # 検証用のモンスターを作成して、EnemyManager の enemies に差し替える
    monster = Monster(name="TestMonster", max_hp=30, attack_power=5, actions=['trigger_conversation'], x=100, y=100, gold=10)
    monster.is_animating = True
    monster.animation_start_time = 0
    monster.animation_duration = 0.0
    monster.pending_conversation_id = 'monster_battle_intro_conversation'

    battle.enemy_manager.enemies = [monster]
    battle.enemy_manager.turn_state = 'start'

    # 1回目の update_turn: turn_state が 'start' から 'acting' に変わる
    battle.enemy_manager.update_turn()
    # 2回目の update_turn: アニメーション終了とともに会話が開始されるはず
    battle.enemy_manager.update_turn()

    current_scene = battle.current_scene
    pygame.quit()

    if current_scene and getattr(current_scene, 'source_enemy', None) is monster:
        print('TEST PASS: ConversationScene received source_enemy from EnemyManager via BattleScene.')
        return 0
    else:
        print('TEST FAIL: ConversationScene did not receive source_enemy correctly.')
        print('current_scene:', type(current_scene), 'source_enemy:', getattr(current_scene, 'source_enemy', None))
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(run_test())
