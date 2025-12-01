# -*- coding: utf-8 -*-
import pygame
from ...config import settings
from .map_scene import MapScene

class MapView:
    """マップを描画するクラス"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def draw(self, map_scene: MapScene):
        # 背景
        self.screen.fill(settings.GREEN)

        # プレイヤー
        pygame.draw.rect(self.screen, settings.BLUE, map_scene.player_rect)

        # 敵シンボル
        for enemy in map_scene.enemies:
            pygame.draw.rect(self.screen, settings.RED, enemy.rect)

        pygame.display.flip()