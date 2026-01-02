# -*- coding: utf-8 -*-
import pygame
from ...scenes.battle_scene import BattleScene
from ...config import settings
from ...data.relic_data import RELICS

class RelicDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.relic_radius = 15 # 半径を小さくする
        self.relic_gap = 10

    def get_relic_rect(self, index: int) -> pygame.Rect:
        """指定されたインデックスのレリックアイコンのRectを返す"""
        x = self.relic_gap + index * (self.relic_radius * 2 + self.relic_gap)
        y = self.relic_gap
        return pygame.Rect(x, y, self.relic_radius * 2, self.relic_radius * 2)

    def draw(self, screen: pygame.Surface, battle_state: BattleScene):
        # レリックアイコンの描画
        for i, relic_id in enumerate(battle_state.player.relics):
            relic_data = RELICS.get(relic_id)
            if not relic_data:
                continue
            
            relic_rect = self.get_relic_rect(i)
            # 残り使用回数が0ならグレーアウト
            remaining = getattr(battle_state.player, 'relic_uses_remaining', {}).get(relic_id, None)
            draw_color = relic_data["color"] if (remaining is None or remaining > 0) else settings.GRAY
            pygame.draw.circle(screen, draw_color, relic_rect.center, self.relic_radius)
            pygame.draw.circle(screen, settings.WHITE, relic_rect.center, self.relic_radius, 2)

        # 拡大表示
        if battle_state.hovered_relic_index is not None:
            relic_id = battle_state.player.relics[battle_state.hovered_relic_index]
            self._draw_enlarged_relic(screen, relic_id)

    def _draw_enlarged_relic(self, screen: pygame.Surface, relic_id: str):
        relic_data = RELICS.get(relic_id)
        if not relic_data:
            return

        width, height = 300, 150
        x = (screen.get_width() - width) / 2
        y = (screen.get_height() - height) / 2
        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(screen, (40, 40, 60), rect, border_radius=10)
        pygame.draw.rect(screen, settings.WHITE, rect, 2, border_radius=10)

        name_text = self.fonts["medium"].render(relic_data["name"], True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=rect.centerx, y=rect.top + 15)
        screen.blit(name_text, name_rect)
        # 残り使用回数表示
        remaining = getattr(screen, 'battle_scene_player_relic_uses', None)
        try:
            # 直接参照できる場合はbattle_stateから取得する
            pass
        except Exception:
            pass
        desc_rect = pygame.Rect(rect.x + 20, name_rect.bottom + 10, rect.width - 40, rect.height - name_rect.height - 30)
        
        lines = relic_data["description"].splitlines()
        line_y = desc_rect.y
        for line in lines:
            line_surface = self.fonts["small"].render(line, True, settings.WHITE)
            line_rect = line_surface.get_rect(centerx=rect.centerx, top=line_y)
            screen.blit(line_surface, line_rect)
            line_y += line_surface.get_height()
        # もしプレイヤーの残り使用回数があれば表示
        try:
            from ...config import settings as _s
            player = None
        except Exception:
            player = None