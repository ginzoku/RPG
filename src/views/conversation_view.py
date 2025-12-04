# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings

class ConversationView:
    def __init__(self, default_background_path: str | None):
        self.font = self._get_japanese_font(24)
        self.speaker_font = self._get_japanese_font(28)
        self.dialogue_box_rect = pygame.Rect(50, settings.SCREEN_HEIGHT - 200, settings.SCREEN_WIDTH - 100, 150)
        self.speaker_rect = pygame.Rect(50, settings.SCREEN_HEIGHT - 230, 200, 30)

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

    def set_background(self, image_path: str):
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
        else:
            screen.fill((0, 0, 0)) # 背景画像がない場合は黒で塗りつぶし

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
            for i, choice_text in enumerate(self.choices):
                color = (255, 255, 0) if i == self.selected_choice_index else (255, 255, 255)
                choice_surface = self.font.render(f"> {choice_text}" if i == self.selected_choice_index else choice_text, True, color)
                screen.blit(choice_surface, (self.dialogue_box_rect.x + 30, self.dialogue_box_rect.y + 50 + i * 30))
