# -*- coding: utf-8 -*-
import pygame
from ..config import settings
from ..scenes.map_scene import MapScene # 修正

class MapView:
    """マップを描画するクラス"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        # アイコン描画設定（小さめにする）
        self.icon_size = max(20, settings.SCREEN_WIDTH // 20)
        self.icon_margin = 10
        # オーバーレイ上のチェイン表示設定（縦方向、間隔を広めにして線を長くする）
        self.chain_count = 15
        self.chain_square = 36
        self.chain_spacing = 84
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
                node_positions = {}
                # 強めに縦間隔を離すため固定の行間を使う（ガッツリ離す）
                level_margin = 100
                level_spacing = 200  # 1行あたりの縦間隔（px） — 十分大きくしてスクロールで見渡せるようにする
                node_size = 44
                h_padding = 60
                for lvl_idx, nodes in enumerate(graph):
                    y = int(level_margin + lvl_idx * level_spacing)
                    # apply vertical scroll offset
                    y -= int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                    count = len(nodes)
                    if count == 0:
                        continue
                    total_w = count * node_size + (count - 1) * h_padding
                    start_x = (settings.SCREEN_WIDTH - total_w) // 2
                    for i, node in enumerate(nodes):
                        x = int(start_x + i * (node_size + h_padding))
                        cx = x + node_size // 2
                        cy = y
                        node_positions[node['id']] = (cx, cy)

                # draw connections onto overlay
                for lvl_idx, nodes in enumerate(graph):
                    for node in nodes:
                        parents = node.get('parents', [])
                        for p in parents:
                            if p in node_positions and node['id'] in node_positions:
                                x1, y1 = node_positions[p]
                                x2, y2 = node_positions[node['id']]
                                # skip drawing if completely off-screen vertically
                                if (y1 < -100 and y2 < -100) or (y1 > settings.SCREEN_HEIGHT + 100 and y2 > settings.SCREEN_HEIGHT + 100):
                                    continue
                                # thicker, slightly darker line for readability
                                pygame.draw.line(overlay, (140, 140, 140), (x1, y1), (x2, y2), 4)

                # draw nodes onto overlay (after connections so nodes overlay lines)
                for lvl_idx, nodes in enumerate(graph):
                    for node in nodes:
                        pos = node_positions.get(node['id'])
                        if not pos:
                            continue
                        cx, cy = pos
                        r = node_size // 2
                        t = node.get('type', 'normal')
                        if t == 'elite':
                            color = (80, 180, 80)
                        elif t == 'shop':
                            color = (100, 180, 240)
                        elif t == 'rest':
                            color = (255, 165, 0)
                        elif t == 'treasure':
                            color = (200, 160, 80)
                        elif t == 'boss':
                            color = (200, 60, 60)
                        elif t == 'event':
                            color = (140, 80, 200)
                        else:
                            color = (200, 200, 200)
                        # skip drawing if off-screen to save time
                        if cy + r < 0 or cy - r > settings.SCREEN_HEIGHT:
                            continue
                        pygame.draw.circle(overlay, color, (cx, cy), r)
                        pygame.draw.circle(overlay, (30, 30, 30), (cx, cy), r, 2)
            else:
                # フォールバック: 縦に15個のマスを並べて描画（スクロールで見渡せる）
                count = 15
                node_size = 44
                level_margin = 100
                level_spacing = 200
                cx = settings.SCREEN_WIDTH // 2

                # compute total content height and clamp scroll
                total_height = level_margin * 2 + (count - 1) * level_spacing
                cur_scroll = int(getattr(map_scene, 'overlay_scroll', 0) or 0)
                if cur_scroll < 0:
                    cur_scroll = 0
                max_scroll = max(0, int(total_height - settings.SCREEN_HEIGHT))
                if cur_scroll > max_scroll:
                    cur_scroll = max_scroll

                # draw connecting vertical lines between centers
                line_color = (140, 140, 140)
                line_width = 6
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