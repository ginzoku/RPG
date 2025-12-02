# -*- coding: utf-8 -*-
import pygame
from typing import Optional
from ..scenes.map_scene import MapScene

class MapController:
    """マップシーンの入力を処理するクラス"""
    def handle_input(self, events: list[pygame.event.Event], map_scene: MapScene) -> Optional['Npc']:
        for event in events:
            if event.type == pygame.KEYDOWN:
                # 移動処理
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

                # 会話開始処理
                if event.key == pygame.K_RETURN:
                    for npc in map_scene.npcs:
                        # プレイヤーがNPCに隣接しているかチェック
                        if map_scene.player_rect.colliderect(npc.rect.inflate(map_scene.grid_size, map_scene.grid_size)):
                            return npc # 衝突したNPCオブジェクトを返す
        return None