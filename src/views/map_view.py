# -*- coding: utf-8 -*-
import pygame
from ..config import settings
from ..scenes.map_scene import MapScene # 修正
from ..utils.map_layout import compute_node_positions

# Toggle node expected-score display here (set False to disable)
SHOW_NODE_SCORES = False

class MapView:
    """マップを描画するクラス"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        # アイコン描画設定（小さめにする）
        self.icon_size = max(20, settings.SCREEN_WIDTH // 20)
        self.icon_margin = 10
        # オーバーレイ上のチェイン表示設定（縦方向、間隔を控えめにして見通しを良くする）
        self.chain_count = 15
        self.chain_square = 30
        self.chain_spacing = 34
        self.chain_top_margin = 80
        self.chain_x = settings.SCREEN_WIDTH // 2
        # dashed line parameters
        self.dash_len = 8
        self.gap_len = 6

    def draw(self, map_scene: MapScene):
        # 背景
        self.screen.fill(settings.BLACK)

        # マップはオーバーレイ上に表示する: オーバーレイがあるときに map_graph をその上に描画する
        # フォールバックとして、graph がない場合は従来グリッドを描画
        graph = getattr(map_scene, 'map_graph', None)
        fallback_grid = graph is None


        # プレイヤー
        pygame.draw.rect(self.screen, settings.BLUE, map_scene.player_rect)

        # 敵シンボル
        for enemy in map_scene.enemies:
            pygame.draw.rect(self.screen, settings.RED, enemy.rect)

        # NPC
        for npc in map_scene.npcs:
            pygame.draw.rect(self.screen, npc.color, npc.rect)


        # オーバーレイのフェード処理: map_scene.overlay_active を目標として map_scene.overlay_alpha を補間
        target_alpha = 255 if getattr(map_scene, 'overlay_active', False) else 0
        # フレームごとの変化量（高速すぎないように調整）
        step = 20
        current = getattr(map_scene, 'overlay_alpha', 0)
        if current < target_alpha:
            current = min(target_alpha, current + step)
        elif current > target_alpha:
            current = max(target_alpha, current - step)
        # 更新値を MapScene に書き戻す
        map_scene.overlay_alpha = current

        # スクロールの補間: controller が設定する overlay_scroll_target に滑らかに追従
        cur_scroll = float(getattr(map_scene, 'overlay_scroll', 0) or 0)
        target_scroll = float(getattr(map_scene, 'overlay_scroll_target', cur_scroll) or cur_scroll)
        smoothing = 0.6
        cur_scroll += (target_scroll - cur_scroll) * smoothing
        if abs(target_scroll - cur_scroll) < 0.5:
            cur_scroll = target_scroll
        map_scene.overlay_scroll = cur_scroll

        if current > 0:
            # 黒いオーバーレイ背景を描画（アルファ付き）
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags=pygame.SRCALPHA)
            bg = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            bg.fill((0, 0, 0))
            bg.set_alpha(int(current))
            overlay.blit(bg, (0, 0))

            # draw graph onto overlay if available, otherwise draw fallback grid onto overlay
            if not fallback_grid:
                expected_scores = {}
                # Compute positions using shared utility (keeps MapView and MapScene consistent)
                node_size = 32
                level_margin = 80
                level_spacing = 80
                h_padding = 40
                node_positions_full, per_level = compute_node_positions(graph, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, getattr(map_scene, 'overlay_scroll', 0), node_size=node_size, level_margin=level_margin, level_spacing=level_spacing, h_padding=h_padding)
                # node_positions for drawing convenience: id -> (cx, cy)
                node_positions = {nid: (cx, cy) for nid, (cx, cy, r) in node_positions_full.items()}
                # build id->node map for quick type checks when drawing
                id_to_node = {n['id']: n for lvl_nodes in graph for n in lvl_nodes}

                # compute expected downstream scores if enabled
                if SHOW_NODE_SCORES:
                    # build children map
                    children = {n['id']: [] for lvl in graph for n in lvl}
                    for lvl_nodes in graph:
                        for n in lvl_nodes:
                            for p in n.get('parents', []):
                                if p in children:
                                    children[p].append(n['id'])
                    # scoring
                    score_map = {'monster': 0.0, 'event': 1.0, 'shop': 1.5, 'rest': 0.5, 'treasure': 2.0, 'elite': 3.0, 'boss': 5.0, 'start': 0.0}
                    expected = {}
                    for lvl_i in range(len(graph) - 1, -1, -1):
                        for n in graph[lvl_i]:
                            nid = n['id']
                            base = score_map.get(n.get('type', 'monster'), 0.0)
                            childs = children.get(nid, [])
                            if not childs:
                                expected[nid] = base
                            else:
                                exp_children = [expected[cid] for cid in childs]
                                expected[nid] = base + (sum(exp_children) / len(exp_children))
                    expected_scores = expected

                # build children map for extra skip-connections
                children_map = {n['id']: [] for lvl in graph for n in lvl}
                for lvl_nodes in graph:
                    for n in lvl_nodes:
                        for p in n.get('parents', []):
                            if p in children_map:
                                children_map[p].append(n['id'])

                # expose node positions to scene for hit-testing
                try:
                    # store rects (x,y,w,h) for collision checks using computed radius
                    map_scene.node_positions = {nid: pygame.Rect(cx - r, cy - r, r * 2, r * 2) for nid, (cx, cy, r) in node_positions_full.items()}
                except Exception:
                    map_scene.node_positions = {}

                # draw connections onto overlay
                # For each node, draw a straight connector from each parent to the node.
                for lvl_idx, nodes in enumerate(graph):
                    for node in nodes:
                        parents = node.get('parents', [])
                        for p in parents:
                            if p not in node_positions or node['id'] not in node_positions:
                                continue
                            x1, y1 = node_positions[p]
                            x2, y2 = node_positions[node['id']]
                            # skip drawing if completely off-screen vertically
                            if (y1 < -100 and y2 < -100) or (y1 > settings.SCREEN_HEIGHT + 100 and y2 > settings.SCREEN_HEIGHT + 100):
                                continue
                            # draw shorter connection (stop at node radii) and thinner line for compact view
                            r = node_size // 2
                            dx = x2 - x1
                            dy = y2 - y1
                            dist = (dx * dx + dy * dy) ** 0.5
                            if dist > 0:
                                sx = x1 + dx * (r / dist)
                                sy = y1 + dy * (r / dist)
                                ex = x2 - dx * (r / dist)
                                ey = y2 - dy * (r / dist)
                                pygame.draw.line(overlay, (140, 140, 140), (int(sx), int(sy)), (int(ex), int(ey)), 3)
                            else:
                                pygame.draw.line(overlay, (140, 140, 140), (x1, y1), (x2, y2), 3)

                # draw nodes onto overlay (after connections so nodes overlay lines)
                enabled_nodes = getattr(map_scene, 'enabled_nodes', None)
                for lvl_idx, nodes in enumerate(graph):
                    for node in nodes:
                        pos = node_positions.get(node['id'])
                        if not pos:
                            continue
                        cx, cy = pos
                        r = node_size // 2
                        t = node.get('type', 'normal')
                        # draw all nodes (skip concept removed)
                        if t == 'elite':
                            color = (80, 180, 80)
                        elif t == 'shop':
                            color = (100, 180, 240)
                        elif t == 'rest':
                            color = (255, 165, 0)
                        elif t == 'treasure':
                            color = (200, 160, 80)
                        elif t == 'dark':
                            color = (60, 60, 60)
                        elif t == 'boss':
                            color = (200, 60, 60)
                        elif t == 'event':
                            color = (140, 80, 200)
                        else:
                            color = (200, 200, 200)
                        # skip drawing if off-screen to save time
                        if cy + r < 0 or cy - r > settings.SCREEN_HEIGHT:
                            continue
                        # dim nodes that are not yet enabled by reducing original color brightness
                        if enabled_nodes is not None and node.get('id') not in enabled_nodes:
                            try:
                                factor = 0.65
                                draw_color = tuple(max(0, min(255, int(c * factor))) for c in color)
                                # slightly darker border for disabled nodes
                                border_color = tuple(max(0, min(255, int(b * 0.6))) for b in (30, 30, 30))
                            except Exception:
                                draw_color = (60, 60, 60)
                                border_color = (30, 30, 30)
                        else:
                            draw_color = color
                            border_color = (30, 30, 30)
                        pygame.draw.circle(overlay, draw_color, (cx, cy), r)
                        pygame.draw.circle(overlay, border_color, (cx, cy), r, 2)
                        # draw expected score label if enabled
                        if SHOW_NODE_SCORES and node.get('id') in expected_scores:
                            val = expected_scores.get(node['id'], 0.0)
                            txt = self.font.render(f"{val:.1f}", True, (255, 255, 255))
                            # background rect for readability
                            tx = cx - txt.get_width() // 2
                            ty = cy + r + 4
                            bg = pygame.Rect(tx - 2, ty - 2, txt.get_width() + 4, txt.get_height() + 4)
                            pygame.draw.rect(overlay, (0, 0, 0, 200), bg)
                            overlay.blit(txt, (tx, ty))
            else:
                # フォールバック: 縦に15個のマスを並べて描画（スクロールで見渡せる）
                count = 15
                node_size = 32
                level_margin = 80
                level_spacing = 80
                cx = settings.SCREEN_WIDTH // 2

                # compute total content height and clamp scroll
                total_height = level_margin * 2 + (count - 1) * level_spacing
                cur_scroll = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                if cur_scroll < 0:
                    cur_scroll = 0
                max_scroll = max(0, int(total_height - settings.SCREEN_HEIGHT))
                if cur_scroll > max_scroll:
                    cur_scroll = max_scroll

                # draw connecting vertical lines between centers (shorten by node radius)
                line_color = (140, 140, 140)
                line_width = 3
                centers = []
                for i in range(count):
                    y = level_margin + i * level_spacing - cur_scroll
                    centers.append((cx, y))

                for i in range(count - 1):
                    x1, y1 = centers[i]
                    x2, y2 = centers[i + 1]
                    # skip if both points off-screen
                    if (y1 < -100 and y2 < -100) or (y1 > settings.SCREEN_HEIGHT + 100 and y2 > settings.SCREEN_HEIGHT + 100):
                        continue
                    # shorten by node radius for nicer spacing
                    r = node_size // 2
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist > 0:
                        sx = x1 + dx * (r / dist)
                        sy = y1 + dy * (r / dist)
                        ex = x2 - dx * (r / dist)
                        ey = y2 - dy * (r / dist)
                        pygame.draw.line(overlay, line_color, (int(sx), int(sy)), (int(ex), int(ey)), line_width)
                    else:
                        pygame.draw.line(overlay, line_color, (x1, y1), (x2, y2), line_width)

                # draw squares
                for i, (cx, y) in enumerate(centers):
                    rect = pygame.Rect(cx - node_size // 2, int(y - node_size // 2), node_size, node_size)
                    if rect.bottom < 0 or rect.top > settings.SCREEN_HEIGHT:
                        continue
                    if i == count - 1:
                        fill_color = (200, 60, 60)
                        border_color = (150, 20, 20)
                    else:
                        fill_color = (220, 220, 220)
                        border_color = (30, 30, 30)
                    pygame.draw.rect(overlay, fill_color, rect, border_radius=6)
                    pygame.draw.rect(overlay, border_color, rect, 2, border_radius=6)

            # finally blit overlay with map content
            self.screen.blit(overlay, (0, 0))

        # 右上アイコンを描画（オーバーレイの上に表示するため、ここで描く）
        icon_rect = pygame.Rect(settings.SCREEN_WIDTH - self.icon_margin - self.icon_size, self.icon_margin, self.icon_size, self.icon_size)
        pygame.draw.rect(self.screen, (40, 40, 40), icon_rect, border_radius=6)  # ダークグレーの背景
        inner = icon_rect.inflate(-self.icon_size // 4, -self.icon_size // 4)
        pygame.draw.rect(self.screen, (200, 200, 200), inner, border_radius=4)

        # NOTE: do not call `pygame.display.flip()` here — the main loop performs a single flip per frame.