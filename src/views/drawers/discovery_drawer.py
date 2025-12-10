# -*- coding: utf-8 -*-
import pygame
from ...config import settings
from ...data.action_data import ACTIONS
from ...components.action_handler import ActionHandler

class DiscoveryDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.card_rects = []

    def draw(self, screen: pygame.Surface, discovered_cards: list[dict], player_for_power) -> list[tuple[pygame.Rect, str]]:
        """
        発見カード選択画面を描画し、各カードのRectとIDのリストを返す。
        """
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_text = self.fonts["large"].render("カードを選択", True, settings.YELLOW)
        title_rect = title_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)

        self.card_rects.clear()
        
        num_cards = len(discovered_cards)
        card_width = 180
        card_height = 240
        gap = 30
        total_width = num_cards * card_width + (num_cards - 1) * gap
        start_x = (settings.SCREEN_WIDTH - total_width) // 2
        center_y = settings.SCREEN_HEIGHT // 2

        for i, card_data in enumerate(discovered_cards):
            card_id = card_data["id"]
            card_x = start_x + i * (card_width + gap)
            card_y = center_y - card_height // 2
            
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.card_rects.append((card_rect, card_id))

            # カードの描画
            can_afford = getattr(player_for_power, 'current_mana', 0) >= card_data.get("cost", 0)
            card_bg_color = (40, 40, 60) if can_afford else (20, 20, 30)
            card_border_color = settings.WHITE if can_afford else (80, 80, 80)
            text_color = settings.LIGHT_BLUE if can_afford else settings.DARK_GRAY

            pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=10)

            # カード名
            name_text = self.fonts["medium"].render(card_data.get("name", card_id), True, settings.WHITE)
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.top + 30))
            screen.blit(name_text, name_rect)

            # コスト
            cost = card_data.get("cost", 0)
            cost_circle_radius = 15
            cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
            pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
            cost_text = self.fonts["card"].render(str(cost), True, settings.WHITE)
            cost_text_rect = cost_text.get_rect(center=cost_circle_center)
            screen.blit(cost_text, cost_text_rect)

            # 説明
            description = card_data.get("description", "")
            desc_lines = description.split("\n")
            desc_y = card_rect.centery - 20
            for line in desc_lines:
                desc_text = self.fonts["small"].render(line, True, settings.WHITE)
                desc_rect = desc_text.get_rect(center=(card_rect.centerx, desc_y))
                screen.blit(desc_text, desc_rect)
                desc_y += 22

        return self.card_rects
