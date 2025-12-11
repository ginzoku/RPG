# -*- coding: utf-8 -*-
import pygame
import math
from typing import TYPE_CHECKING

from ..config import settings
from ..data.action_data import ACTIONS
from .action_handler import ActionHandler
from ..data.unique_data import DEFAULT_UNIQUE_ID

if TYPE_CHECKING:
    from ..scenes.battle_scene import BattleScene

class InputHandler:
    def __init__(self, battle_scene: "BattleScene"):
        self.scene = battle_scene

    def process_event(self, event: pygame.event.Event):
        """イベントを処理し、適切なハンドラに振り分ける"""
        if self.scene.game_over: return

        # 山札／捨て札ビュー表示中の場合
        if self.scene.showing_deck_viewer or getattr(self.scene, 'showing_discard_viewer', False):
            # DeckViewerDrawer がまだ BattleView によって割り当てられていない可能性があるため安全に参照する
            dv = getattr(self.scene, 'deck_viewer_drawer', None)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    # 左クリックで表示を閉じる（どちらのビューも閉じる）
                    self.scene.showing_deck_viewer = False
                    if hasattr(self.scene, 'showing_discard_viewer'):
                        self.scene.showing_discard_viewer = False
                elif event.button == 4:  # マウスホイール上
                    if dv and hasattr(dv, 'update_scroll'):
                        cards = self.scene.deck_manager.discard_pile if getattr(self.scene, 'showing_discard_viewer', False) else self.scene.deck_manager.deck
                        dv.update_scroll(cards, -20)
                elif event.button == 5:  # マウスホイール下
                    if dv and hasattr(dv, 'update_scroll'):
                        cards = self.scene.deck_manager.discard_pile if getattr(self.scene, 'showing_discard_viewer', False) else self.scene.deck_manager.deck
                        dv.update_scroll(cards, 20)
            elif event.type == pygame.MOUSEMOTION:
                # ホバーカード情報を更新（DeckViewerDrawerで検出）
                if dv and hasattr(dv, 'get_hovered_card'):
                    hovered = dv.get_hovered_card(event.pos)
                    self.scene.hovered_deck_card = hovered
                else:
                    self.scene.hovered_deck_card = None
            return

        if self.scene.turn != "player":
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(event.pos)

    def _handle_mouse_motion(self, pos: tuple[int, int]):
        """マウス移動イベントを処理し、ホバー状態を更新する"""
        # clear hover flags
        self.scene.hovered_card_index = None
        self.scene.hovered_relic_index = None
        self.scene.hovered_unique = False
        for enemy in self.scene.enemy_manager.enemies:
            enemy.is_targeted = False

        # レリックのホバー判定
        relic_radius = 15
        relic_gap = 10
        for i, relic_id in enumerate(self.scene.player.relics):
            x = relic_gap + i * (relic_radius * 2 + relic_gap)
            y = relic_gap
            relic_rect = pygame.Rect(x, y, relic_radius * 2, relic_radius * 2)
            if relic_rect.collidepoint(pos):
                self.scene.hovered_relic_index = i
                return

        # 敵のホバー判定
        for i, enemy in enumerate(self.scene.enemy_manager.enemies):
            if enemy.is_alive:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 80, 100)
                if enemy_rect.collidepoint(pos):
                    enemy.is_targeted = True
                    return

        # 山札上のユニークボタンのホバー判定
        deck_top_btn = getattr(self.scene, 'deck_top_button_rect', None)
        if deck_top_btn and deck_top_btn.collidepoint(pos):
            self.scene.hovered_unique = True
            return

        # カードのホバー判定
        num_commands = len(self.scene.deck_manager.hand)
        if num_commands > 0:
            card_width, card_height = 120, 170
            overlap_x = 80
            total_width = (num_commands - 1) * overlap_x + card_width
            start_x = (settings.SCREEN_WIDTH - total_width) / 2
            card_y = settings.SCREEN_HEIGHT - card_height - 10

            for i in range(num_commands - 1, -1, -1):
                current_card_x = start_x + i * overlap_x
                card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)
                if self.scene.hovered_card_index == i:
                    card_rect.y -= 30

                if card_rect.collidepoint(pos):
                    action_id = self.scene.deck_manager.hand[i]
                    # unplayable 属性があってもホバーは可能にする（グレー表示はしない）
                    self.scene.hovered_card_index = i
                    return

    def _handle_mouse_click(self, pos: tuple[int, int]):
        """マウスクリックイベントを処理し、シーンの状態を更新する"""
        # 山札のクリック判定（ゲーム画面の左下辺り）
        # Use BattleScene-provided indicator rects if available (set by BattleView)
        # 先に山札上の丸ボタン領域をチェック（優先）
        deck_top_btn = getattr(self.scene, 'deck_top_button_rect', None)
        if deck_top_btn and deck_top_btn.collidepoint(pos):
            # 現在選択されているユニーク（battle_scene.current_unique_id）を優先して発動
            unique_id = getattr(self.scene, 'current_unique_id', DEFAULT_UNIQUE_ID)
            # BattleScene に use_unique API を実装している前提
            if hasattr(self.scene, 'use_unique'):
                ok = self.scene.use_unique(unique_id)
                if not ok:
                    # use_unique 側で適切なメッセージを表示する
                    pass
            else:
                # フォールバック: 直接斬りつけを実行（従来互換）
                action_id = 'slash'
                effective_id = action_id
                if hasattr(self.scene.deck_manager, 'get_effective_card_id'):
                    effective_id = self.scene.deck_manager.get_effective_card_id(action_id)
                action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))
                cost = action.get('cost', 0)
                if self.scene.player.current_mana < cost:
                    if hasattr(self.scene, 'show_message'):
                        self.scene.show_message('マナが足りない！', duration=1.2)
                    else:
                        print(f"DEBUG: Not enough mana for {action_id}")
                    return
                # determine targets and execute
                first_effect = action.get('effects', [{}])[0]
                target_scope = first_effect.get('target_scope')
                targets = []
                if target_scope == 'self':
                    targets = [self.scene.player]
                elif target_scope == 'single':
                    if self.scene.targeted_enemy_index is not None and self.scene.enemy_manager.enemies[self.scene.targeted_enemy_index].is_alive:
                        targets = [self.scene.enemy_manager.enemies[self.scene.targeted_enemy_index]]
                elif target_scope == 'all':
                    targets = [enemy for enemy in self.scene.enemy_manager.enemies if enemy.is_alive]
                if not targets and target_scope not in ['self', None]:
                    return
                ActionHandler.execute_player_action(self.scene.player, targets, effective_id, self.scene.deck_manager, self.scene)
                try:
                    self.scene._update_target_after_enemy_death()
                    self.scene._check_game_over()
                except Exception:
                    pass
            return

        deck_rect = getattr(self.scene, 'deck_indicator_rect', None)
        discard_rect = getattr(self.scene, 'discard_indicator_rect', None)
        if deck_rect and deck_rect.collidepoint(pos):
            self.scene.showing_deck_viewer = True
            return
        if discard_rect and discard_rect.collidepoint(pos):
            # open discard viewer
            if hasattr(self.scene, 'showing_discard_viewer'):
                self.scene.showing_discard_viewer = True
            else:
                self.scene.showing_deck_viewer = True
            return
        
        # ターン終了ボタンのクリック判定
        log_area_y = settings.SCREEN_HEIGHT - int(settings.SCREEN_HEIGHT / 4)
        button_width, button_height = 120, 40
        button_x = settings.SCREEN_WIDTH - button_width - 150
        button_y = log_area_y - button_height - 10
        end_turn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        if end_turn_button_rect.collidepoint(pos):
            self.scene.end_player_turn()
            return

        # 敵のクリック判定
        for i, enemy in enumerate(self.scene.enemy_manager.enemies):
            if enemy.is_alive:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 80, 100)
                if enemy_rect.collidepoint(pos):
                    self.scene.set_target(i)
                    return

        # カードのクリック判定
        if self.scene.hovered_card_index is not None:
            # ホバーされているカードがクリックされたか再確認
            num_commands = len(self.scene.deck_manager.hand)
            card_width, card_height = 120, 170
            overlap_x = 80
            total_width = (num_commands - 1) * overlap_x + card_width
            start_x = (settings.SCREEN_WIDTH - total_width) / 2
            card_y = settings.SCREEN_HEIGHT - card_height - 10 - 30 # ホバー時のY座標
            
            i = self.scene.hovered_card_index
            current_card_x = start_x + i * overlap_x
            card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)

            if card_rect.collidepoint(pos):
                # If we're awaiting an exhaust choice (after discard choose), resolve it first
                if hasattr(self.scene.deck_manager, 'awaiting_exhaust_choice') and self.scene.deck_manager.awaiting_exhaust_choice:
                    resolved = self.scene.deck_manager.resolve_exhaust_choice(i)
                    if not resolved:
                        print('DEBUG: exhaust choice resolution failed')
                    return

                # If we're awaiting a discard choice (from an effect), resolve it here
                if hasattr(self.scene.deck_manager, 'awaiting_discard_choice') and self.scene.deck_manager.awaiting_discard_choice:
                    # resolve selection (InputHandler receives index i)
                    resolved = self.scene.deck_manager.resolve_discard_choice(i)
                    if not resolved:
                        print('DEBUG: discard choice resolution failed')
                    return

                # クリック時は unplayable 属性を持つカードを無効化する
                action_id = self.scene.deck_manager.hand[i]
                action = ACTIONS.get(action_id, {})
                if action.get("unplayable", False):
                    # 使用不可カード: 何もしない（将来的にメッセージ表示等を追加可能）
                    print(f"DEBUG: Tried to click unplayable card {action_id}")
                    return
                # マナが足りない場合は実行しない
                if self.scene.player.current_mana < action.get("cost", 0):
                    # 画面上にメッセージを出す（BattleScene.show_message を使う）
                    if hasattr(self.scene, 'show_message'):
                        self.scene.show_message("マナが足りない！", duration=1.2)
                    else:
                        print(f"DEBUG: Not enough mana to play {action_id}")
                    return

                self.scene.execute_card_action(i)
                return