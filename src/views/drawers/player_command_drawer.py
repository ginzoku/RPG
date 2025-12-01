# -*- coding: utf-8 -*-
import pygame
import math
from ...scenes.battle_scene import BattleScene
from ...config import settings
from ...data.action_data import ACTIONS
from ...components.action_handler import ActionHandler
from ...data.status_effect_data import STATUS_EFFECTS

class PlayerCommandDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts

    def draw(self, screen: pygame.Surface, battle_state: BattleScene, log_area_rect: pygame.Rect):
        # --- 新しいレイアウトロジック ---
        cards = battle_state.deck_manager.hand
        num_commands = len(cards)
        if num_commands == 0:
            return

        card_width = 120
        card_height = 170
        overlap_x = 80  # カードが重なる量を減らし、間隔を広げる
        
        total_width = (num_commands - 1) * overlap_x + card_width
        start_x = (screen.get_width() - total_width) / 2
        card_y = screen.get_height() - card_height - 10

        # ホバーされていないカードを先に描画
        for i, action_id in enumerate(cards):
            if i == battle_state.hovered_card_index:
                continue # ホバーされているカードは後で描画
            
            current_card_x = start_x + i * overlap_x
            card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)
            self._draw_single_card(screen, battle_state, action_id, card_rect, i)
        
        # ホバーされているカードを最後に（一番手前に）描画
        if battle_state.hovered_card_index is not None:
            i = battle_state.hovered_card_index
            action_id = cards[i]
            hover_y = card_y - 30 # 少し上に表示
            current_card_x = start_x + i * overlap_x
            card_rect = pygame.Rect(current_card_x, hover_y, card_width, card_height)
            self._draw_single_card(screen, battle_state, action_id, card_rect, i)
        
        # --- 拡大カードの描画 ---
        if battle_state.hovered_card_index is not None:
            action_id = cards[battle_state.hovered_card_index]
            self._draw_enlarged_card(screen, battle_state, action_id)


    def _draw_single_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str, card_rect: pygame.Rect, card_index: int):
        action = ACTIONS[action_id]
        can_afford = battle_state.player.current_mana >= action.get("cost", 0)

        if not can_afford:
            card_bg_color, card_border_color, text_color = ((20, 20, 30), (80, 80, 80), settings.DARK_GRAY)
        else:
            card_bg_color, card_border_color, text_color = ((40, 40, 60), settings.WHITE, settings.LIGHT_BLUE)

        pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=5)
        pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=5)

        # アクション名
        name_text = self.fonts["small"].render(action["name"], True, text_color)
        name_rect = name_text.get_rect(center=card_rect.center)
        screen.blit(name_text, name_rect)

        # 左上: 消費MP
        cost = action.get("cost", 0)
        if cost >= 0:
            cost_circle_radius = 16
            cost_circle_center = (card_rect.left + cost_circle_radius + 5, card_rect.top + cost_circle_radius + 5)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 1)
            cost_text = self.fonts["card"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値の表示
        power = ActionHandler.get_card_display_power(battle_state.player, action_id)
        if power is not None:
            color = settings.RED if action["type"] == "attack" else settings.BLUE
            self._draw_power_circle(screen, power, card_rect, color)

    def _draw_power_circle(self, screen: pygame.Surface, power: int, card_rect: pygame.Rect, color: tuple, power_circle_radius: int = 16):
        power_circle_center = (card_rect.right - power_circle_radius - 5, card_rect.bottom - power_circle_radius - 5)
        pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
        pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 1)
        power_text = self.fonts["card"].render(str(power), True, settings.WHITE)
        power_text_rect = power_text.get_rect(center=power_circle_center)
        screen.blit(power_text, power_text_rect)

    def _draw_enlarged_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str):
        action = ACTIONS[action_id]
        
        card_width = 240
        card_height = 340
        card_x = (screen.get_width() - card_width) / 2
        card_y = (screen.get_height() - card_height) / 2 - 50
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # 背景と枠線
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        pygame.draw.rect(screen, settings.WHITE, card_rect, 3, border_radius=10)

        # アクション名
        # MPコスト表示エリアを除いたカードの中央に配置する
        cost_circle_radius = 24
        cost_area_right_edge = card_rect.left + (cost_circle_radius * 2) + 20 # コスト円の右端+余白
        name_area_center_x = cost_area_right_edge + (card_rect.right - cost_area_right_edge) / 2

        name_text = self.fonts["small"].render(action["name"], True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=name_area_center_x, y=card_rect.top + 20)
        screen.blit(name_text, name_rect)

        # 説明文
        description = action.get("description", "").format(power=action.get("power", ""))
        # 説明文の描画領域をアクション名の下に設定
        description_rect = pygame.Rect(card_rect.x + 20, name_rect.bottom + 10, card_rect.width - 40, card_rect.height - name_rect.height - 80)
        self._draw_text_multiline(screen, description, self.fonts["card"], description_rect, settings.WHITE)

        # 左上: 消費MP
        cost = action.get("cost", 0)
        if cost >= 0:
            cost_circle_radius = 24
            cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
            cost_text = self.fonts["small"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値
        power = ActionHandler.get_card_display_power(battle_state.player, action_id)
        if power is not None:
            color = settings.RED if action["type"] == "attack" else settings.BLUE
            self._draw_power_circle(screen, power, card_rect, color, 24)

    def _draw_text_multiline(self, surface, text, font, rect, color):
        """指定された矩形内にテキストを自動で折り返して描画する"""
        lines = text.splitlines()
        space_width = font.size(' ')[0]
        max_width, max_height = rect.size
        pos = list(rect.topleft)
        for line in lines:
            words = line.split(' ')
            for word in line:
                word_surface = font.render(word, True, color)
                word_width, word_height = word_surface.get_size()
                if pos[0] + word_width >= rect.right:
                    pos[0] = rect.left
                    pos[1] += word_height
                surface.blit(word_surface, pos)
                pos[0] += word_width + space_width
            pos[0] = rect.left
            pos[1] += word_height

    def _draw_power_circle(self, screen: pygame.Surface, power: int, card_rect: pygame.Rect, color: tuple, power_circle_radius: int = 16):
        power_circle_center = (card_rect.right - power_circle_radius - 5, card_rect.bottom - power_circle_radius - 5)
        pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
        pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 1)
        power_text = self.fonts["card"].render(str(power), True, settings.WHITE)
        power_text_rect = power_text.get_rect(center=power_circle_center)
        screen.blit(power_text, power_text_rect)

    def _draw_enlarged_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str):
        action = ACTIONS[action_id]
        
        card_width = 240
        card_height = 340
        card_x = (screen.get_width() - card_width) / 2
        card_y = (screen.get_height() - card_height) / 2 - 50
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # 背景と枠線
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        pygame.draw.rect(screen, settings.WHITE, card_rect, 3, border_radius=10)

        # アクション名
        # MPコスト表示エリアを除いたカードの中央に配置する
        cost_circle_radius = 24
        cost_area_right_edge = card_rect.left + (cost_circle_radius * 2) + 20 # コスト円の右端+余白
        name_area_center_x = cost_area_right_edge + (card_rect.right - cost_area_right_edge) / 2

        name_text = self.fonts["small"].render(action["name"], True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=name_area_center_x, y=card_rect.top + 20)
        screen.blit(name_text, name_rect)

        # 説明文
        description = action.get("description", "").format(power=action.get("power", ""))
        # 説明文の描画領域をアクション名の下に設定
        description_rect = pygame.Rect(card_rect.x + 20, name_rect.bottom + 10, card_rect.width - 40, card_rect.height - name_rect.height - 80)
        self._draw_text_multiline(screen, description, self.fonts["card"], description_rect, settings.WHITE)

        # 左上: 消費MP
        cost = action.get("cost", 0)
        if cost >= 0:
            cost_circle_radius = 24
            cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
            cost_text = self.fonts["small"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値
        if action["type"] == "attack":
            base_power = action.get("power", 0)
            if action.get("damage_type") == "physical":
                base_power += battle_state.player.attack_power # attack_powerを威力表示に加算
            if "weak" in battle_state.player.status_effects:
                base_power = math.ceil(base_power * STATUS_EFFECTS["weak"]["value"])
            if base_power > 0:
                self._draw_power_circle(screen, base_power, card_rect, settings.RED, 24)
        elif action_id == "guard":
            power = action.get("power", 0)
            self._draw_power_circle(screen, power, card_rect, settings.BLUE, 24)

    def _draw_text_multiline(self, surface, text, font, rect, color):
        """指定された矩形内にテキストを自動で折り返して描画する"""
        lines = text.splitlines()
        space_width = font.size(' ')[0]
        max_width, max_height = rect.size
        pos = list(rect.topleft)
        for line in lines:
            words = line.split(' ')
            for word in line:
                word_surface = font.render(word, True, color)
                word_width, word_height = word_surface.get_size()
                if pos[0] + word_width >= rect.right:
                    pos[0] = rect.left
                    pos[1] += word_height
                surface.blit(word_surface, pos)
                pos[0] += word_width + space_width
            pos[0] = rect.left
            pos[1] += word_height