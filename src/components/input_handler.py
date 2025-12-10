# -*- coding: utf-8 -*-
import pygame
import math
from typing import TYPE_CHECKING

from ..config import settings
from ..data.action_data import ACTIONS

if TYPE_CHECKING:
    from ..scenes.battle_scene import BattleScene

class InputHandler:
    def __init__(self, battle_scene: "BattleScene"):
        self.scene = battle_scene

    def process_event(self, event: pygame.event.Event):
        """イベントを処理し、適切なハンドラに振り分ける"""
        if self.scene.game_over: return

        # 山札ビュー表示中の場合
        if self.scene.showing_deck_viewer:
            # DeckViewerDrawer がまだ BattleView によって割り当てられていない可能性があるため安全に参照する
            dv = getattr(self.scene, 'deck_viewer_drawer', None)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    self.scene.showing_deck_viewer = False  # 閉じる
                elif event.button == 4:  # マウスホイール上
                    if dv and hasattr(dv, 'update_scroll'):
                        dv.update_scroll(self.scene.deck_manager.deck, -20)
                elif event.button == 5:  # マウスホイール下
                    if dv and hasattr(dv, 'update_scroll'):
                        dv.update_scroll(self.scene.deck_manager.deck, 20)
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
        self.scene.hovered_card_index = None
        self.scene.hovered_relic_index = None
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
                    action = ACTIONS[action_id]
                    can_afford = self.scene.player.current_mana >= action.get("cost", 0)
                    if can_afford:
                        self.scene.hovered_card_index = i
                    return

    def _handle_mouse_click(self, pos: tuple[int, int]):
        """マウスクリックイベントを処理し、シーンの状態を更新する"""
        # 山札のクリック判定（ゲーム画面の左下辺り）
        deck_rect = pygame.Rect(10, settings.SCREEN_HEIGHT - 120, 150, 110)
        if deck_rect.collidepoint(pos):
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
                self.scene.execute_card_action(i)
                return