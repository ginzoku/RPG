# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings


class MapConversationView:
    def __init__(self, default_background_path: str | None):
        # 日本語フォント探索
        self.font = self._get_japanese_font(26)
        self.speaker_font = self._get_japanese_font(30)
        self.background_image = None
        if default_background_path:
            try:
                self.background_image = pygame.image.load(default_background_path).convert()
                self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            except Exception:
                self.background_image = None

        self.dialogue_text = ""
        self.speaker_name = ""
        self.choices = []
        self.selected_choice_index = 0

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return pygame.font.Font(p, size)
                except Exception:
                    continue
        return pygame.font.Font(None, size)

    def set_dialogue(self, speaker: str | None, text: str):
        self.speaker_name = speaker if speaker else ""
        self.dialogue_text = text

    def set_choices(self, choices: list[str]):
        self.choices = choices

    def clear_choices(self):
        self.choices = []
        self.selected_choice_index = 0

    def set_selected_choice(self, index: int):
        self.selected_choice_index = index

    def set_background(self, image_path: str | None):
        if not image_path:
            self.background_image = None
            return
        try:
            self.background_image = pygame.image.load(image_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception:
            self.background_image = None

    def draw(self, screen: pygame.Surface):
        # マップの背景をそのままにして、画面下部にログ風パネルを描画する
        try:
            log_height = int(settings.SCREEN_HEIGHT * 0.28)
            log_rect = pygame.Rect(0, settings.SCREEN_HEIGHT - log_height, settings.SCREEN_WIDTH, log_height)

            panel = pygame.Surface((log_rect.width, log_rect.height), pygame.SRCALPHA)
            panel.fill((12, 12, 16, 220))
            screen.blit(panel, log_rect.topleft)
            pygame.draw.rect(screen, settings.WHITE, log_rect, 1)

            padding = 14
            max_width = log_rect.width - padding * 2

            # 話者を左上に表示
            if self.speaker_name:
                s_surf = self.speaker_font.render(self.speaker_name, True, settings.YELLOW)
                screen.blit(s_surf, (log_rect.x + padding, log_rect.y + padding))

            # テキストを折り返して表示（簡易実装）
            words = self.dialogue_text.split(' ')
            lines = []
            cur = ''
            for w0 in words:
                test = (cur + ' ' + w0).strip() if cur else w0
                if self.font.size(test)[0] <= max_width:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = w0
            if cur:
                lines.append(cur)

            # テキストは話者行の下から描画
            start_y = log_rect.y + padding + (self.speaker_font.get_height() + 6 if self.speaker_name else 0)
            for i, line in enumerate(lines[:6]):
                surf = self.font.render(line, True, settings.WHITE)
                screen.blit(surf, (log_rect.x + padding, start_y + i * (self.font.get_height() + 6)))

        finally:
            # マップ会話時はここで必ず表示更新する
            pygame.display.flip()
