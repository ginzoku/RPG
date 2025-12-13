# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings


class TitleView:
    def __init__(self):
        self.screen = None
        self.fonts = self._load_fonts()
        self.menu_items = [("ゲームを始める", "start"), ("終了する", "quit")]
        self.menu_rects: list[tuple[pygame.Rect, str]] = []

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def _load_fonts(self) -> dict:
        return {name: self._get_japanese_font(size) for name, size in settings.FONT_SIZES.items()}

    def draw(self, screen: pygame.Surface):
        self.screen = screen
        screen.fill(settings.BLACK)

        # タイトルテキスト
        title_font = self.fonts.get("huge", pygame.font.Font(None, 72))
        title_surf = title_font.render("RPGプロトタイプ", True, settings.WHITE)
        title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3))
        screen.blit(title_surf, title_rect)

        # メニュー描画
        self.menu_rects = []
        menu_font = self.fonts.get("large", pygame.font.Font(None, 36))
        base_y = settings.SCREEN_HEIGHT // 2
        spacing = 60

        mouse_pos = pygame.mouse.get_pos()
        for i, (label, key) in enumerate(self.menu_items):
            surf = menu_font.render(label, True, settings.WHITE)
            rect = surf.get_rect(center=(settings.SCREEN_WIDTH // 2, base_y + i * spacing))
            # ハイライト
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (80, 80, 120), rect.inflate(20, 10), border_radius=6)
            screen.blit(surf, rect)
            self.menu_rects.append((rect, key))

        # クレジット等
        credit_font = self.fonts.get("small", pygame.font.Font(None, 18))
        credit = credit_font.render("(c) Your Name", True, settings.WHITE)
        screen.blit(credit, (10, settings.SCREEN_HEIGHT - 30))

        pygame.display.flip()

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, key in self.menu_rects:
                if rect.collidepoint(event.pos):
                    if key == "quit":
                        return "quit"
                    if key == "start":
                        return "start"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "start"
            if event.key == pygame.K_ESCAPE:
                return "quit"

        return None
