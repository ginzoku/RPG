# -*- coding: utf-8 -*-
import pygame
import os
from ..components.monster import Monster
from ..config import settings
from ..scenes.battle_scene import BattleScene
from ..components.character import Character
from .drawers.character_status_drawer import CharacterStatusDrawer
from .drawers.player_command_drawer import PlayerCommandDrawer
from .drawers.relic_drawer import RelicDrawer

class BattleView:
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("RPG戦闘")
        
        self.fonts = self._load_fonts()
        self.status_drawer = CharacterStatusDrawer(self.fonts)
        self.command_drawer = PlayerCommandDrawer(self.fonts)
        self.relic_drawer = RelicDrawer(self.fonts)

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def _load_fonts(self) -> dict:
        return {
            "large": self._get_japanese_font(48),
            "medium": self._get_japanese_font(36),
            "small": self._get_japanese_font(24),
            "log": self._get_japanese_font(20),
            "card": self._get_japanese_font(18),
        }

    def draw(self, battle_state: BattleScene):
        self.screen.fill(settings.BLACK)
        
        self.status_drawer.draw(self.screen, battle_state.player, settings.BLUE)
        self.status_drawer.draw(self.screen, battle_state.enemy, settings.RED)
        self.relic_drawer.draw(self.screen, battle_state)
        self._draw_ui(battle_state)
        
        pygame.display.flip()

    def _draw_ui(self, battle_state: BattleScene):
        if battle_state.turn == "player":
            turn_text = self.fonts["medium"].render("プレイヤーのターン", True, settings.YELLOW)
        else:
            turn_text = self.fonts["medium"].render("敵のターン", True, settings.RED)
        self.screen.blit(turn_text, (settings.SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 20))
        
        # --- UIエリアのレイアウト調整 ---
        padding = 10
        
        # ログエリア
        log_area_height = int(settings.SCREEN_HEIGHT / 4)
        log_area_y = settings.SCREEN_HEIGHT - log_area_height
        log_area_rect = pygame.Rect(0, log_area_y, settings.SCREEN_WIDTH, log_area_height)

        # ターン終了ボタンの描画 (プレイヤーのターン中のみ)
        if battle_state.turn == "player" and not battle_state.game_over:
            button_width = 120
            button_height = 40
            button_x = settings.SCREEN_WIDTH - button_width - 150 # 捨て札表示と被らないように左にずらす
            button_y = log_area_y - button_height - 10 # ログエリアの上に配置
            end_turn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            pygame.draw.rect(self.screen, (100, 0, 0), end_turn_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, settings.WHITE, end_turn_button_rect, 2, border_radius=5)
            
            button_text = self.fonts["small"].render("ターン終了", True, settings.WHITE)
            text_rect = button_text.get_rect(center=end_turn_button_rect.center)
            self.screen.blit(button_text, text_rect)

        # プレイヤーのターンでない時だけログエリアの背景を描画
        if battle_state.turn != "player":
            pygame.draw.rect(self.screen, settings.DARK_GRAY, log_area_rect)
            pygame.draw.rect(self.screen, settings.WHITE, log_area_rect, 2)

        # デッキと捨て札の枚数を描画
        if not battle_state.game_over:
            deck_count = len(battle_state.deck_manager.deck) if battle_state.deck_manager else 0
            discard_count = len(battle_state.deck_manager.discard_pile) if battle_state.deck_manager else 0
            
            deck_text = self.fonts["small"].render(f"山札: {deck_count}", True, settings.WHITE)
            self.screen.blit(deck_text, (log_area_rect.left + 20, log_area_rect.top - 40))

            discard_text = self.fonts["small"].render(f"捨て札: {discard_count}", True, settings.WHITE)
            discard_rect = discard_text.get_rect(right=log_area_rect.right - 20, top=log_area_rect.top - 40)
            self.screen.blit(discard_text, discard_rect)

        # プレイヤーのターンならコマンドを描画
        if battle_state.turn == "player" and not battle_state.game_over:
            self.command_drawer.draw(self.screen, battle_state, log_area_rect)
        else:
            # それ以外の場合はバトルログを描画
            self._draw_battle_log(battle_state, log_area_rect)
        
        if battle_state.game_over:
            if battle_state.winner == "player":
                result_text = self.fonts["large"].render("勝利！", True, settings.GREEN)
            else:
                result_text = self.fonts["large"].render("敗北...", True, settings.RED)
            
            result_rect = result_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(result_text, result_rect)
            
            restart_text = self.fonts["medium"].render("Rキー: リスタート", True, settings.WHITE)
            restart_rect = restart_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

    def _draw_battle_log(self, battle_state: BattleScene, log_area_rect: pygame.Rect):
        padding = 10
        start_x = log_area_rect.left + padding
        drawable_height = log_area_rect.height - (padding * 2)
        line_height = drawable_height // battle_state.max_log_lines if battle_state.max_log_lines > 0 else drawable_height
        start_y = log_area_rect.top + padding + (line_height - self.fonts["log"].get_height()) // 2

        for i, message in enumerate(battle_state.battle_log):
            log_text = self.fonts["log"].render(message, True, settings.LIGHT_BLUE)
            self.screen.blit(log_text, (start_x, start_y + i * line_height))