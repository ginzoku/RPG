# -*- coding: utf-8 -*-
import pygame
import math
from ...components.character import Character
from ...config import settings
from ...data.status_effect_data import STATUS_EFFECTS
from ...data.monster_action_data import MONSTER_ACTIONS

class CharacterStatusDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts

    def draw(self, screen: pygame.Surface, character: Character, color: tuple[int, int, int], is_selected_target: bool = False):
        """キャラクターのステータス全体を描画するメインメソッド"""
        char_width = 80
        char_height = 100
        
        # キャラクター本体の四角形を描画
        pygame.draw.rect(screen, color, (character.x, character.y, char_width, char_height))
        
        # --- 枠線の描画ロジック ---
        # ターゲット選択中にマウスホバーされている場合のハイライト
        border_color = settings.WHITE
        border_width = 2
        if hasattr(character, 'is_targeted') and character.is_targeted:
            border_color = settings.YELLOW
            border_width = 4
        
        # ターゲットとして選択されている場合のハイライト (ホバーより優先)
        if is_selected_target:
            border_color = settings.YELLOW
            border_width = 4
        pygame.draw.rect(screen, border_color, (character.x, character.y, char_width, char_height), border_width)
        
        # name_text = self.fonts["medium"].render(character.name, True, settings.WHITE)
        # screen.blit(name_text, (character.x - 20, character.y - 40))
        
        hp_text = self.fonts["small"].render(f"HP: {character.current_hp}/{character.max_hp}", True, settings.WHITE)
        screen.blit(hp_text, (character.x - 10, character.y + char_height + 5))

        # --- UI要素のY座標を整理 ---
        base_y = character.y + char_height + 5
        hp_bar_y = base_y + 30  # HPテキストとHPバーの間隔
        mana_orbs_y = hp_bar_y + 30 # HPバーとマナの間隔
        status_effects_y = mana_orbs_y + 30 # マナと状態異常の間隔

        # プレイヤーの場合のみマナオーブを描画
        if character.max_mana > 0:
            self._draw_mana_orbs(screen, character, character.x - 10, mana_orbs_y)

        self._draw_status_effects(screen, character, character.x - 10, status_effects_y)
        self._draw_hp_bar(screen, character, character.x - 10, hp_bar_y, 100, 15)

        # 敵の場合のみインテントを描画
        if hasattr(character, 'next_action') and character.next_action:
            self._draw_intent(screen, character)

    def _draw_status_effects(self, screen: pygame.Surface, character: Character, x: int, y: int):
        status_offset = 0
        for status_id, turns in character.status_effects.items():
            status_data = STATUS_EFFECTS[status_id]
            status_text = self.fonts["small"].render(f"{status_data['name']}: {turns}", True, status_data['color'])
            screen.blit(status_text, (x, y + status_offset))
            status_offset += 25

    def _draw_hp_bar(self, screen: pygame.Surface, character: Character, x: int, y: int, width: int, height: int):
        pygame.draw.rect(screen, settings.DARK_GRAY, (x, y, width, height))
        hp_percentage = character.get_hp_percentage()
        hp_bar_width = (width * hp_percentage) / 100
        
        bar_color = settings.RED
        if hp_percentage > 50: bar_color = settings.GREEN
        elif hp_percentage > 25: bar_color = settings.YELLOW
        
        pygame.draw.rect(screen, bar_color, (x, y, hp_bar_width, height))
        pygame.draw.rect(screen, settings.WHITE, (x, y, width, height), 1)

    def _draw_mana_orbs(self, screen: pygame.Surface, character: Character, x: int, y: int):
        orb_radius = 10
        orb_gap = 5
        for i in range(character.max_mana):
            orb_x = x + i * (orb_radius * 2 + orb_gap) + orb_radius
            if i < character.current_mana:
                color = settings.YELLOW
            else:
                color = settings.DARK_GRAY
            pygame.draw.circle(screen, color, (orb_x, y), orb_radius)
            pygame.draw.circle(screen, settings.WHITE, (orb_x, y), orb_radius, 1)

    def _draw_intent(self, screen: pygame.Surface, monster: Character):
        action_id = monster.next_action
        action_data = MONSTER_ACTIONS.get(action_id)
        if not action_data:
            return

        intent_type = action_data.get("intent_type", "unknown")
        intent_text = ""
        icon = "?" # デフォルト

        if intent_type == "attack":
            power = action_data["power"]
            damage = int(monster.attack_power * power)
            intent_text = str(damage)
            icon = "⚔"
        elif intent_type == "attack_debuff":
            power = action_data["power"]
            damage = int(monster.attack_power * power)
            intent_text = str(damage)
            icon = "⚔" # アイコンは攻撃と同じ
        elif intent_type == "debuff":
            icon = "↓"

        full_text = f"{icon} {intent_text}"
        text_surface = self.fonts["medium"].render(full_text, True, settings.WHITE)
        text_rect = text_surface.get_rect(centerx=monster.x + 40, bottom=monster.y - 10)
        screen.blit(text_surface, text_rect)