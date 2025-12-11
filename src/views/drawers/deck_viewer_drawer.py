"""Deck viewer drawer - clean implementation

Displays deck cards in a grid (5 per row), allows vertical scrolling and
shows a centered overlay with card details on hover. Works even when the
deck is empty (displays a message) so clicking the deck always shows a
visible UI.
"""

import pygame
from ...config import settings
from ...data.action_data import ACTIONS
from ...components.action_handler import ActionHandler


class DeckViewerDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.card_rects = []
        self.scroll_offset = 0
        self.cards_per_row = 5
        self.card_height = 140
        self.card_gap_x = 10
        self.card_gap_y = 10
        self.viewport_height = 400

    def draw(self, screen: pygame.Surface, deck_cards: list[str], player_for_power, title: str = "山札確認") -> pygame.Rect:
        deck_cards = deck_cards or []
        # display cards in ID order regardless of current deck order
        display_cards = sorted(list(deck_cards))

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        window_width = 800
        window_height = 500
        window_rect = pygame.Rect(0, 0, window_width, window_height)
        window_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

        pygame.draw.rect(screen, (30, 30, 50), window_rect, border_radius=15)
        pygame.draw.rect(screen, settings.WHITE, window_rect, 3, border_radius=15)

        title_text = self.fonts["medium"].render(title, True, settings.YELLOW)
        screen.blit(title_text, (window_rect.left + 20, window_rect.top + 20))

        card_area_rect = pygame.Rect(window_rect.left + 20, window_rect.top + 60, window_rect.width - 40, window_rect.height - 120)
        self.viewport_height = card_area_rect.height

        # compute card width and gap to fill the area with cards_per_row cards
        available_width = card_area_rect.width
        max_card_w = 180
        min_card_w = 80
        calc_card_w = int(available_width / self.cards_per_row) - 6
        card_w = max(min(calc_card_w, max_card_w), min_card_w)
        if self.cards_per_row > 1:
            total_cards_w = card_w * self.cards_per_row
            remaining = max(0, available_width - total_cards_w)
            gap_x = int(remaining / (self.cards_per_row - 1))
            gap_x = max(gap_x, 6)
        else:
            gap_x = self.card_gap_x

        display_card_w = card_w
        display_card_h = self.card_height

        pygame.draw.rect(screen, (20, 20, 30), card_area_rect, border_radius=8)

        self.card_rects.clear()

        if len(display_cards) == 0:
            no_text = self.fonts["medium"].render("山札がありません", True, settings.WHITE)
            no_rect = no_text.get_rect(center=card_area_rect.center)
            screen.blit(no_text, no_rect)
        else:
            for i, card_id in enumerate(display_cards):
                card_data = ACTIONS.get(card_id, {})
                row = i // self.cards_per_row
                col = i % self.cards_per_row

                card_x = card_area_rect.left + col * (display_card_w + gap_x)
                card_y = card_area_rect.top + row * (display_card_h + self.card_gap_y) - self.scroll_offset

                card_rect = pygame.Rect(card_x, card_y, display_card_w, display_card_h)
                if card_rect.bottom < card_area_rect.top or card_rect.top > card_area_rect.bottom:
                    continue

                can_afford = getattr(player_for_power, 'current_mana', 0) >= card_data.get("cost", 0)
                if not can_afford:
                    card_bg_color = (20, 20, 30)
                    card_border_color = (80, 80, 80)
                    text_color = settings.DARK_GRAY
                else:
                    card_bg_color = (40, 40, 60)
                    card_border_color = settings.WHITE
                    text_color = settings.LIGHT_BLUE

                pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=6)
                pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=6)

                name_text = self.fonts["small"].render(card_data.get("name", card_id), True, text_color)
                name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.centery - 30))
                screen.blit(name_text, name_rect)

                # 消費MPは unplayable 属性のカードでは表示しない
                if not card_data.get("unplayable", False):
                    cost = card_data.get("cost", 0)
                    if cost >= 0:
                        cost_circle_radius = 12
                        cost_circle_center = (card_rect.left + cost_circle_radius + 6, card_rect.top + cost_circle_radius + 6)
                        pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
                        pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 1)
                        cost_text = self.fonts["card"].render(str(cost), True, settings.WHITE)
                        cost_text_rect = cost_text.get_rect(center=cost_circle_center)
                        screen.blit(cost_text, cost_text_rect)

                power = ActionHandler.get_card_display_power(player_for_power, card_id)
                if power is not None:
                    effect_type = card_data.get("effects", [{}])[0].get("type")
                    color = settings.BLUE
                    if effect_type == "damage":
                        color = settings.RED
                    power_circle_radius = 12
                    power_circle_center = (card_rect.right - power_circle_radius - 6, card_rect.bottom - power_circle_radius - 6)
                    pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
                    pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 1)
                    power_text = self.fonts["card"].render(str(power), True, settings.WHITE)
                    power_text_rect = power_text.get_rect(center=power_circle_center)
                    screen.blit(power_text, power_text_rect)

                self.card_rects.append((card_rect, card_id, card_data))

        # scrollbar
        self._draw_scrollbar(screen, card_area_rect, len(deck_cards), display_card_h, gap_x)

        # hover details
        if self.card_rects:
            mouse_pos = pygame.mouse.get_pos()
            hovered_card = self.get_hovered_card(mouse_pos)
            if hovered_card:
                card_id, card_data, card_rect = hovered_card
                self._draw_enlarged_card(screen, card_data, card_id, player_for_power, window_rect)

        # No explicit close button: viewer is closed by clicking anywhere (handled by InputHandler).
        # Return nothing.
        return None

    def _draw_scrollbar(self, screen: pygame.Surface, card_area_rect: pygame.Rect, total_cards: int, display_card_h: int, gap_x: int):
        scrollbar_width = 10
        scrollbar_rect = pygame.Rect(card_area_rect.right + 5, card_area_rect.top, scrollbar_width, card_area_rect.height)
        pygame.draw.rect(screen, (50, 50, 70), scrollbar_rect)

        rows = (total_cards + self.cards_per_row - 1) // self.cards_per_row
        content_height = rows * (display_card_h + self.card_gap_y) - self.card_gap_y
        max_scroll = max(0, content_height - self.viewport_height)

        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            thumb_height = max(20, int(scrollbar_rect.height * (self.viewport_height / max(1, content_height))))
            thumb_y = scrollbar_rect.top + int((scrollbar_rect.height - thumb_height) * scroll_ratio)
            thumb_rect = pygame.Rect(scrollbar_rect.left, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(screen, settings.LIGHT_BLUE, thumb_rect)

    def update_scroll(self, deck_cards: list[str], delta: int):
        rows = (len(deck_cards) + self.cards_per_row - 1) // self.cards_per_row
        content_height = rows * (self.card_height + self.card_gap_y) - self.card_gap_y
        max_scroll = max(0, content_height - self.viewport_height)
        self.scroll_offset = max(0, min(self.scroll_offset + delta, max_scroll))

    def get_hovered_card(self, mouse_pos: tuple[int, int]) -> tuple | None:
        for card_rect, card_id, card_data in self.card_rects:
            if card_rect.collidepoint(mouse_pos):
                return (card_id, card_data, card_rect)
        return None

    def _draw_enlarged_card(self, screen: pygame.Surface, card_data: dict, card_id: str, player_for_power, window_rect: pygame.Rect):
        detail_width = min(420, window_rect.width - 80)
        detail_height = min(340, window_rect.height - 80)
        detail_x = window_rect.centerx - detail_width // 2
        detail_y = window_rect.centery - detail_height // 2

        detail_rect = pygame.Rect(detail_x, detail_y, detail_width, detail_height)
        panel = pygame.Surface((detail_width, detail_height))
        panel.set_alpha(230)
        panel.fill((28, 28, 40))
        screen.blit(panel, (detail_x, detail_y))
        pygame.draw.rect(screen, settings.LIGHT_BLUE, detail_rect, 3, border_radius=10)

        card_name = card_data.get("name", card_id)
        name_text = self.fonts["medium"].render(card_name, True, settings.YELLOW)
        name_rect = name_text.get_rect(center=(detail_x + detail_width // 2, detail_y + 28))
        screen.blit(name_text, name_rect)

        # 詳細表示のコストは unplayable 属性のカードでは表示しない
        if not card_data.get("unplayable", False):
            cost = card_data.get("cost", 0)
            cost_text = self.fonts["small"].render(f"コスト: {cost}", True, settings.WHITE)
            screen.blit(cost_text, (detail_x + 20, detail_y + 64))

        description = card_data.get("description", "説明なし")
        desc_lines = description.split("\n")
        desc_y = detail_y + 100
        for line in desc_lines:
            desc_text = self.fonts["small"].render(line, True, settings.WHITE)
            screen.blit(desc_text, (detail_x + 20, desc_y))
            desc_y += 22

        power = ActionHandler.get_card_display_power(player_for_power, card_id)
        if power is not None:
            power_text = self.fonts["small"].render(f"パワー: {power}", True, settings.LIGHT_BLUE)
            power_rect = power_text.get_rect(bottomleft=(detail_x + 20, detail_y + detail_height - 20))
            screen.blit(power_text, power_rect)

