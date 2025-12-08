# -*- coding: utf-8 -*-
import pygame
import time
from ...config import settings # Added import

class DamageIndicator:
    """ダメージ数値のアニメーション表示を管理するクラス"""
    def __init__(self, text: str, position: tuple[int, int], color: tuple[int, int, int], font: pygame.font.Font):
        self.text = text
        self.start_pos = position
        self.current_pos = list(position)
        self.color = color
        self.font = font
        self.start_time = time.time()
        self.duration = settings.ANIMATION_SETTINGS["damage_indicator"]["duration"]
        self.is_alive = True
        self.jump_height = settings.ANIMATION_SETTINGS["damage_indicator"]["jump_height"]

    def update(self):
        """アニメーションの状態を更新する"""
        if not self.is_alive:
            return

        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.duration:
            self.is_alive = False
            return

        # 0から1への進捗度
        progress = elapsed_time / self.duration

        # 放物線を描くような動き（跳ねるアニメーション）
        # y = -4 * h * (x - 0.5)^2 + h  (h: jump_height, x: progress)
        # これにより、progress=0.5で頂点に達し、progress=0と1でy=0になる
        y_offset = -4 * self.jump_height * (progress - 0.5)**2 + self.jump_height

        self.current_pos[1] = self.start_pos[1] - y_offset

    def draw(self, screen: pygame.Surface):
        """ダメージ数値を画面に描画する"""
        if not self.is_alive:
            return
        
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=self.current_pos)
        screen.blit(text_surface, text_rect)