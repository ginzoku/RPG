# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings

class ConversationView:
    def __init__(self, default_background_path: str | None):
        self.font = self._get_japanese_font(24)
        self.speaker_font = self._get_japanese_font(28)
        
        # UIの相対的なサイズと位置を定義
        dialogue_box_height = int(settings.SCREEN_HEIGHT * 0.25)
        dialogue_box_margin_x = int(settings.SCREEN_WIDTH * 0.05)
        dialogue_box_y = settings.SCREEN_HEIGHT - dialogue_box_height - int(settings.SCREEN_HEIGHT * 0.05)

        self.dialogue_box_rect = pygame.Rect(
            dialogue_box_margin_x,
            dialogue_box_y,
            settings.SCREEN_WIDTH - (dialogue_box_margin_x * 2),
            dialogue_box_height
        )

        speaker_box_height = int(settings.SCREEN_HEIGHT * 0.05)
        speaker_box_width = int(settings.SCREEN_WIDTH * 0.2)
        speaker_box_y_offset = int(settings.SCREEN_HEIGHT * 0.01)

        self.speaker_rect = pygame.Rect(
            dialogue_box_margin_x,
            dialogue_box_y - speaker_box_height - speaker_box_y_offset,
            speaker_box_width,
            speaker_box_height
        )

        self.speaker_name = ""
        self.dialogue_text = ""
        self.choices = []
        self.selected_choice_index = 0
        
        self.background_image = None
        if default_background_path:
            self.set_background(default_background_path)
    
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
        if image_path is None:
            self.background_image = None
            return

        try:
            full_path = image_path # 仮定: image_pathはすでにフルパスか、または適切に解決されるパス
            self.background_image = pygame.image.load(full_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image {image_path}: {e}")
            self.background_image = None # ロード失敗時は背景なし

    def draw(self, screen):
        # 背景の描画
        if self.background_image:
            screen.blit(self.background_image, (0, 0))

        # ダイアログボックスの描画
        pygame.draw.rect(screen, (0, 0, 0, 180), self.dialogue_box_rect, border_radius=10) # 半透明の黒
        pygame.draw.rect(screen, (255, 255, 255), self.dialogue_box_rect, 2, border_radius=10) # 枠線

        # 話者名の描画
        if self.speaker_name:
            pygame.draw.rect(screen, (50, 50, 50), self.speaker_rect, border_radius=5)
            speaker_surface = self.speaker_font.render(self.speaker_name, True, (255, 255, 255))
            screen.blit(speaker_surface, (self.speaker_rect.x + 10, self.speaker_rect.y + 5))

        # ダイアログテキストの描画
        dialogue_surface = self.font.render(self.dialogue_text, True, (255, 255, 255))
        screen.blit(dialogue_surface, (self.dialogue_box_rect.x + 10, self.dialogue_box_rect.y + 10))

        # 選択肢の描画
        if self.choices:
            # 選択肢の描画位置と行の高さを相対的に計算
            choice_start_x = self.dialogue_box_rect.x + int(self.dialogue_box_rect.width * 0.05)
            # ダイアログボックス上部から、ボックスの高さの35%の位置を開始点とする
            choice_start_y = self.dialogue_box_rect.y + int(self.dialogue_box_rect.height * 0.35)
            line_height = self.font.get_height() + 10  # フォントの高さに少しマージンを追加

            for i, choice_text in enumerate(self.choices):
                color = (255, 255, 0) if i == self.selected_choice_index else (255, 255, 255)
                choice_surface = self.font.render(f"> {choice_text}" if i == self.selected_choice_index else choice_text, True, color)
                # 計算された相対位置に描画
                screen.blit(choice_surface, (choice_start_x, choice_start_y + i * line_height))
