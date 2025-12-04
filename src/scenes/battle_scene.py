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
from ..scenes.conversation_scene import ConversationScene
from ..config import settings

class BattleScene:
    def __init__(self, player: Character):
        self.player = player
        self.current_scene = self # BattleScene自身を初期シーンとして設定
        self.reset("conversation_test_group") # デフォルトの敵グループで初期化

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
        if not self.game_over:
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

        targets = []
        # 最初の効果のtarget_scopeに基づいてターゲットを決定する
        first_effect = action.get("effects", [{}])[0]
        target_scope = first_effect.get("target_scope")

        if target_scope == "self":
            targets = [self.player]
        elif target_scope == "single":
            if self.targeted_enemy_index is not None and self.enemy_manager.enemies[self.targeted_enemy_index].is_alive:
                targets = [self.enemy_manager.enemies[self.targeted_enemy_index]]
        elif target_scope == "all":
            targets = [enemy for enemy in self.enemy_manager.enemies if enemy.is_alive]

        # ターゲットが必要なのに選択されていない場合は実行しない
        if not targets and target_scope not in ["self", None]:
            return

        # アクションを実行。ActionHandlerが各効果のターゲットを適切に処理する
        # 注意: ここでは最初の効果のターゲットリストを渡している。
        # 1アクションに複数のtarget_scopeが混在する場合は、ActionHandler側でのさらなる修正が必要。
        ActionHandler.execute_player_action(self.player, targets, action_id, self.deck_manager)

        self.deck_manager.move_used_card(card_index)
        self.hovered_card_index = None # ホバー状態をリセット
        self._update_target_after_enemy_death()
        self._check_game_over()
        if self.game_over: self.end_player_turn()

    def process_input(self, event: pygame.event.Event):
        """入力処理をInputHandlerに委譲するか、現在のシーンに委譲する"""
        if self.current_scene == self: # バトルシーンがアクティブな場合
            self.input_handler.process_event(event)
        else: # 会話シーンがアクティブな場合
            self.current_scene.process_input(event)

    def update_state(self):
        """ゲームの状態を更新する"""
        if self.current_scene == self: # バトルシーンがアクティブな場合
            # 既存のバトルシーンのupdate_stateロジック
            if self.turn == "enemy" and not self.game_over:
                self.enemy_manager.update_turn()
                self._check_game_over()

                if self.enemy_manager.turn_state == "finished":
                    # 各敵の行動実行フェーズ
                    for enemy in self.enemy_manager.enemies:
                        if not enemy.is_alive: # 倒れている敵は行動しない
                            continue

                        action_id = enemy.decide_next_action() # 次の行動を決定 (next_actionに格納される)
                        action_data = MONSTER_ACTIONS.get(action_id, {})

                        # 会話イベントの検出
                        is_conversation_action = False
                        for effect in action_data.get("effects", []):
                            if effect.get("type") == "conversation_event":
                                conversation_id = effect["conversation_id"]
                                self.current_scene = ConversationScene(self.player, conversation_id, self.return_from_conversation)
                                is_conversation_action = True
                                break
                        
                        if is_conversation_action:
                            # 会話イベントが発生したら、それ以上の敵の行動は処理せず、会話シーンに遷移する
                            # プレイヤーの防御値リセットやターン終了処理はreturn_from_conversationで行われる
                            return 

                        # 会話イベントでなければ通常行動を実行
                        # targetsはActionHandlerで決定されるため、ここでenemy.targetsを設定する必要はない
                        ActionHandler.execute_monster_action(enemy, [self.player], action_id) # 常にプレイヤーをターゲットとする
                        
                        # 行動後の状態異常のデクリメントなどはActionHandler内で処理されるべきだが、
                        # 現在はここに書かれているので残す。ただし、会話イベントの場合は既にreturnしている
                        if not self.game_over:
                            enemy.decrement_status_effects()
                    
                    # すべての敵の行動が終わり、会話イベントも発生しなかった場合
                    # プレイヤーの防御値をリセット
                    self.onEnemyTurnEnd()

        else: # 会話シーンがアクティブな場合
            self.current_scene.update_state()
            # 会話シーンが終了したかチェック
            if self.current_scene.is_finished:
                # 会話シーンからバトルシーンに戻る
                self.current_scene = self
                # 会話の結果に基づいてバトルシーンの状態を更新する必要がある場合はここで行う
                # 現時点では何もしないが、将来的にconversation_scene.resultなどを利用する可能性

    def return_from_conversation(self, result: dict | None = None):
        """会話シーンから戻ってきた際に呼び出されるコールバック"""
        self.current_scene = self # バトルシーンに制御を戻す
        # result には会話シーンでの選択結果などが含まれる可能性がある
        # ここで会話の結果に基づいてバトルシーンに影響を与える処理を行う
        if result and "effects" in result:
            # 会話の選択結果に応じたエフェクトを適用
            # ActionHandler を利用してエフェクトを適用する
            # ただし、ActionHandler は player action を想定しているので、
            # monster action の effect を適用できるように修正が必要かもしれない
            print(f"Applying conversation effects: {result['effects']}")
            for effect in result["effects"]:
                targets = [self.player] # 常にプレイヤーが対象

                # ActionHandler._process_effect を呼び出して効果を適用
                # 会話の結果のエフェクトには特定のsource（攻撃元）がないため、
                # ここでは便宜的にプレイヤー自身をsourceとして渡す（後で調整の余地あり）
                ActionHandler._process_effect(self.player, targets, effect)
            self._check_game_over() # 会話イベントの結果でゲームオーバーになる可能性があるのでチェック
        
        # 会話が終了したので敵のターン状態を進める
        # これがないと会話の後に敵のターンが再度開始されてしまう
        self.onEnemyTurnEnd()
        
    def onEnemyTurnEnd(self):
        """敵のターン終了時に呼び出されるコールバック"""
        self.player.defense_buff = 0 # プレイヤーの防御値をリセット
        self.turn = "player"
        self.deck_manager.draw_cards(5)
        self.player.fully_recover_mana()