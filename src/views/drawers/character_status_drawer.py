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
        sanity_bar_y = hp_bar_y + 30 # HPバーと正気度バーの間隔
        mana_orbs_y = sanity_bar_y + 30 # 正気度バーとマナの間隔
        status_effects_y = mana_orbs_y + 30 # マナと状態異常の間隔

        self._draw_hp_bar(screen, character, character.x - 10, hp_bar_y, 100, 15)
        self._draw_defense_buff(screen, character, character.x - 10, hp_bar_y)

        # プレイヤーの場合のみ正気度とマナを描画 (マナの有無で判定)
        if character.max_mana > 0 and character.max_sanity is not None:
            san_text = self.fonts["small"].render(f"SAN: {character.current_sanity}/{character.max_sanity}", True, settings.WHITE)
            screen.blit(san_text, (character.x - 10, hp_bar_y + 5))
            self._draw_sanity_bar(screen, character, character.x - 10, sanity_bar_y, 100, 15)
            self._draw_mana_orbs(screen, character, character.x - 10, mana_orbs_y)

        self._draw_status_effects(screen, character, character.x - 10, status_effects_y, is_player=(character.max_mana > 0))

        # 敵の場合のみインテントを描画
        if hasattr(character, 'next_action') and character.next_action:
            self._draw_intent(screen, character)
    
    def draw_tooltip(self, screen: pygame.Surface, character: Character, status_id: str):
        """状態異常のツールチップを描画する"""
        status_data = STATUS_EFFECTS.get(status_id)
        if not status_data:
            return

        width, height = 250, 100
        x = (screen.get_width() - width) / 2
        y = (screen.get_height() - height) / 2
        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(screen, (40, 40, 60), rect, border_radius=10)
        pygame.draw.rect(screen, settings.WHITE, rect, 2, border_radius=10)

        name_text = self.fonts["medium"].render(f"{status_data['name']} ({character.status_effects[status_id]})", True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=rect.centerx, y=rect.top + 15)
        screen.blit(name_text, name_rect)

        desc_text = self.fonts["small"].render(status_data["description"], True, settings.WHITE)
        desc_rect = desc_text.get_rect(centerx=rect.centerx, y=name_rect.bottom + 10)
        screen.blit(desc_text, desc_rect)

    def _draw_status_effects(self, screen: pygame.Surface, character: Character, x: int, y: int, is_player: bool):
        icon_size = 30
        icon_font = self.fonts["medium"]
        turn_font = self.fonts["small"]

        for i, (status_id, turns) in enumerate(character.status_effects.items()):
            status_data = STATUS_EFFECTS[status_id]
            icon_x = x + i * (icon_size + 5)
            icon_y = y if is_player else y - 60 # 敵キャラはSAN/MANAがない分上に表示
            
            # アイコン背景
            icon_bg_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(screen, settings.DARK_GRAY, icon_bg_rect, border_radius=5)
            pygame.draw.rect(screen, settings.WHITE, icon_bg_rect, 1, border_radius=5)

            # アイコン文字
            icon_surface = icon_font.render(status_data['icon'], True, status_data['color'])
            icon_rect = icon_surface.get_rect(center=icon_bg_rect.center)
            screen.blit(icon_surface, icon_rect)

            # ターン数
            turn_surface = turn_font.render(str(turns), True, settings.WHITE)
            turn_rect = turn_surface.get_rect(bottomright=(icon_bg_rect.right + 5, icon_bg_rect.bottom + 5))
            pygame.draw.circle(screen, settings.BLACK, turn_rect.center, 10)
            screen.blit(turn_surface, turn_rect)

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
            # 正気度ダメージがあるかチェック
            if "effects" in action_data:
                for effect in action_data["effects"]:
                    if effect["type"] == "sanity_damage":
                        intent_text = str(effect["value"])
                        icon = "🌀" # 正気度攻撃用のアイコン
                        break

        full_text = f"{icon} {intent_text}"
        text_surface = self.fonts["medium"].render(full_text, True, settings.WHITE)
        text_rect = text_surface.get_rect(centerx=monster.x + 40, bottom=monster.y - 10)
        screen.blit(text_surface, text_rect)