# -*- coding: utf-8 -*-
import pygame
from ..scenes.map_scene import MapScene # 修正

class MapController:
    """マップシーンの入力を処理するクラス"""
    def handle_input(self, events: list[pygame.event.Event], map_scene: MapScene):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1
        
        map_scene.move_player(dx, dy)