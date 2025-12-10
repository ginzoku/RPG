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
        self.background_image = None
        self.current_scene = self # BattleScene自身を初期シーンとして設定
        self.reset("conversation_test_group") # デフォルトの敵グループで初期化

    def reset(self, enemy_group_id: str):
        # 背景の読み込み
        enemy_group_data = ENEMY_GROUPS.get(enemy_group_id, {})
        background_path = enemy_group_data.get("background")
        if background_path:
            try:
                self.background_image = pygame.image.load(background_path).convert()
                self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading battle background image {background_path}: {e}")
                self.background_image = None
        else:
            self.background_image = None

        # 敵の初期化
        self.enemy_manager = EnemyManager(self.player, self)
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
        self.turn_count: int = 0 # ターンカウンター
        self.showing_deck_viewer: bool = False  # 山札ビュー表示フラグ
        self.hovered_deck_card: tuple | None = None  # ホバーされている山札カード情報
        self.deck_viewer_drawer = None  # BattleViewで初期化される
        self.discovery_card_rects: list[tuple[pygame.Rect, str]] = [] # 発見カードのRectとID
        
        # プレイヤーの戦闘開始時の状態リセット
        self.player.reset_for_battle(self.enemy_manager.enemies)
        self.deck_manager = DeckManager()
        self.deck_manager.draw_cards(5)

        # バトル開始時に一番左の敵をデフォルトターゲットに設定
        first_living_enemy_index = next((i for i, e in enumerate(self.enemy_manager.enemies) if e.is_alive), None)
        self.targeted_enemy_index = first_living_enemy_index

    def set_discovery_card_rects(self, rects: list[tuple[pygame.Rect, str]]):
        """Viewから発見カードのRect情報を受け取る"""
        self.discovery_card_rects = rects

    def _check_game_over(self):
        was_game_over = self.game_over # チェック前の状態を保存

        if all(not enemy.is_alive for enemy in self.enemy_manager.enemies):
            if not was_game_over: # ゲームオーバーになった瞬間のみ実行
                self.reward_gold = sum(enemy.gold for enemy in self.enemy_manager.enemies)
                self.player.gold += self.reward_gold
            self.game_over = True
            self.winner = "player"

        if not self.player.is_alive:
            self.game_over = True
            self.winner = "enemy"
            
        # ゲームオーバー状態に移行した瞬間に一度だけカードを削除する
        if self.game_over and not was_game_over:
            self.deck_manager.remove_temporary_cards()

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
            self.player.process_turn_end_relic_effects(self.enemy_manager.enemies) # プレイヤーのターン終了時のレリック効果を処理
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
        if self.deck_manager and self.deck_manager.is_discovering:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    for rect, card_id in self.discovery_card_rects:
                        if rect.collidepoint(event.pos):
                            self.deck_manager.add_discovered_card_to_hand(card_id)
                            self.discovery_card_rects = [] # 選択後はクリア
                            break # 複数のカードを同時にクリックしないように
            return # ディスカバリー中は他の入力を無視

        if self.current_scene == self: # バトルシーンがアクティブな場合
            self.input_handler.process_event(event)
        else: # 会話シーンがアクティブな場合
            self.current_scene.process_input(event)

    def update_state(self):
        # サブシーン（会話など）がアクティブな場合は、そちらのupdateを呼ぶ
        if self.current_scene != self:
            self.current_scene.update_state()
            return

        if self.turn == "enemy" and not self.game_over:
            self.enemy_manager.update_turn()
            self._check_game_over()

            if self.enemy_manager.turn_state == "finished":
                # 敵のターン終了処理
                for enemy in self.enemy_manager.enemies:
                    # 敵の行動決定とターゲット設定
                    action_id = enemy.decide_next_action()
                    action_data = MONSTER_ACTIONS.get(action_id, {})
                    first_effect = action_data.get("effects", [{}])[0]
                    target_scope = first_effect.get("target_scope")
                    if target_scope == "all":
                        enemy.targets = [self.player] # 将来的に味方が増える場合はリストにする
                    else: # single, self
                        enemy.targets = [self.player]
                    if not self.game_over:
                        enemy.decrement_status_effects()
                
                # プレイヤーの防御値をリセット
                self.player.defense_buff = 0
                
                # ターンカウンターをインクリメント
                self.turn_count += 1
                
                # プレイヤーのターン開始時のレリック効果を処理
                self.player.process_turn_start_relic_effects()
                self.player.process_timed_relic_effects(self.turn_count)
                self._check_game_over() # レリックの効果で死ぬ可能性
                if self.game_over: return # ゲームオーバーなら即時終了
                
                self.turn = "player"
                self.deck_manager.draw_cards(5)
                self.player.fully_recover_mana()

    def start_conversation(self, conversation_id: str):
        self.current_scene = ConversationScene(self.player, conversation_id, self.return_from_conversation)

    def return_from_conversation(self, result: dict | None = None):
        """会話シーンから戻ってきた際に呼び出されるコールバック"""
        self.current_scene = self # バトルシーンに制御を戻す
        self.enemy_manager.advance_to_next_enemy() # 会話が終わったので、次の敵の行動に進める
        # # result には会話シーンでの選択結果などが含まれる可能性がある
        # # ここで会話の結果に基づいてバトルシーンに影響を与える処理を行う
        # if result and "effects" in result:
        #     # 会話の選択結果に応じたエフェクトを適用
        #     # ActionHandler を利用してエフェクトを適用する
        #     # ただし、ActionHandler は player action を想定しているので、
        #     # monster action の effect を適用できるように修正が必要かもしれない
        #     print(f"Applying conversation effects: {result['effects']}")
        #     for effect in result["effects"]:
        #         targets = [self.player] # 常にプレイヤーが対象

        #         # ActionHandler._process_effect を呼び出して効果を適用
        #         # 会話の結果のエフェクトには特定のsource（攻撃元）がないため、
        #         # ここでは便宜的にプレイヤー自身をsourceとして渡す（後で調整の余地あり）
        #         ActionHandler._process_effect(self.player, targets, effect)
        #     self._check_game_over() # 会話イベントの結果でゲームオーバーになる可能性があるのでチェック
        
        # # 会話が終了したので敵のターン状態を進める
        # # これがないと会話の後に敵のターンが再度開始されてしまう
        # self.onEnemyTurnEnd()
        
    def onEnemyTurnEnd(self):
        """敵のターン終了時に呼び出されるコールバック"""
        self.player.defense_buff = 0 # プレイヤーの防御値をリセット
        self.turn = "player"
        self.deck_manager.draw_cards(5)
        self.player.fully_recover_mana()