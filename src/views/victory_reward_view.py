# -*- coding: utf-8 -*-
import pygame
import random
import os
from ..config import settings
from ..data.action_data import ACTIONS
from .drawers.player_command_drawer import PlayerCommandDrawer
from ..components.action_handler import ActionHandler


class VictoryRewardView:
    """勝利報酬のUI描画と入力処理。

    - `cards` は提示中のカードIDリスト
    - `rects` は描画時に決まるカードのクリック領域
    """
    def __init__(self, cards: list[str], battle_scene=None):
        self.cards = cards
        self.rects: list[tuple[pygame.Rect, str]] = []
        self.skip_rect: pygame.Rect | None = None
        self.font = None
        self.fonts = {}
        # drawer を作ってカード描画を流用する準備
        self._card_drawer: PlayerCommandDrawer | None = None
        # battle_scene から player や deck_manager を参照して威力計算や特殊表示を行う
        self.battle_scene = battle_scene
        self.player_for_power = getattr(battle_scene, 'player', None)
        self.deck_manager_for_view = getattr(battle_scene, 'deck_manager', None)

    def _ensure_font(self):
        if self.font is None:
            try:
                self.font = self._get_japanese_font(24)
            except Exception:
                try:
                    self.font = pygame.font.SysFont(None, 24)
                except Exception:
                    self.font = pygame.font.Font(None, 24)

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return pygame.font.Font(font_path, size)
                except Exception:
                    continue
        # fallback
        try:
            return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.SysFont(None, size)

    def draw(self, screen: pygame.Surface):
        self._ensure_font()
        screen.fill((18, 18, 28))

        title_font = self._get_japanese_font(48)
        title = title_font.render("勝利！ 報酬を1枚選んでください", True, settings.WHITE)
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        # --- カードは PlayerCommandDrawer の拡大カードデザインをそのまま3枚並べる ---
        # フォント辞書を作成
        self.fonts = {name: self._get_japanese_font(size) for name, size in settings.FONT_SIZES.items()}
        # drawer を遅延生成
        if self._card_drawer is None:
            self._card_drawer = PlayerCommandDrawer(self.fonts)
        # compute card sizing to place three 'enlarged' cards side-by-side
        num_cards = len(self.cards)
        # margins and gap
        margin = 40
        gap = 30
        max_available_width = screen.get_width() - margin * 2 - gap * (max(0, num_cards - 1))
        card_width = int(max_available_width / max(1, num_cards))
        # keep card aspect ratio similar to PlayerCommandDrawer (w:h ~= 0.7)
        card_height = int(card_width / 0.7)
        # if too tall, cap and recompute width
        max_card_height = int(screen.get_height() * 0.75)
        if card_height > max_card_height:
            card_height = max_card_height
            card_width = int(card_height * 0.7)

        # Ensure skip button fits below the cards. If cards are too tall such that
        # the skip button would be drawn off-screen, reduce card height slightly.
        # We anticipate the skip button height used later (skip_h) and a small
        # bottom margin.
        center_y = int(screen.get_height() * 0.55)
        skip_h_est = 44
        bottom_margin = 20
        # bottom of skip rect would be: center_y + card_height//2 + 24 + skip_h_est
        if center_y + (card_height // 2) + 24 + skip_h_est + bottom_margin > screen.get_height():
            # compute the maximum allowed card_height so that skip stays inside
            allowed = screen.get_height() - center_y - 24 - skip_h_est - bottom_margin
            # allowed is the space from card bottom to bottom margin; card_height/2 <= allowed
            new_card_height = max(60, int(allowed * 2))
            # avoid increasing the size accidentally
            if new_card_height < card_height:
                card_height = new_card_height
                card_width = int(card_height * 0.7)

        total_width = card_width * num_cards + gap * (max(0, num_cards - 1))
        start_x = int((screen.get_width() - total_width) / 2)

        self.rects = []
        mouse_pos = pygame.mouse.get_pos()
        hovered_index = None
        for i, card_id in enumerate(self.cards):
            current_card_x = start_x + i * (card_width + gap)
            rect = pygame.Rect(current_card_x, center_y - card_height // 2, card_width, card_height)
            # draw enlarged-style card into the rect
            try:
                # Prefer the drawer helper so visuals match exactly
                if self._card_drawer:
                    # On victory reward screen we hide the standalone effect summary
                    # and the top-right cost label because the description area
                    # already explains the card. Pass flags to suppress them.
                    self._card_drawer.draw_enlarged_into_rect(
                        screen, self.battle_scene, card_id, rect,
                        show_effect_summary=False, show_cost_label=False
                    )
                else:
                    self._draw_enlarged_card_in_rect(screen, card_id, rect)
            except Exception:
                # fallback minimal
                pygame.draw.rect(screen, (60, 60, 80), rect, border_radius=10)
                pygame.draw.rect(screen, settings.WHITE, rect, 2, border_radius=10)
                name = ACTIONS.get(card_id, {}).get('name', card_id)
                screen.blit(self.fonts['small'].render(name, True, settings.WHITE), (rect.x + 8, rect.y + 8))

            self.rects.append((rect, card_id))
            if rect.collidepoint(mouse_pos):
                hovered_index = i

        # スキップボタン
        skip_w, skip_h = 140, 44
        # position skip button below the card row
        skip_rect = pygame.Rect(settings.SCREEN_WIDTH // 2 - skip_w // 2, center_y + (card_height // 2) + 24, skip_w, skip_h)
        pygame.draw.rect(screen, (80, 80, 80), skip_rect, border_radius=6)
        pygame.draw.rect(screen, settings.WHITE, skip_rect, 2, border_radius=6)
        skip_text = self._get_japanese_font(24).render("スキップ", True, settings.WHITE)
        screen.blit(skip_text, skip_text.get_rect(center=skip_rect.center))
        self.skip_rect = skip_rect

        # ホバーで拡大カードを描画
        # hover emphasis: add a glow/border to hovered card
        if hovered_index is not None:
            try:
                r, cid = self.rects[hovered_index]
                glow_rect = r.inflate(12, 12)
                s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 20))
                screen.blit(s, glow_rect.topleft)
                pygame.draw.rect(screen, settings.YELLOW, glow_rect, 3, border_radius=12)
            except Exception:
                pass

        pygame.display.flip()

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Return selected card_id or 'skip' or None"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for rect, cid in self.rects:
                if rect.collidepoint(pos):
                    return cid
            if self.skip_rect and self.skip_rect.collidepoint(pos):
                return 'skip'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'skip'
        return None

    def _draw_enlarged_card_in_rect(self, screen: pygame.Surface, action_id: str, card_rect: pygame.Rect):
        """Draw enlarged card UI into the given rect (adapted from PlayerCommandDrawer._draw_enlarged_card)."""
        effective_id = action_id
        if hasattr(self.deck_manager_for_view, 'get_effective_card_id'):
            effective_id = self.deck_manager_for_view.get_effective_card_id(action_id)
        action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))

        # background and border
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        card_border_color = settings.WHITE
        if action.get('exhaust', False):
            card_border_color = settings.YELLOW
        pygame.draw.rect(screen, card_border_color, card_rect, 3, border_radius=10)

        # name area
        name_font = self.fonts.get('small')
        if not name_font:
            name_font = self._get_japanese_font(24)
        name_text = name_font.render(action.get('name', action_id), True, settings.WHITE)
        name_rect = name_text.get_rect(midtop=(card_rect.centerx, card_rect.top + 14))
        screen.blit(name_text, name_rect)

        # description
        power_for_desc = ""
        if action.get('effects'):
            power_for_desc = action['effects'][0].get('power', "")
        description = action.get('description', "").format(power=power_for_desc)
        desc_font = self.fonts.get('card', self._get_japanese_font(18))
        description_rect = pygame.Rect(card_rect.x + 16, name_rect.bottom + 8, card_rect.width - 32, card_rect.height - name_rect.height - 64)
        # draw multiline using similar helper
        self._draw_text_multiline(screen, description, desc_font, description_rect, settings.WHITE)

        # cost circle at top-left
        if not action.get('unplayable', False):
            cost = action.get('cost', 0)
            if cost >= 0:
                cost_circle_radius = max(10, int(card_rect.width * 0.08))
                cost_circle_center = (card_rect.left + cost_circle_radius + 12, card_rect.top + cost_circle_radius + 12)
                pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
                pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
                cost_text = self.fonts.get('small', self._get_japanese_font(18)).render(str(cost), True, settings.WHITE)
                cost_text_rect = cost_text.get_rect(center=cost_circle_center)
                screen.blit(cost_text, cost_text_rect)

        # power circle at bottom-right
        power = None
        try:
            power = ActionHandler.get_card_display_power(self.player_for_power, effective_id)
        except Exception:
            power = None
        if power is not None:
            effect_type = action.get('effects', [{}])[0].get('type')
            hits = action.get('effects', [{}])[0].get('hits', 1)
            color = settings.BLUE
            if effect_type == 'damage':
                color = settings.RED
            power_circle_radius = max(12, int(card_rect.width * 0.08))
            power_circle_center = (card_rect.right - power_circle_radius - 12, card_rect.bottom - power_circle_radius - 12)
            pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
            pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 2)
            display_text = str(power)
            if hits > 1:
                display_text = f"{power}x{hits}"
            font = self.fonts.get('card', self._get_japanese_font(18))
            power_text = font.render(display_text, True, settings.WHITE)
            power_text_rect = power_text.get_rect(center=power_circle_center)
            screen.blit(power_text, power_text_rect)
