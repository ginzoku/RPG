# -*- coding: utf-8 -*-
import pygame
from typing import Optional
from ..scenes.map_scene import MapScene
from ..config import settings

class MapController:
    """マップシーンの入力を処理するクラス"""
    def handle_input(self, events: list[pygame.event.Event], map_scene: MapScene) -> Optional['Npc']:
        for event in events:
            # マウスホイール/タッチスクロール: オーバーレイが有効なときはスクロール操作に使う
            if event.type == pygame.MOUSEWHEEL:
                if getattr(map_scene, 'overlay_active', False):
                    # 上方向スクロールは event.y > 0
                    scroll_step = 60
                    cur = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                    # if we have a generated graph, calculate content height similarly to MapView
                    graph = getattr(map_scene, 'map_graph', None)
                    if graph:
                        count = len(graph)
                        # match MapView: spacing shortened to match view
                        level_margin = 80
                        level_spacing = 100
                        content_height = level_margin * 2 + (count - 1) * level_spacing
                        visible = settings.SCREEN_HEIGHT
                    else:
                        # fallback to previous chain assumptions
                        count = 15
                        sq = 44
                        spacing = 42
                        top_margin = 70
                        content_height = top_margin * 2 + (count - 1) * spacing
                        visible = settings.SCREEN_HEIGHT
                    max_scroll = max(0, int(content_height - visible))
                    new = cur - event.y * scroll_step
                    if new < 0:
                        new = 0
                    if new > max_scroll:
                        new = max_scroll
                    # set target (controller updates target; view interpolates current toward it)
                    map_scene.overlay_scroll_target = new
                    continue
            # Some platforms use MOUSEBUTTONDOWN with button 4/5 for wheel
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                if getattr(map_scene, 'overlay_active', False):
                    scroll_step = 60
                    direction = 1 if event.button == 4 else -1
                    cur = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                    graph = getattr(map_scene, 'map_graph', None)
                    if graph:
                        count = len(graph)
                        level_margin = 80
                        level_spacing = 100
                        content_height = level_margin * 2 + (count - 1) * level_spacing
                        visible = settings.SCREEN_HEIGHT
                    else:
                        count = 15
                        sq = 44
                        spacing = 42
                        top_margin = 70
                        content_height = top_margin * 2 + (count - 1) * spacing
                        visible = settings.SCREEN_HEIGHT
                    max_scroll = max(0, int(content_height - visible))
                    new = cur - direction * scroll_step
                    if new < 0:
                        new = 0
                    if new > max_scroll:
                        new = max_scroll
                    map_scene.overlay_scroll_target = new
                    continue
            # マウスクリック: 右上アイコンのクリックを検出してオーバーレイを切り替える
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # アイコンは画面右上に小さめに表示（スクリーン幅の1/20, margin=10）
                icon_size = max(20, settings.SCREEN_WIDTH // 20)
                margin = 10
                icon_rect = pygame.Rect(settings.SCREEN_WIDTH - margin - icon_size, margin, icon_size, icon_size)
                if icon_rect.collidepoint(mx, my):
                    # トグル表示
                    map_scene.overlay_active = not getattr(map_scene, 'overlay_active', False)
                    # consume this event (don't treat as other interactions)
                    continue

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