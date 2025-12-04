# -*- coding: utf-8 -*-
import pygame
import math
from ...components.character import Character
from ...config import settings
from ...data.status_effect_data import STATUS_EFFECTS
from ...data.permanent_effect_data import PERMANENT_EFFECTS
from ...data.monster_action_data import MONSTER_ACTIONS

class CharacterStatusDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts

    def draw(self, screen: pygame.Surface, character: Character, color: tuple[int, int, int], is_selected_target: bool = False, mouse_pos: tuple[int, int] | None = None):
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
            self._draw_status_effects(screen, character, character.x - 10, status_effects_y, mouse_pos)
        else:
            # 敵の場合
            status_effects_y = hp_bar_y + 25 # HPバーの下
            self._draw_status_effects(screen, character, character.x - 10, status_effects_y, mouse_pos)

        # 敵の場合のみインテントを描画
        if hasattr(character, 'next_action') and character.next_action:
            self._draw_intent(screen, character)

    def _draw_status_effects(self, screen: pygame.Surface, character: Character, x: int, y: int, mouse_pos: tuple[int, int] | None = None):
        icon_radius = 12
        icon_gap = 5
        status_offset_x = 0
        
        font = self.fonts["card"]

        # 攻撃力・防御力変化の描画
        stat_changes = {
            "attack": character.attack_power - character.base_attack_power,
            "defense": character.defense_power - character.base_defense_power
        }

        for stat_name, diff in stat_changes.items():
            if diff == 0:
                continue

            icon_char, base_color = ("A", settings.RED) if stat_name == "attack" else ("D", settings.BLUE)
            text_color = settings.GREEN if diff > 0 else settings.RED
            
            center_x = x + status_offset_x + icon_radius
            center_y = y + icon_radius
            icon_rect = pygame.Rect(center_x - icon_radius, center_y - icon_radius, icon_radius * 2, icon_radius * 2)

            # アイコン背景
            pygame.draw.circle(screen, base_color, (center_x, center_y), icon_radius)
            pygame.draw.circle(screen, settings.WHITE, (center_x, center_y), icon_radius, 1)

            # アイコン文字 (A or D)
            icon_text = self.fonts["small"].render(icon_char, True, settings.WHITE)
            text_rect = icon_text.get_rect(center=(center_x, center_y))
            screen.blit(icon_text, text_rect)

            # 数値
            diff_text_str = f"+{diff}" if diff > 0 else str(diff)
            diff_text = font.render(diff_text_str, True, text_color)
            diff_rect = diff_text.get_rect(midleft=(center_x + icon_radius + 3, center_y))
            screen.blit(diff_text, diff_rect)

            current_icon_width = icon_radius * 2 + icon_gap + diff_text.get_width()
            status_offset_x += current_icon_width

            # if mouse_pos and icon_rect.collidepoint(mouse_pos):
            #     self._draw_tooltip(screen, {"name": "攻撃力" if stat_name == "attack" else "防御力", "description": f"基本値から{diff:+}されています。"}, icon_rect.centerx, icon_rect.top)

        # 永続効果の描画
        for effect_id in character.permanent_effects:
            effect_data = PERMANENT_EFFECTS.get(effect_id)
            if not effect_data: continue

            icon_char = effect_data.get("icon", "?")
            color = effect_data.get("color", settings.WHITE)

            center_x = x + status_offset_x + icon_radius
            center_y = y + icon_radius
            icon_rect = pygame.Rect(center_x - icon_radius, center_y - icon_radius, icon_radius * 2, icon_radius * 2)

            pygame.draw.circle(screen, color, (center_x, center_y), icon_radius)
            pygame.draw.circle(screen, settings.BLACK, (center_x, center_y), icon_radius, 1)

            icon_text = self.fonts["small"].render(icon_char, True, settings.BLACK)
            text_rect = icon_text.get_rect(center=(center_x, center_y))
            screen.blit(icon_text, text_rect)

            status_offset_x += icon_radius * 2 + icon_gap
            if mouse_pos and icon_rect.collidepoint(mouse_pos):
                self._draw_tooltip(screen, effect_data, icon_rect.centerx, icon_rect.top)

        for status_id, turns in character.status_effects.items():
            status_data = STATUS_EFFECTS.get(status_id)
            if not status_data:
                continue

            icon_char = status_data.get("icon", "?")
            color = status_data.get("color", settings.WHITE)

            center_x = x + status_offset_x + icon_radius
            center_y = y + icon_radius
            
            icon_rect = pygame.Rect(center_x - icon_radius, center_y - icon_radius, icon_radius * 2, icon_radius * 2)

            pygame.draw.circle(screen, color, (center_x, center_y), icon_radius)
            pygame.draw.circle(screen, settings.BLACK, (center_x, center_y), icon_radius, 1)

            icon_text = self.fonts["small"].render(icon_char, True, settings.BLACK)
            text_rect = icon_text.get_rect(center=(center_x, center_y))
            screen.blit(icon_text, text_rect)

            current_icon_width = icon_radius * 2

            # 永続効果でない場合のみターン数を描画
            if turns != -1:
                turns_text = font.render(str(turns), True, settings.WHITE)
                turns_rect = turns_text.get_rect(midleft=(center_x + icon_radius + 3, center_y))
                screen.blit(turns_text, turns_rect)
                current_icon_width += icon_gap + turns_text.get_width()
            else:
                current_icon_width += icon_gap
            
            status_offset_x += current_icon_width

            if mouse_pos and icon_rect.collidepoint(mouse_pos):
                self._draw_tooltip(screen, status_data, icon_rect.centerx, icon_rect.top)

    def _draw_tooltip(self, screen: pygame.Surface, status_data: dict, x: int, y: int):
        padding = 5
        font_name = self.fonts["small"]
        font_desc = self.fonts["card"]

        name_text = font_name.render(status_data['name'], True, settings.WHITE)
        desc_text = font_desc.render(status_data['description'], True, settings.WHITE)

        width = max(name_text.get_width(), desc_text.get_width()) + padding * 2
        height = name_text.get_height() + desc_text.get_height() + padding * 2

        tooltip_rect = pygame.Rect(x - width // 2, y - height - 5, width, height)
        
        pygame.draw.rect(screen, settings.DARK_GRAY, tooltip_rect, border_radius=3)
        pygame.draw.rect(screen, settings.WHITE, tooltip_rect, 1, border_radius=3)

        screen.blit(name_text, (tooltip_rect.x + padding, tooltip_rect.y + padding))
        screen.blit(desc_text, (tooltip_rect.x + padding, tooltip_rect.y + padding + name_text.get_height()))

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

        intent_text = ""
        text_color = settings.WHITE # デフォルトの色
        icon = "?" # デフォルト

        # インテントタイプに基づいてアイコンとテキストを決定する
        intent_type = action_data.get("intent_type") # ここでintent_typeを取得

        if intent_type == "attack":
            first_effect = action_data.get("effects", [{}])[0]
            power = first_effect.get("power", 0)
            hits = first_effect.get("hits", 1)
            damage = power + monster.attack_power
            intent_text = f"{damage}x{hits}" if hits > 1 else str(damage)
            text_color = settings.RED
            icon = "⚔"
            if first_effect.get("target_scope") == "all":
                icon = "⚔" # 全体攻撃用アイコン

            # 2つ目以降の効果にデバフがあればアイコンを変更
            if any(e.get("type") == "apply_status" and STATUS_EFFECTS.get(e.get("status_id"), {}).get("is_debuff") for e in action_data.get("effects", [])[1:]):
                icon = "⚔↓"

        elif intent_type == "attack_debuff":
            first_effect = action_data.get("effects", [{}])[0]
            power = first_effect.get("power", 0)
            hits = first_effect.get("hits", 1)
            damage = power + monster.attack_power
            intent_text = f"{damage}x{hits}" if hits > 1 else str(damage)
            text_color = settings.RED
            icon = "⚔↓"

        elif intent_type == "sanity_attack":
            first_effect = action_data.get("effects", [{}])[0]
            intent_text = str(first_effect.get("power", 0))
            text_color = settings.YELLOW
            icon = "🌀" # 正気度攻撃用のアイコン

        elif intent_type == "debuff":
            icon = "↓" # デバフ全般のアイコン
            # 具体的なデバフをintent_textに表示することも可能

        elif intent_type == "defense":
            icon = "🛡" # 防御アイコン
            # 防御量をintent_textに表示することも可能

        elif intent_type == "conversation": # ここを追加
            icon = "💬" # 会話イベント用のアイコン
            intent_text = "" # 会話の場合はテキスト不要、または「会話」と表示しても良い
            text_color = settings.BLUE # 会話用の色

        elif intent_type == "unknown" or intent_type == "wait": # waitもunknownにまとめる
            icon = "..." # 何もしない、または不明な行動

        # インテントの描画
        full_text = f"{icon} {intent_text}".strip()
        text_surface = self.fonts["medium"].render(full_text, True, text_color)
        text_rect = text_surface.get_rect(centerx=monster.x + 40, bottom=monster.y - 10)
        screen.blit(text_surface, text_rect)