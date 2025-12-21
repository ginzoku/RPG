# -*- coding: utf-8 -*-
import pygame
from typing import Optional
from ..scenes.map_scene import MapScene
from ..config import settings
from ..components.enemy_symbol import EnemySymbol
from ..components.npc import Npc
from ..data.enemy_group_data import ENEMY_GROUPS
import random

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
            # マウス移動: オーバーレイ上でノードのホバーを検出して MapScene に記録
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if getattr(map_scene, 'overlay_active', False):
                    node_positions = getattr(map_scene, 'node_positions', None)
                    graph = getattr(map_scene, 'map_graph', None)
                    hovered = None
                    if node_positions and graph:
                        for nid, rect in node_positions.items():
                            if rect.collidepoint(mx, my):
                                # only consider enabled nodes for hover
                                allowed = getattr(map_scene, 'enabled_nodes', None)
                                if allowed is None or nid in allowed:
                                    hovered = nid
                                    break
                    try:
                        map_scene.hovered_node = hovered
                    except Exception:
                        pass
                else:
                    try:
                        map_scene.hovered_node = None
                    except Exception:
                        pass
                # do not consume the motion event; allow other handlers if needed
            # マウスクリック: 右上アイコンのクリックを検出してオーバーレイを切り替える
            if event.type == pygame.MOUSEBUTTONDOWN:
                # handle right-click selection of a source node when overlay active
                if event.button == 3 and getattr(map_scene, 'overlay_active', False):
                    mx, my = event.pos
                    node_positions = getattr(map_scene, 'node_positions', None)
                    graph = getattr(map_scene, 'map_graph', None)
                    if node_positions and graph:
                        for nid, rect in node_positions.items():
                            if rect.collidepoint(mx, my):
                                # only allow selecting enabled nodes
                                allowed = getattr(map_scene, 'enabled_nodes', None)
                                if allowed is None or nid in allowed:
                                    # toggle selection
                                    if getattr(map_scene, 'selected_source_node', None) == nid:
                                        map_scene.selected_source_node = None
                                    else:
                                        map_scene.selected_source_node = nid
                                break
                    # consume the click
                    continue
                # left-click handling continues
                if event.button == 1:
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

                    # If overlay is active and we have a generated graph, check for node clicks
                    if getattr(map_scene, 'overlay_active', False):
                        # hit-test against node positions if MapView exposed them
                        node_positions = getattr(map_scene, 'node_positions', None)
                        graph = getattr(map_scene, 'map_graph', None)
                        if node_positions and graph:
                            for nid, rect in node_positions.items():
                                if rect.collidepoint(mx, my):
                                    # find node object by id
                                    node_obj = None
                                    for lvl in graph:
                                        for n in lvl:
                                            if n.get('id') == nid:
                                                node_obj = n
                                                break
                                        if node_obj:
                                            break
                                    if not node_obj:
                                        break
                                    # ignore clicks on nodes that are not enabled
                                    allowed = getattr(map_scene, 'enabled_nodes', None)
                                    if allowed is not None and node_obj.get('id') not in allowed:
                                        # click on disabled node: ignore
                                        break
                                    t = node_obj.get('type', 'monster')
                                    # monster/elite/boss -> initiate battle by setting collided_enemy
                                    if t in ('monster', 'elite', 'boss'):
                                        try:
                                            group_ids = list(ENEMY_GROUPS.keys())
                                            gid = random.choice(group_ids) if group_ids else 'default'
                                            # create a synthetic EnemySymbol for pending transition
                                            enemy_sym = EnemySymbol(0, 0, 32, gid)
                                            # attach map node id so MapScene can advance after battle
                                            try:
                                                enemy_sym._map_node_id = nid
                                            except Exception:
                                                pass
                                            # set pending battle so MapScene.update doesn't clear it
                                            map_scene._pending_battle = enemy_sym
                                        except Exception:
                                            map_scene._pending_battle = None
                                        # consume the click event (no ConversationScene)
                                        return None
                                    else:
                                        # event/shop/rest/treasure/dark -> open conversation with default id
                                        # choose a conversation id mapping (fallbacks)
                                        conv_map = {
                                            'event': 'test_choice_conversation',
                                            'shop': 'npc_1_intro',
                                            'rest': 'npc_1_intro',
                                            'treasure': 'npc_1_intro',
                                            'dark': 'test_choice_conversation'
                                        }
                                        conv = conv_map.get(t, 'test_choice_conversation')
                                        # return a temporary Npc-like object with conversation_id
                                        temp_npc = Npc(-100, -100, map_scene.grid_size or 32, conv)
                                        try:
                                            temp_npc._map_node_id = nid
                                        except Exception:
                                            pass
                                        return temp_npc

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