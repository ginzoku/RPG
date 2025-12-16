# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings
from ..data.monster_data import MONSTERS

class BestiaryView:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.selected_index = 0
        self.scroll_offset = 0
        self.item_height = 56

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        # reuse font-loading logic similar to other views if needed
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def draw(self, screen: pygame.Surface, monster_keys: list[str], selected_key: str | None):
        screen.fill(settings.BLACK)

        # title
        title_font = self.fonts.get("large", self._get_japanese_font(36))
        title_surf = title_font.render("モンスター図鑑", True, settings.WHITE)
        screen.blit(title_surf, (30, 20))

        # left panel: monster list
        list_rect = pygame.Rect(30, 80, 300, settings.SCREEN_HEIGHT - 120)
        pygame.draw.rect(screen, (20, 20, 30), list_rect)
        pygame.draw.rect(screen, settings.WHITE, list_rect, 2)

        # draw items
        start_y = list_rect.top + 6 - self.scroll_offset
        name_font = self.fonts.get("small", self._get_japanese_font(18))
        for i, key in enumerate(monster_keys):
            y = start_y + i * self.item_height
            item_rect = pygame.Rect(list_rect.left + 6, y, list_rect.width - 12, self.item_height - 8)
            if item_rect.bottom < list_rect.top or item_rect.top > list_rect.bottom:
                continue
            # highlight selected
            if key == selected_key:
                pygame.draw.rect(screen, (50, 50, 80), item_rect, border_radius=6)
            text = MONSTERS.get(key, {}).get("name", key)
            surf = name_font.render(text, True, settings.WHITE)
            screen.blit(surf, (item_rect.left + 8, item_rect.top + 8))

        # right panel: details
        detail_rect = pygame.Rect(list_rect.right + 20, 80, settings.SCREEN_WIDTH - (list_rect.right + 40), settings.SCREEN_HEIGHT - 120)
        pygame.draw.rect(screen, (18, 18, 28), detail_rect)
        pygame.draw.rect(screen, settings.WHITE, detail_rect, 2)

        if selected_key and selected_key in MONSTERS:
            data = MONSTERS[selected_key]
            # image area
            img_path = data.get("image")
            img_surf = None
            if img_path and os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    # scale to fit
                    max_h = 240
                    iw, ih = img.get_size()
                    scale = min(1.0, max_h / ih)
                    img_surf = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
                except Exception:
                    img_surf = None

            if img_surf:
                screen.blit(img_surf, (detail_rect.left + 20, detail_rect.top + 20))

            # name and stats
            name_font = self.fonts.get("medium", self._get_japanese_font(22))
            name_s = name_font.render(data.get("name", selected_key), True, settings.YELLOW)
            screen.blit(name_s, (detail_rect.left + 20, detail_rect.top + 260))

            stats_font = self.fonts.get("small", self._get_japanese_font(16))
            stats_y = detail_rect.top + 300
            hp = data.get("max_hp")
            if hp is not None:
                hp_s = stats_font.render(f"HP: {hp}", True, settings.WHITE)
                screen.blit(hp_s, (detail_rect.left + 20, stats_y))
                stats_y += 24
            atk = data.get("attack_power")
            if atk is not None:
                atk_s = stats_font.render(f"攻撃: {atk}", True, settings.WHITE)
                screen.blit(atk_s, (detail_rect.left + 20, stats_y))
                stats_y += 24

            # description
            desc = data.get("description", "説明なし")
            # simple wrap
            wrap_font = self.fonts.get("small", self._get_japanese_font(16))
            x = detail_rect.left + 20
            y = stats_y + 8
            max_w = detail_rect.width - 40
            for line in desc.splitlines():
                words = line.split(' ')
                cur = ""
                for w in words:
                    test = (cur + " " + w).strip()
                    if wrap_font.size(test)[0] <= max_w:
                        cur = test
                    else:
                        surf = wrap_font.render(cur, True, settings.WHITE)
                        screen.blit(surf, (x, y))
                        y += wrap_font.get_height() + 4
                        cur = w
                if cur:
                    surf = wrap_font.render(cur, True, settings.WHITE)
                    screen.blit(surf, (x, y))
                    y += wrap_font.get_height() + 4

        # footer / instructions
        footer = self.fonts.get("small", self._get_japanese_font(16)).render("クリックで選択 / ESCで戻る", True, settings.WHITE)
        screen.blit(footer, (30, settings.SCREEN_HEIGHT - 40))

        pygame.display.flip()
