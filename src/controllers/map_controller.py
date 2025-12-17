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
                    scroll_step = 30
                    cur = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                    # コンテンツ高さと表示領域を MapView と同じ計算で導出してクランプ
                    count = 15
                    sq = 36
                    spacing = 84
                    top_margin = 80
                    total_height = count * sq + (count - 1) * spacing
                    visible = settings.SCREEN_HEIGHT - top_margin - 40
                    max_scroll = max(0, total_height - visible)
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
                    scroll_step = 30
                    direction = 1 if event.button == 4 else -1
                    cur = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                    count = 15
                    sq = 36
                    spacing = 84
                    top_margin = 80
                    total_height = count * sq + (count - 1) * spacing
                    visible = settings.SCREEN_HEIGHT - top_margin - 40
                    max_scroll = max(0, total_height - visible)
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