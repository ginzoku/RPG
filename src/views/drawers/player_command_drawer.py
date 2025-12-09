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

    def draw(self, screen: pygame.Surface, battle_state: BattleScene, command_area_rect: pygame.Rect):
        # --- 新しいレイアウトロジック ---
        cards = battle_state.deck_manager.hand
        num_commands = len(cards)
        if num_commands == 0:
            return

        # --- カードサイズの相対的な定義 ---
        card_height = int(command_area_rect.height * 0.95)
        card_width = int(card_height * 0.7)  # 縦横比を固定
        overlap_x = int(card_width * 0.65)   # カードの重なり具合
        hover_lift = int(card_height * 0.2)  # ホバー時の浮き上がり量

        total_width = (num_commands - 1) * overlap_x + card_width
        start_x = (screen.get_width() - total_width) / 2
        card_y = screen.get_height() - card_height - int(command_area_rect.height * 0.05)

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
            hover_y = card_y - hover_lift # 少し上に表示
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

        # 廃棄カードの特別な表示
        if action.get("exhaust", False):
            card_border_color = settings.YELLOW # 例えば黄色に

        pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=5)
        pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=5)

        # アクション名
        name_text = self.fonts["small"].render(action["name"], True, text_color)
        name_rect = name_text.get_rect(center=card_rect.center)
        screen.blit(name_text, name_rect)

        # 左上: 消費MP
        cost = action.get("cost", 0)
        if cost >= 0:
            cost_circle_radius = int(card_rect.width * 0.15)
            cost_circle_center = (card_rect.left + cost_circle_radius + 5, card_rect.top + cost_circle_radius + 5)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 1)
            cost_text = self.fonts["card"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値の表示
        power = ActionHandler.get_card_display_power(battle_state.player, action_id)
        if power is not None:
            effect_type = action.get("effects", [{}])[0].get("type")
            hits = action.get("effects", [{}])[0].get("hits", 1)
            color = settings.BLUE
            if effect_type == "damage": color = settings.RED
            power_circle_radius = int(card_rect.width * 0.15)
            self._draw_power_circle(screen, power, card_rect, color, power_circle_radius, hits=hits)

    def _draw_power_circle(self, screen: pygame.Surface, power: int, card_rect: pygame.Rect, color: tuple, power_circle_radius: int, hits: int = 1):
        power_circle_center = (card_rect.right - power_circle_radius - 5, card_rect.bottom - power_circle_radius - 5)
        pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
        pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 1)
        
        display_text = str(power)
        font = self.fonts["card"]
        if hits > 1:
            display_text = f"{power}x{hits}"
            if len(display_text) > 3:
                font = self.fonts["small"]

        power_text = font.render(display_text, True, settings.WHITE)
        power_text_rect = power_text.get_rect(center=power_circle_center)
        screen.blit(power_text, power_text_rect)

    def _draw_enlarged_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str):
        action = ACTIONS[action_id]
        
        # --- 拡大カードサイズの相対的な定義 ---
        card_height = int(screen.get_height() * 0.6)
        card_width = int(card_height * 0.7)
        card_x = (screen.get_width() - card_width) / 2
        card_y = (screen.get_height() - card_height) / 2 - int(screen.get_height() * 0.05)
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # 背景と枠線
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        card_border_color = settings.WHITE
        if action.get("exhaust", False):
            card_border_color = settings.YELLOW # 例えば黄色に
        pygame.draw.rect(screen, card_border_color, card_rect, 3, border_radius=10)

        # アクション名
        cost_circle_radius = int(card_width * 0.12)
        cost_area_right_edge = card_rect.left + (cost_circle_radius * 2) + 20
        name_area_center_x = cost_area_right_edge + (card_rect.right - cost_area_right_edge) / 2

        name_text = self.fonts["small"].render(action["name"], True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=name_area_center_x, y=card_rect.top + 20)
        screen.blit(name_text, name_rect)

        # 説明文
        power_for_desc = ""
        if action.get("effects"): power_for_desc = action["effects"][0].get("power", "")
        description = action.get("description", "").format(power=power_for_desc)
        description_rect = pygame.Rect(card_rect.x + 20, name_rect.bottom + 10, card_rect.width - 40, card_rect.height - name_rect.height - 80)
        self._draw_text_multiline(screen, description, self.fonts["card"], description_rect, settings.WHITE)

        # 左上: 消費MP
        cost = action.get("cost", 0)
        if cost >= 0:
            cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
            cost_text = self.fonts["small"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値
        power = ActionHandler.get_card_display_power(battle_state.player, action_id)
        if power is not None:
            effect_type = action.get("effects", [{}])[0].get("type")
            hits = action.get("effects", [{}])[0].get("hits", 1)
            color = settings.BLUE
            if effect_type == "damage": color = settings.RED
            power_circle_radius = int(card_width * 0.12)
            self._draw_power_circle(screen, power, card_rect, color, power_circle_radius, hits=hits)

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