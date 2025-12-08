# -*- coding: utf-8 -*-
import pygame
import os
import time
from ..components.monster import Monster
from ..config import settings
from ..scenes.battle_scene import BattleScene
from ..components.character import Character
from .drawers.character_status_drawer import CharacterStatusDrawer
from .drawers.player_command_drawer import PlayerCommandDrawer # 既存の行
from .drawers.damage_indicator import DamageIndicator # インポートパスを修正
from .drawers.relic_drawer import RelicDrawer

class BattleView:
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("RPG戦闘")
        
        self.fonts = self._load_fonts()
        self.status_drawer = CharacterStatusDrawer(self.fonts)
        self.command_drawer = PlayerCommandDrawer(self.fonts)
        self.relic_drawer = RelicDrawer(self.fonts)
        self.damage_animations = []
        self.last_known_hp = {}

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
            "bar": self._get_japanese_font(12),
        }

    def draw(self, battle_state: BattleScene):
        # 1. 常に戦闘シーンの基本要素（背景、キャラクターなど）を描画
        if battle_state.background_image:
            self.screen.blit(battle_state.background_image, (0, 0))
        else:
            self.screen.fill(settings.BLACK)
        
        self._check_for_damage(battle_state.player)
        for enemy in battle_state.enemy_manager.enemies:
            self._check_for_damage(enemy)

        mouse_pos = pygame.mouse.get_pos()
        self.status_drawer.draw(self.screen, battle_state.player, settings.BLUE, False, mouse_pos)
        for i, enemy in enumerate(battle_state.enemy_manager.enemies):
            if enemy.is_alive:
                is_selected = (i == battle_state.targeted_enemy_index)
                self.status_drawer.draw(self.screen, enemy, settings.RED, is_selected, mouse_pos)
        
        self.relic_drawer.draw(self.screen, battle_state)

        # 2. アクティブなシーンに応じて、会話か戦闘UIかを描画
        if battle_state.current_scene != battle_state:
            # 会話シーンがアクティブな場合
            battle_state.current_scene.draw(self.screen)
        else:
            # 戦闘シーンがアクティブな場合
            self._draw_ui(battle_state)
        
        # 3. ダメージアニメーションを常に最前面に描画
        self._update_and_draw_animations()

        # 4. 画面を更新
        pygame.display.flip()

    def _check_for_damage(self, character: Character):
        char_id = id(character)
        current_hp = character.current_hp
        
        if char_id not in self.last_known_hp:
            self.last_known_hp[char_id] = current_hp
            return

        last_hp = self.last_known_hp[char_id]
        if current_hp < last_hp:
            damage = last_hp - current_hp
            # character_status_drawer と同じ計算でキャラクター幅を求める
            char_width = int(settings.SCREEN_WIDTH * 0.08)
            pos = (character.x + char_width // 2, character.y) 
            color = settings.DAMAGE_RED
            font = self.fonts["medium"]
            self.damage_animations.append(DamageIndicator(str(damage), pos, color, font))

        self.last_known_hp[char_id] = current_hp

    def _update_and_draw_animations(self):
        # 生きているアニメーションのみを保持
        self.damage_animations = [anim for anim in self.damage_animations if anim.is_alive]
        for anim in self.damage_animations:
            anim.update()
            anim.draw(self.screen)

    def _draw_ui(self, battle_state: BattleScene):
        if battle_state.turn == "player":
            turn_text = self.fonts["medium"].render("プレイヤーのターン", True, settings.YELLOW)
        else:
            turn_text = self.fonts["medium"].render("敵のターン", True, settings.RED)
        self.screen.blit(turn_text, (settings.SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 20))
        
        # --- UIエリアのレイアウト ---
        command_area_height = int(settings.SCREEN_HEIGHT / 4)
        command_area_y = settings.SCREEN_HEIGHT - command_area_height
        command_area_rect = pygame.Rect(0, command_area_y, settings.SCREEN_WIDTH, command_area_height)

        # ターン終了ボタンの描画 (プレイヤーのターン中のみ)
        if battle_state.turn == "player" and not battle_state.game_over:
            button_width = int(settings.SCREEN_WIDTH * 0.12)
            button_height = int(command_area_height * 0.2)
            button_x = settings.SCREEN_WIDTH - button_width - int(settings.SCREEN_WIDTH * 0.1)
            button_y = command_area_y - button_height - int(command_area_height * 0.05)
            end_turn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            pygame.draw.rect(self.screen, (100, 0, 0), end_turn_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, settings.WHITE, end_turn_button_rect, 2, border_radius=5)
            
            button_text = self.fonts["small"].render("ターン終了", True, settings.WHITE)
            text_rect = button_text.get_rect(center=end_turn_button_rect.center)
            self.screen.blit(button_text, text_rect)

        # デッキと捨て札の枚数を描画
        if not battle_state.game_over:
            deck_count = len(battle_state.deck_manager.deck) if battle_state.deck_manager else 0
            discard_count = len(battle_state.deck_manager.discard_pile) if battle_state.deck_manager else 0
            
            deck_text = self.fonts["small"].render(f"山札: {deck_count}", True, settings.WHITE)
            deck_pos_x = int(settings.SCREEN_WIDTH * 0.02)
            deck_pos_y = settings.SCREEN_HEIGHT - int(settings.SCREEN_HEIGHT * 0.06)
            self.screen.blit(deck_text, (deck_pos_x, deck_pos_y))

            discard_text = self.fonts["small"].render(f"捨て札: {discard_count}", True, settings.WHITE)
            discard_pos_x = settings.SCREEN_WIDTH - int(settings.SCREEN_WIDTH * 0.02)
            discard_pos_y = settings.SCREEN_HEIGHT - int(settings.SCREEN_HEIGHT * 0.03)
            discard_rect = discard_text.get_rect(right=discard_pos_x, bottom=discard_pos_y)
            self.screen.blit(discard_text, discard_rect)

        # プレイヤーのターンならコマンドを描画
        if battle_state.turn == "player" and not battle_state.game_over:
            self.command_drawer.draw(self.screen, battle_state, command_area_rect)
        
        if battle_state.game_over:
            if battle_state.winner == "player":
                result_text = self.fonts["large"].render("勝利！", True, settings.GREEN)
            else:
                result_text = self.fonts["large"].render("敗北...", True, settings.RED)
            
            result_rect = result_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(result_text, result_rect)

            if battle_state.reward_gold > 0:
                gold_text = self.fonts["medium"].render(f"{battle_state.reward_gold} ゴールド獲得", True, settings.YELLOW)
                gold_rect = gold_text.get_rect(center=(settings.SCREEN_WIDTH // 2, result_rect.bottom + 30))
                self.screen.blit(gold_text, gold_rect)
            
            restart_text = self.fonts["medium"].render("Rキー: マップに戻る", True, settings.WHITE)
            restart_rect = restart_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)