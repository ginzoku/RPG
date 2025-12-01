# -*- coding: utf-8 -*-
import pygame
from ..scenes.map_scene import MapScene

class MapController:
    """マップシーンの入力を処理するクラス"""
    def handle_input(self, events: list[pygame.event.Event], map_scene: MapScene):
        for event in events:
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                
                if dx != 0 or dy != 0:
                    map_scene.move_player(dx, dy)