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

        if current > 0:
            # 黒いオーバーレイ背景を描画（アルファ付き）
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags=pygame.SRCALPHA)
            bg = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            bg.fill((0, 0, 0))
            bg.set_alpha(int(current))
            overlay.blit(bg, (0, 0))
            # overlay をまず画面に貼る（これが黒い View）
            self.screen.blit(overlay, (0, 0))

            # ---- 縦方向チェイン描画: ■ (line) ■ (line) ■ ----
            count = self.chain_count
            sq = self.chain_square
            spacing = self.chain_spacing
            total_height = count * sq + (count - 1) * spacing
            # スクロールは controller が設定する target に滑らかに補間して追従する
            cur = float(getattr(map_scene, 'overlay_scroll', 0) or 0)
            target = float(getattr(map_scene, 'overlay_scroll_target', cur) or cur)
            # clamp target to valid range
            max_scroll = max(0, total_height - (settings.SCREEN_HEIGHT - self.chain_top_margin - 40))
            if target < 0:
                target = 0
            if target > max_scroll:
                target = max_scroll
            map_scene.overlay_scroll_target = target
            # interpolate current toward target for smooth motion
            smoothing = 0.6
            cur += (target - cur) * smoothing
            # snap when near
            if abs(target - cur) < 0.5:
                cur = target
            map_scene.overlay_scroll = cur
            # 初期Y位置（トップマージンから現在のスクロール値を引く）
            start_y = self.chain_top_margin - cur
            cx = settings.SCREEN_WIDTH // 2

            # 線は各四角の間に個別のセグメントとして描く（四角と重ならないよう上下にギャップを設ける）
            line_x = cx  # 四角と同じ水平中心に配置
            line_color = (180, 180, 180)
            line_width = 6
            gap = 12  # 四角と線の間のギャップ（px）

            # 各四角の下端と次の四角の上端の間に線を引く（線が四角と重ならない）
            for i in range(count - 1):
                sq_top = start_y + i * (sq + spacing)
                next_top = start_y + (i + 1) * (sq + spacing)
                seg_start = sq_top + sq + gap
                seg_end = next_top - gap
                # seg_end が seg_start より小さければ描画しない（間隔不足）
                if seg_end <= seg_start:
                    continue
                # 画面外はスキップ
                if seg_end < 0 or seg_start > settings.SCREEN_HEIGHT:
                    continue
                pygame.draw.line(self.screen, line_color, (line_x, seg_start), (line_x, seg_end), line_width)

            # 次に四角を描く
            for i in range(count):
                y = start_y + i * (sq + spacing)
                rect = pygame.Rect(cx - sq // 2, y, sq, sq)
                if rect.bottom < 0 or rect.top > settings.SCREEN_HEIGHT:
                    continue
                # 最下の四角（最後の要素）は赤くする
                if i == count - 1:
                    fill_color = (200, 60, 60)
                    border_color = (150, 20, 20)
                else:
                    fill_color = (220, 220, 220)
                    border_color = (30, 30, 30)
                pygame.draw.rect(self.screen, fill_color, rect, border_radius=6)
                pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)

        # 右上アイコンを描画（オーバーレイの上に表示するため、ここで描く）
        icon_rect = pygame.Rect(settings.SCREEN_WIDTH - self.icon_margin - self.icon_size, self.icon_margin, self.icon_size, self.icon_size)
        pygame.draw.rect(self.screen, (40, 40, 40), icon_rect, border_radius=6)  # ダークグレーの背景
        inner = icon_rect.inflate(-self.icon_size // 4, -self.icon_size // 4)
        pygame.draw.rect(self.screen, (200, 200, 200), inner, border_radius=4)

        # NOTE: do not call `pygame.display.flip()` here — the main loop performs a single flip per frame.