# -*- coding: utf-8 -*-
import pygame
import math
import random
from ..components.character import Character
from ..components.monster import Monster
from ..data.action_data import ACTIONS
from ..components.deck_manager import DeckManager
from ..components.action_handler import ActionHandler
from ..components.enemy_manager import EnemyManager
from ..components.input_handler import InputHandler
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.relic_data import RELICS
from ..data.enemy_group_data import ENEMY_GROUPS, ENEMY_POSITIONS
from ..config import settings

class BattleScene:
    def __init__(self, player: Character):
        self.player = player
        self.reset("goblin_duo") # デフォルトの敵グループで初期化

    def reset(self, enemy_group_id: str):
        # 敵の初期化
        self.enemy_manager = EnemyManager(self.player)
        self.enemy_manager.setup_enemies(enemy_group_id)
        self.input_handler = InputHandler(self)
        
        # ゲーム状態
        self.turn: str = "player"
        self.game_over: bool = False
        self.winner: str | None = None
        self.hovered_card_index: int | None = None
        self.hovered_relic_index: int | None = None
        self.targeted_enemy_index: int | None = None # 現在選択されている敵のインデックス
        self.reward_gold: int = 0 # 勝利時に獲得するゴールド
        
        # プレイヤーの戦闘開始時の状態リセット
        self.player.reset_for_battle()
        self.deck_manager = DeckManager()
        self.deck_manager.draw_cards(5)

        # バトル開始時に一番左の敵をデフォルトターゲットに設定
        first_living_enemy_index = next((i for i, e in enumerate(self.enemy_manager.enemies) if e.is_alive), None)
        self.targeted_enemy_index = first_living_enemy_index

    def _check_game_over(self):
        if all(not enemy.is_alive for enemy in self.enemy_manager.enemies):
            self.reward_gold = sum(enemy.gold for enemy in self.enemy_manager.enemies)
            self.player.gold += self.reward_gold
            self.game_over = True
            self.winner = "player"
        if not self.player.is_alive:
            self.game_over = True
            self.winner = "enemy"

    def _update_target_after_enemy_death(self):
        """
        ターゲット中の敵が倒された場合に、次のターゲットを自動で選択する。
        右隣の敵、いなければ左端の敵をターゲットにする。
        """
        if self.targeted_enemy_index is None:
            return

        # 現在のターゲットがまだ生きているか、そもそも敵が全滅している場合は何もしない
        if self.enemy_manager.enemies[self.targeted_enemy_index].is_alive or all(not e.is_alive for e in self.enemy_manager.enemies):
            return

        num_enemies = len(self.enemy_manager.enemies)
        # 倒された敵の右隣から探し始める
        for i in range(1, num_enemies):
            next_index = (self.targeted_enemy_index + i) % num_enemies
            if self.enemy_manager.enemies[next_index].is_alive:
                self.targeted_enemy_index = next_index
                return
        
        # 生きている敵が見つからなかった場合 (全滅)
        self.targeted_enemy_index = None
    
    def end_player_turn(self):
        self.turn = "enemy"
        # 敵の防御値をリセット
        for enemy in self.enemy_manager.enemies:
            enemy.defense_buff = 0
        self.player.decrement_status_effects() # プレイヤーのターン終了処理
        self.deck_manager.discard_hand()
        self.hovered_card_index = None
        self.enemy_manager.turn_state = "start"

    def set_target(self, enemy_index: int):
        """指定されたインデックスの敵をターゲットに設定する"""
        self.targeted_enemy_index = enemy_index

    def execute_card_action(self, card_index: int):
        """指定されたカードのアクションを実行する"""
        action_id = self.deck_manager.hand[card_index]
        action = ACTIONS[action_id]

        target_enemy = None
        if self.targeted_enemy_index is not None and self.enemy_manager.enemies[self.targeted_enemy_index].is_alive:
            target_enemy = self.enemy_manager.enemies[self.targeted_enemy_index]

        # 攻撃カードの場合、ターゲットが必要
        if action["type"] == "attack":
            if not target_enemy:
                return
            ActionHandler.execute_player_action(self.player, target_enemy, action_id, self.deck_manager)
        # 攻撃以外（スキルなど）なら即時実行
        else:
            dummy_target = target_enemy or next((e for e in self.enemy_manager.enemies if e.is_alive), None)
            if not dummy_target: return # 実行対象がいない
            ActionHandler.execute_player_action(self.player, dummy_target, action_id, self.deck_manager)

        self.deck_manager.move_used_card(card_index)
        self.hovered_card_index = None # ホバー状態をリセット
        self._update_target_after_enemy_death()
        self._check_game_over()
        if self.game_over: self.end_player_turn()

    def process_input(self, event: pygame.event.Event):
        """入力処理をInputHandlerに委譲する"""
        self.input_handler.process_event(event)

    def update_state(self):
        if self.turn == "enemy" and not self.game_over:
            self.enemy_manager.update_turn()
            self._check_game_over()

            if self.enemy_manager.turn_state == "finished":
                # 敵のターン終了処理
                for enemy in self.enemy_manager.enemies:
                    enemy.decide_next_action()
                    enemy.decrement_status_effects()
                
                # プレイヤーの防御値をリセット
                self.player.defense_buff = 0
                
                self.turn = "player"
                self.deck_manager.draw_cards(5)
                self.player.fully_recover_mana()