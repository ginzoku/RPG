# -*- coding: utf-8 -*-
import pygame
from ..config import settings
from ..scenes.conversation_scene import ConversationScene
import os

class ConversationView:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = self._get_japanese_font(24)
        self.speaker_font = self._get_japanese_font(20)

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

    def draw(self, conversation_scene: ConversationScene, map_view, map_scene):
        # 背景を黒で塗りつぶす
        self.screen.fill(settings.BLACK)

        # 会話ウィンドウ
        window_height = 150
        window_rect = pygame.Rect(50, settings.SCREEN_HEIGHT - window_height - 50, settings.SCREEN_WIDTH - 100, window_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), window_rect) # 半透明の黒
        pygame.draw.rect(self.screen, settings.WHITE, window_rect, 2)

        if not conversation_scene.conversation_data:
            return

        current_line = conversation_scene.conversation_data[conversation_scene.current_line_index]
        speaker = current_line["speaker"]
        text = current_line["text"]

        # 話者名
        speaker_surface = self.speaker_font.render(f"【{speaker}】", True, settings.YELLOW)
        self.screen.blit(speaker_surface, (window_rect.x + 20, window_rect.y + 15))

        # 会話テキスト
        text_surface = self.font.render(text, True, settings.WHITE)
        self.screen.blit(text_surface, (window_rect.x + 30, window_rect.y + 60))

        # 次へ進むインジケーター (例: ▼)
        indicator = self.font.render("▼", True, settings.WHITE)
        self.screen.blit(indicator, (window_rect.right - 40, window_rect.bottom - 30))

        pygame.display.flip()