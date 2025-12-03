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

        self._draw_hp_bar(screen, character, character.x - 10, hp_bar_y, 100, 15)
        self._draw_defense_buff(screen, character, character.x - 10, hp_bar_y)

        # プレイヤーの場合のみ正気度とマナを描画
        if character.max_mana > 0 and character.max_sanity is not None:
            sanity_bar_y = hp_bar_y + 30 # HPバーと正気度バーの間隔
            mana_orbs_y = sanity_bar_y + 30 # 正気度バーとマナの間隔
            status_effects_y = mana_orbs_y + 30 # マナと状態異常の間隔

            san_text = self.fonts["small"].render(f"SAN: {character.current_sanity}/{character.max_sanity}", True, settings.WHITE)
            screen.blit(san_text, (character.x - 10, hp_bar_y + 5))
            self._draw_sanity_bar(screen, character, character.x - 10, sanity_bar_y, 100, 15)
            self._draw_mana_orbs(screen, character, character.x - 10, mana_orbs_y)
            self._draw_status_effects(screen, character, character.x - 10, status_effects_y)
        else:
            # 敵の場合
            status_effects_y = hp_bar_y + 25 # HPバーの下
            self._draw_status_effects(screen, character, character.x - 10, status_effects_y)

        # 敵の場合のみインテントを描画
        if hasattr(character, 'next_action') and character.next_action:
            self._draw_intent(screen, character)

    def _draw_status_effects(self, screen: pygame.Surface, character: Character, x: int, y: int):
        icon_radius = 12
        icon_gap = 5
        status_offset_x = 0
        
        font = self.fonts["card"] # 小さめのフォントを使用

        for status_id, turns in character.status_effects.items():
            status_data = STATUS_EFFECTS.get(status_id)
            if not status_data:
                continue

            icon_char = status_data.get("icon", "?")
            color = status_data.get("color", settings.WHITE)

            # アイコンの円を描画
            center_x = x + status_offset_x + icon_radius
            center_y = y + icon_radius
            pygame.draw.circle(screen, color, (center_x, center_y), icon_radius)
            pygame.draw.circle(screen, settings.BLACK, (center_x, center_y), icon_radius, 1)

            # アイコン文字を描画
            icon_text = self.fonts["small"].render(icon_char, True, settings.BLACK)
            text_rect = icon_text.get_rect(center=(center_x, center_y))
            screen.blit(icon_text, text_rect)

            # ターン数を描画
            turns_text = font.render(str(turns), True, settings.WHITE)
            turns_rect = turns_text.get_rect(midleft=(center_x + icon_radius + 3, center_y))
            screen.blit(turns_text, turns_rect)
            
            status_offset_x += (icon_radius * 2) + icon_gap + turns_text.get_width()

    def _draw_hp_bar(self, screen: pygame.Surface, character: Character, x: int, y: int, width: int, height: int):
        pygame.draw.rect(screen, settings.DARK_GRAY, (x, y, width, height))
        hp_percentage = character.get_hp_percentage()
        hp_bar_width = (width * hp_percentage) / 100
        
        bar_color = settings.RED
        if hp_percentage > 50: bar_color = settings.GREEN
        elif hp_percentage > 25: bar_color = settings.YELLOW
        
        pygame.draw.rect(screen, bar_color, (x, y, hp_bar_width, height))
        pygame.draw.rect(screen, settings.WHITE, (x, y, width, height), 1)

    def _draw_sanity_bar(self, screen: pygame.Surface, character: Character, x: int, y: int, width: int, height: int):
        pygame.draw.rect(screen, settings.DARK_GRAY, (x, y, width, height))
        sanity_percentage = character.get_sanity_percentage() if character.current_sanity is not None else 0
        sanity_bar_width = (width * sanity_percentage) / 100
        pygame.draw.rect(screen, settings.YELLOW, (x, y, sanity_bar_width, height))
        pygame.draw.rect(screen, settings.WHITE, (x, y, width, height), 1)

    def _draw_defense_buff(self, screen: pygame.Surface, character: Character, x: int, y: int):
        if character.defense_buff > 0:
            radius = 15
            circle_x = x + 100 + radius + 5  # HPバーの右側に配置
            circle_y = y + 7 # HPバーの高さの中心に合わせる
            
            # 白い丸
            pygame.draw.circle(screen, settings.WHITE, (circle_x, circle_y), radius)
            
            # 黒い文字
            font = self.fonts["small"]
            text = font.render(str(character.defense_buff), True, settings.BLACK)
            text_rect = text.get_rect(center=(circle_x, circle_y))
            screen.blit(text, text_rect)

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
        text_color = settings.WHITE # デフォルトの色
        icon = "?" # デフォルト

        if intent_type == "attack":
            power = action_data["power"]
            damage = int(monster.attack_power * power)
            intent_text = str(damage)
            text_color = settings.RED # 物理ダメージは赤
            icon = "⚔"
        elif intent_type == "sanity_attack":
            power = action_data["power"]
            intent_text = str(power)
            text_color = settings.YELLOW # 正気度ダメージは黄色
            icon = "⚔"
        elif intent_type == "attack_debuff":
            power = action_data["power"]
            damage = int(monster.attack_power * power)
            intent_text = str(damage)
            text_color = settings.RED # 物理＋デバフも赤
            icon = "⚔" # アイコンは攻撃と同じ
        elif intent_type == "debuff":
            icon = "↓"
        elif intent_type == "unknown":
            text_color = settings.LIGHT_GRAY

        full_text = f"{icon} {intent_text}"
        text_surface = self.fonts["medium"].render(full_text, True, text_color)
        text_rect = text_surface.get_rect(centerx=monster.x + 40, bottom=monster.y - 10)
        screen.blit(text_surface, text_rect)