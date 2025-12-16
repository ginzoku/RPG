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
from .drawers.deck_viewer_drawer import DeckViewerDrawer
from .drawers.discovery_drawer import DiscoveryDrawer

class BattleView:
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("RPG戦闘")
        
        self.fonts = self._load_fonts()
        self.status_drawer = CharacterStatusDrawer(self.fonts)
        self.command_drawer = PlayerCommandDrawer(self.fonts)
        self.relic_drawer = RelicDrawer(self.fonts)
        self.deck_viewer_drawer = DeckViewerDrawer(self.fonts)
        self.discovery_drawer = DiscoveryDrawer(self.fonts)
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
            name: self._get_japanese_font(size)
            for name, size in settings.FONT_SIZES.items()
        }

    def draw(self, battle_state: BattleScene):
        # BattleSceneに deck_viewer_drawer を設定（初回のみ）
        if battle_state.deck_viewer_drawer is None:
            battle_state.deck_viewer_drawer = self.deck_viewer_drawer
        
        # 1. 常に戦闘シーンの基本要素（背景、キャラクターなど）を描画
        if battle_state.background_image:
            self.screen.blit(battle_state.background_image, (0, 0))
        else:
            self.screen.fill(settings.BLACK)
        
        self._check_for_damage(battle_state.player)
        for enemy in battle_state.enemy_manager.enemies:
            self._check_for_damage(enemy)

        self._update_hit_animation(battle_state.player) # Call for player
        for enemy in battle_state.enemy_manager.enemies:
            self._update_hit_animation(enemy) # Call for each enemy

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
        
        # 山札ビューが表示中の場合
        if battle_state.showing_deck_viewer:
            # デッキ変換ルールがある場合は変換後の表示を行う
            effective_deck = battle_state.deck_manager.get_effective_deck()
            # suppress title text for a cleaner UI
            self.deck_viewer_drawer.draw(self.screen, effective_deck, battle_state.player, title="")

        # 捨て札ビューが表示中の場合
        if getattr(battle_state, 'showing_discard_viewer', False):
            effective_discard = battle_state.deck_manager.get_effective_deck() if hasattr(battle_state.deck_manager, 'get_effective_deck') else battle_state.deck_manager.discard_pile
            # get_effective_deck returns transformed view for the deck; for discard we need to map discard_pile as well
            if hasattr(battle_state.deck_manager, 'get_effective_card_id'):
                effective_discard = [battle_state.deck_manager.get_effective_card_id(cid) for cid in battle_state.deck_manager.discard_pile]
            # suppress title text for a cleaner UI
            self.deck_viewer_drawer.draw(self.screen, effective_discard, battle_state.player, title="")

        # 発見カード選択画面が表示中の場合
        if battle_state.deck_manager and battle_state.deck_manager.is_discovering:
            card_rects = self.discovery_drawer.draw(self.screen, battle_state.deck_manager.discovered_cards, battle_state.player)
            battle_state.set_discovery_card_rects(card_rects)
        
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

    def _update_hit_animation(self, character: Character):
        if not character.is_hit_animating:
            return

        elapsed_time = pygame.time.get_ticks() - character.hit_animation_start_time
        duration_ms = character.hit_animation_duration * 1000

        if elapsed_time < duration_ms:
            progress = elapsed_time / duration_ms
            
            # スライドは最初動いて最後戻る
            # 0 -> 1 -> 0 のプログレス
            # 例: 0.2秒のアニメーションなら、0.1秒で最大距離に達し、0.2秒で元の位置に戻る
            if progress <= 0.5:
                current_progress = progress * 2 # 0 -> 1
            else:
                current_progress = (1 - progress) * 2 # 1 -> 0
            
            slide_distance = settings.ANIMATION_SETTINGS["hit_slide"]["distance"]
            offset = slide_distance * character.hit_animation_direction * current_progress
            character.x = character.original_x + offset
        else:
            character.is_hit_animating = False
            character.x = character.original_x # アニメーション終了時には元の位置に戻す

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
            
            # Draw discard pile as a button-like indicator (right-bottom) and expose its rect.
            btn_w, btn_h = 140, 44
            discard_rect = pygame.Rect(settings.SCREEN_WIDTH - btn_w - 10, settings.SCREEN_HEIGHT - btn_h - 20, btn_w, btn_h)
            pygame.draw.rect(self.screen, (50, 50, 70), discard_rect, border_radius=6)
            pygame.draw.rect(self.screen, settings.WHITE, discard_rect, 2, border_radius=6)
            # show discard count instead of fixed label
            try:
                discard_count = len(battle_state.deck_manager.discard_pile) if getattr(battle_state, 'deck_manager', None) else 0
            except Exception:
                discard_count = 0
            label = self.fonts["small"].render(str(discard_count), True, (0, 0, 0))
            label_rect = label.get_rect(center=discard_rect.center)
            self.screen.blit(label, label_rect)
            battle_state.discard_indicator_rect = discard_rect

        # プレイヤーのターンならコマンドを描画
        if battle_state.turn == "player" and not battle_state.game_over:
            self.command_drawer.draw(self.screen, battle_state, command_area_rect)
        # 一時表示メッセージ（例: マナが足りない！）を描画
        try:
            import pygame as _pygame
            now = _pygame.time.get_ticks()
        except Exception:
            now = 0

        if getattr(battle_state, 'transient_message', None):
            expire_at = getattr(battle_state, 'transient_message_expire_at', 0)
            if now >= expire_at:
                battle_state.transient_message = None
            else:
                msg = battle_state.transient_message
                # 中央上寄せに半透明パネルで表示
                surf = self.fonts['medium'].render(msg, True, settings.WHITE)
                rect = surf.get_rect(center=(settings.SCREEN_WIDTH // 2, command_area_rect.top - 60))
                panel = _pygame.Surface((rect.width + 20, rect.height + 12), _pygame.SRCALPHA)
                panel.fill((20, 20, 30, 200))
                panel_rect = panel.get_rect(center=rect.center)
                self.screen.blit(panel, panel_rect.topleft)
                pygame.draw.rect(self.screen, settings.WHITE, panel_rect, 1, border_radius=6)
                self.screen.blit(surf, rect)
        
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