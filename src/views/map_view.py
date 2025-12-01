# -*- coding: utf-8 -*-
import pygame
from ..config import settings
from ..scenes.map_scene import MapScene # 修正

class MapView:
    """マップを描画するクラス"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def draw(self, map_scene: MapScene):
        # 背景
        self.screen.fill(settings.BLACK)

        # 移動可能エリアの描画
        for y in range(map_scene.map_height):
            for x in range(map_scene.map_width):
                if map_scene.map_data[y][x] == 1:
                    rect = pygame.Rect(x * map_scene.grid_size, y * map_scene.grid_size, map_scene.grid_size, map_scene.grid_size)
                    
                    # 上の辺を描画
                    if y == 0 or map_scene.map_data[y - 1][x] == 0:
                        pygame.draw.line(self.screen, settings.WHITE, rect.topleft, rect.topright)
                    
                    # 下の辺を描画
                    if y == map_scene.map_height - 1 or map_scene.map_data[y + 1][x] == 0:
                        pygame.draw.line(self.screen, settings.WHITE, rect.bottomleft, rect.bottomright)

                    # 左の辺を描画
                    if x == 0 or map_scene.map_data[y][x - 1] == 0:
                        pygame.draw.line(self.screen, settings.WHITE, rect.topleft, rect.bottomleft)

                    # 右の辺を描画
                    if x == map_scene.map_width - 1 or map_scene.map_data[y][x + 1] == 0:
                        pygame.draw.line(self.screen, settings.WHITE, rect.topright, rect.bottomright)


        # プレイヤー
        pygame.draw.rect(self.screen, settings.BLUE, map_scene.player_rect)

        # 敵シンボル
        for enemy in map_scene.enemies:
            pygame.draw.rect(self.screen, settings.RED, enemy.rect)

        pygame.display.flip()