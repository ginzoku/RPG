# -*- coding: utf-8 -*-
import pygame
import math
import os
from ...data.unique_data import DEFAULT_UNIQUE_ID
from ...scenes.battle_scene import BattleScene
from ...config import settings
from ...data.action_data import ACTIONS
from ...data.unique_data import UNIQUE_ABILITIES
from ...components.action_handler import ActionHandler
from ...data.status_effect_data import STATUS_EFFECTS

class PlayerCommandDrawer:
    def __init__(self, fonts: dict):
        self.fonts = fonts

    def draw(self, screen: pygame.Surface, battle_state: BattleScene, command_area_rect: pygame.Rect):
        # --- 新しいレイアウトロジック ---
        cards = battle_state.deck_manager.hand
        num_commands = len(cards)
        if num_commands == 0:
            # Ensure hovered index is cleared when no cards
            battle_state.hovered_card_index = None
            return

        # Validate hovered index to avoid stale/out-of-range values
        if battle_state.hovered_card_index is not None:
            if not (0 <= battle_state.hovered_card_index < num_commands):
                battle_state.hovered_card_index = None

        # --- カードサイズの相対的な定義 ---
        card_height = int(command_area_rect.height * 0.95)
        card_width = int(card_height * 0.7)  # 縦横比を固定
        overlap_x = int(card_width * 0.65)   # カードの重なり具合
        hover_lift = int(card_height * 0.2)  # ホバー時の浮き上がり量

        total_width = (num_commands - 1) * overlap_x + card_width
        start_x = (screen.get_width() - total_width) / 2
        card_y = screen.get_height() - card_height - int(command_area_rect.height * 0.05)

        # 選択モード時のヘッダ表示
        header_text = None
        dm = getattr(battle_state, 'deck_manager', None)
        if dm is not None:
            cfg = getattr(dm, '_discard_config', None)
            if getattr(dm, 'awaiting_discard_choice', False):
                dcfg = (cfg or {}).get('discard', {})
                cnt = int(dcfg.get('count', 1))
                header_text = f"手札から {cnt} 枚を選んで捨ててください"
            elif getattr(dm, 'awaiting_exhaust_choice', False):
                ecfg = (cfg or {}).get('exhaust', {})
                cnt = int(ecfg.get('count', 1))
                header_text = f"手札から {cnt} 枚を選んで廃棄してください"

        if header_text:
            header_surf = self.fonts['medium'].render(header_text, True, (255, 255, 255))
            header_rect = header_surf.get_rect(center=(screen.get_width() // 2, command_area_rect.top - 28))
            # 半透明の背景パネル
            panel_rect = header_rect.inflate(20, 12)
            panel = pygame.Surface(panel_rect.size)
            panel.set_alpha(180)
            panel.fill((20, 20, 30))
            screen.blit(panel, panel_rect.topleft)
            pygame.draw.rect(screen, (200, 200, 200), panel_rect, 1, border_radius=6)
            screen.blit(header_surf, header_rect)

        # ホバーされていないカードを先に描画
        for i, action_id in enumerate(cards):
            if i == battle_state.hovered_card_index:
                continue # ホバーされているカードは後で描画
            
            current_card_x = start_x + i * overlap_x
            card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)
            self._draw_single_card(screen, battle_state, action_id, card_rect, i)
        
        # ホバーされているカードを最後に（一番手前に）描画
        if battle_state.hovered_card_index is not None:
            i = battle_state.hovered_card_index
            action_id = cards[i]
            hover_y = card_y - hover_lift # 少し上に表示
            current_card_x = start_x + i * overlap_x
            card_rect = pygame.Rect(current_card_x, hover_y, card_width, card_height)
            self._draw_single_card(screen, battle_state, action_id, card_rect, i)
        
        # --- 拡大カードの描画 ---
        if battle_state.hovered_card_index is not None:
            action_id = cards[battle_state.hovered_card_index]
            self._draw_enlarged_card(screen, battle_state, action_id)
        
        # --- 山札表示 ---
        self._draw_deck_indicator(screen, battle_state)


    def _draw_single_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str, card_rect: pygame.Rect, card_index: int):
        # 表示は戦闘中の変換ルールを反映した effective_id を使う
        effective_id = action_id
        if hasattr(battle_state.deck_manager, 'get_effective_card_id'):
            effective_id = battle_state.deck_manager.get_effective_card_id(action_id)
        action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))
        # 見た目は常に通常カラーで表示（マナ不足時のグレーアウトを廃止）
        card_bg_color, card_border_color, text_color = ((40, 40, 60), settings.WHITE, settings.LIGHT_BLUE)

        # 廃棄カードの特別な表示（effective_id の属性を参照）
        if action.get("exhaust", False):
            card_border_color = settings.YELLOW # 例えば黄色に

        pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=5)
        pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=5)

        # アクション名（表示は変換後の名前）
        name_text = self.fonts["small"].render(action.get("name", action_id), True, text_color)
        name_rect = name_text.get_rect(center=card_rect.center)
        screen.blit(name_text, name_rect)

        # 左上: 消費MP（unplayable 属性のカードは表示しない）
        if not action.get("unplayable", False):
            cost = action.get("cost", 0)
            if cost >= 0:
                cost_circle_radius = int(card_rect.width * 0.15)
                cost_circle_center = (card_rect.left + cost_circle_radius + 5, card_rect.top + cost_circle_radius + 5)
                pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
                pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 1)
                cost_text = self.fonts["card"].render(str(cost), True, settings.WHITE)
                cost_text_rect = cost_text.get_rect(center=cost_circle_center)
                screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値の表示
        # 表示用の威力は effective_id で計算
        power = ActionHandler.get_card_display_power(battle_state.player, effective_id)
        if power is not None:
            effect_type = action.get("effects", [{}])[0].get("type")
            hits = action.get("effects", [{}])[0].get("hits", 1)
            color = settings.BLUE
            if effect_type == "damage": color = settings.RED
            power_circle_radius = int(card_rect.width * 0.15)
            self._draw_power_circle(screen, power, card_rect, color, power_circle_radius, hits=hits)

    def _draw_power_circle(self, screen: pygame.Surface, power: int, card_rect: pygame.Rect, color: tuple, power_circle_radius: int, hits: int = 1):
        power_circle_center = (card_rect.right - power_circle_radius - 5, card_rect.bottom - power_circle_radius - 5)
        pygame.draw.circle(screen, color, power_circle_center, power_circle_radius)
        pygame.draw.circle(screen, settings.WHITE, power_circle_center, power_circle_radius, 1)
        
        display_text = str(power)
        font = self.fonts["card"]
        if hits > 1:
            display_text = f"{power}x{hits}"
            if len(display_text) > 3:
                font = self.fonts["small"]

        power_text = font.render(display_text, True, settings.WHITE)
        power_text_rect = power_text.get_rect(center=power_circle_center)
        screen.blit(power_text, power_text_rect)

    def _draw_enlarged_card(self, screen: pygame.Surface, battle_state: BattleScene, action_id: str):
        effective_id = action_id
        if hasattr(battle_state.deck_manager, 'get_effective_card_id'):
            effective_id = battle_state.deck_manager.get_effective_card_id(action_id)
        action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))
        
        # --- 拡大カードサイズの相対的な定義 ---
        card_height = int(screen.get_height() * 0.6)
        card_width = int(card_height * 0.7)
        card_x = (screen.get_width() - card_width) / 2
        card_y = (screen.get_height() - card_height) / 2 - int(screen.get_height() * 0.05)
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

        # 背景と枠線
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        card_border_color = settings.WHITE
        if action.get("exhaust", False):
            card_border_color = settings.YELLOW # 例えば黄色に
        pygame.draw.rect(screen, card_border_color, card_rect, 3, border_radius=10)

        # アクション名
        cost_circle_radius = int(card_width * 0.12)
        cost_area_right_edge = card_rect.left + (cost_circle_radius * 2) + 20
        name_area_center_x = cost_area_right_edge + (card_rect.right - cost_area_right_edge) / 2

        name_text = self.fonts["small"].render(action.get("name", action_id), True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=name_area_center_x, y=card_rect.top + 20)
        screen.blit(name_text, name_rect)

        # 説明文
        power_for_desc = ""
        if action.get("effects"): power_for_desc = action["effects"][0].get("power", "")
        description = action.get("description", "").format(power=power_for_desc)
        description_rect = pygame.Rect(card_rect.x + 20, name_rect.bottom + 10, card_rect.width - 40, card_rect.height - name_rect.height - 80)
        self._draw_text_multiline(screen, description, self.fonts["card"], description_rect, settings.WHITE)

        # 左上: 消費MP（unplayable 属性のカードは表示しない）
        if not action.get("unplayable", False):
            cost = action.get("cost", 0)
            if cost >= 0:
                cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
                pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
                pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
                cost_text = self.fonts["small"].render(str(cost), True, settings.WHITE)
                cost_text_rect = cost_text.get_rect(center=cost_circle_center)
                screen.blit(cost_text, cost_text_rect)

        # 右下: 威力または防御値
        power = ActionHandler.get_card_display_power(battle_state.player, effective_id)
        if power is not None:
            effect_type = action.get("effects", [{}])[0].get("type")
            hits = action.get("effects", [{}])[0].get("hits", 1)
            color = settings.BLUE
            if effect_type == "damage": color = settings.RED
            power_circle_radius = int(card_width * 0.12)
            self._draw_power_circle(screen, power, card_rect, color, power_circle_radius, hits=hits)

    def draw_enlarged_into_rect(self, screen: pygame.Surface, battle_state: BattleScene | None, action_id: str, card_rect: pygame.Rect, show_effect_summary: bool = True, show_cost_label: bool = True):
        """Draw the enlarged card UI into the specified rect.

        This reuses the same visual logic as `_draw_enlarged_card` but allows
        drawing into an arbitrary rectangle (useful for reward screens).
        """
        # Determine effective id using battle_state's deck_manager if available
        effective_id = action_id
        if battle_state and hasattr(battle_state, 'deck_manager') and hasattr(battle_state.deck_manager, 'get_effective_card_id'):
            effective_id = battle_state.deck_manager.get_effective_card_id(action_id)
        action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))

        # background and border
        pygame.draw.rect(screen, (60, 60, 80), card_rect, border_radius=10)
        card_border_color = settings.WHITE
        if action.get("exhaust", False):
            card_border_color = settings.YELLOW
        pygame.draw.rect(screen, card_border_color, card_rect, 3, border_radius=10)

        # name area
        name_text = self.fonts["small"].render(action.get("name", action_id), True, settings.WHITE)
        name_rect = name_text.get_rect(centerx=card_rect.left + (card_rect.width * 0.5), y=card_rect.top + 20)
        screen.blit(name_text, name_rect)

        # Show cost as text near top-right for clarity (in addition to cost circle)
        if show_cost_label and not action.get("unplayable", False):
            cost = action.get("cost", 0)
            try:
                cost_label = self.fonts["small"].render(f"消費: {cost}", True, settings.LIGHT_BLUE)
                cost_label_rect = cost_label.get_rect(topright=(card_rect.right - 12, card_rect.top + 12))
                screen.blit(cost_label, cost_label_rect)
            except Exception:
                pass

        # effect summary line (first effect) to make effect explicit on reward cards
        effects = action.get("effects", [])
        effect_summary = None
        if show_effect_summary and effects:
            eff = effects[0]
            etype = eff.get("type")
            if etype == "damage":
                power = eff.get("power", "")
                hits = eff.get("hits", 1)
                effect_summary = f"効果: ダメージ {power} x{hits}"
            elif etype == "draw_card":
                power = eff.get("power", "")
                effect_summary = f"効果: ドロー {power}"
            elif etype == "gain_defense":
                power = eff.get("power", "")
                effect_summary = f"効果: 防御 +{power}"
            elif etype == "apply_status":
                status = eff.get("status_id", "")
                turns = eff.get("turns", "")
                effect_summary = f"効果: {status} {turns}ターン"
            elif etype == "add_card_to_hand":
                cid = eff.get("card_id", "")
                amt = eff.get("amount", 1)
                effect_summary = f"効果: {cid} x{amt} を手札に"
            else:
                effect_summary = f"効果: {etype}"

        if effect_summary:
            try:
                eff_surf = self.fonts["medium"].render(effect_summary, True, settings.LIGHT_BLUE)
                eff_rect = eff_surf.get_rect(centerx=card_rect.left + (card_rect.width * 0.5), y=name_rect.bottom + 6)
                screen.blit(eff_surf, eff_rect)
            except Exception:
                pass

        # description area
        power_for_desc = ""
        if action.get("effects"): power_for_desc = action["effects"][0].get("power", "")
        description = action.get("description", "").format(power=power_for_desc)
        description_rect = pygame.Rect(card_rect.x + 20, name_rect.bottom + 10, card_rect.width - 40, card_rect.height - name_rect.height - 80)
        self._draw_text_multiline(screen, description, self.fonts["card"], description_rect, settings.WHITE)

        # cost circle
        if not action.get("unplayable", False):
            cost = action.get("cost", 0)
            if cost >= 0:
                cost_circle_radius = int(card_rect.width * 0.12)
                cost_circle_center = (card_rect.left + cost_circle_radius + 10, card_rect.top + cost_circle_radius + 10)
                pygame.draw.circle(screen, settings.BLUE, cost_circle_center, cost_circle_radius)
                pygame.draw.circle(screen, settings.WHITE, cost_circle_center, cost_circle_radius, 2)
                cost_text = self.fonts["small"].render(str(cost), True, settings.WHITE)
                cost_text_rect = cost_text.get_rect(center=cost_circle_center)
                screen.blit(cost_text, cost_text_rect)

        # power circle
        power = None
        try:
            player = getattr(battle_state, 'player', None) if battle_state else None
            power = ActionHandler.get_card_display_power(player, effective_id)
        except Exception:
            power = None
        if power is not None:
            effect_type = action.get("effects", [{}])[0].get("type")
            hits = action.get("effects", [{}])[0].get("hits", 1)
            color = settings.BLUE
            if effect_type == "damage": color = settings.RED
            power_circle_radius = int(card_rect.width * 0.12)
            self._draw_power_circle(screen, power, card_rect, color, power_circle_radius, hits=hits)

    def _draw_text_multiline(self, surface, text, font, rect, color):
        """指定された矩形内にテキストを自動で折り返して描画する"""
        lines = text.splitlines()
        space_width = font.size(' ')[0]
        max_width, max_height = rect.size
        pos = list(rect.topleft)
        for line in lines:
            words = line.split(' ')
            for word in line:
                word_surface = font.render(word, True, color)
                word_width, word_height = word_surface.get_size()
                if pos[0] + word_width >= rect.right:
                    pos[0] = rect.left
                    pos[1] += word_height
                surface.blit(word_surface, pos)
                pos[0] += word_width + space_width
            pos[0] = rect.left
            pos[1] += word_height
    
    def _draw_deck_indicator(self, screen: pygame.Surface, battle_state: BattleScene):
        """山札インジケーターを描画"""
        # simple button-like indicator with only the label '山札'
        btn_w, btn_h = 140, 44
        deck_rect = pygame.Rect(10, screen.get_height() - btn_h - 20, btn_w, btn_h)

        # button background and border
        pygame.draw.rect(screen, (50, 50, 70), deck_rect, border_radius=6)
        pygame.draw.rect(screen, settings.WHITE, deck_rect, 2, border_radius=6)

        # show deck count (number) in the button-like area
        deck_count = 0
        try:
            deck_count = len(battle_state.deck_manager.deck) if getattr(battle_state, 'deck_manager', None) else 0
        except Exception:
            deck_count = 0
        label = self.fonts["small"].render(str(deck_count), True, (0, 0, 0))
        label_rect = label.get_rect(center=deck_rect.center)
        screen.blit(label, label_rect)
        # expose the clickable rect to the battle scene so input handling matches visual
        try:
            battle_state.deck_indicator_rect = deck_rect
        except Exception:
            pass
        # --- 山札の上に丸いボタンを描画 ---
        # 中央に画像を置き、丸の下に '1' を描く
        circle_radius = 28
        # 少し上に上げて、下の '1' が山札ボタンに被らないようにする
        extra_raise = 22
        circle_center = (deck_rect.centerx, deck_rect.top - 10 - circle_radius - extra_raise)
        circle_rect = pygame.Rect(circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                                  circle_radius * 2, circle_radius * 2)

        # 背景の円
        pygame.draw.circle(screen, (60, 60, 90), circle_center, circle_radius)
        pygame.draw.circle(screen, settings.WHITE, circle_center, circle_radius, 2)

        # 中央に小さな画像を置く（存在すれば読み込む）
        icon_surf = None
        if not hasattr(self, '_cached_deck_top_icon_tried'):
            self._cached_deck_top_icon = None
            self._cached_deck_top_icon_tried = True
            # 試しにプロジェクト内の既知のパスを確認する
            possible_paths = [
                os.path.join('assets', 'icons', 'deck_icon.png'),
                os.path.join('assets', 'icons', 'card.png'),
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    try:
                        img = pygame.image.load(p).convert_alpha()
                        self._cached_deck_top_icon = img
                        break
                    except Exception:
                        self._cached_deck_top_icon = None
        else:
            self._cached_deck_top_icon = getattr(self, '_cached_deck_top_icon', None)

        if getattr(self, '_cached_deck_top_icon', None):
            # アイコンを円に合わせて縮小して描画
            icon = self._cached_deck_top_icon
            # マージンを少し残す
            max_dim = int(circle_radius * 1.4)
            iw, ih = icon.get_size()
            scale = min(max_dim / iw, max_dim / ih, 1.0)
            new_surf = pygame.transform.smoothscale(icon, (int(iw * scale), int(ih * scale)))
            rect = new_surf.get_rect(center=circle_center)
            screen.blit(new_surf, rect)
        else:
            # 代替: 円の中に小さな白丸を描画してアイコンの代替にする
            inner_r = int(circle_radius * 0.5)
            pygame.draw.circle(screen, settings.WHITE, circle_center, inner_r)

        # 円の下にユニークのクールダウンを描画。0なら準備完了（'1' を表示）
        remaining_cd = 0
        unique_state = getattr(battle_state, 'unique_state', None)
        if unique_state and isinstance(unique_state, dict):
            remaining_cd = int(unique_state.get(DEFAULT_UNIQUE_ID, 0))

        # 準備完了時（remaining_cd == 0）はラベルを表示しない
        if remaining_cd > 0:
            label_text = str(remaining_cd)
            try:
                color = settings.DARK_GRAY
                text_surf = self.fonts['small'].render(label_text, True, color)
            except Exception:
                text_surf = pygame.font.Font(None, 20).render(label_text, True, settings.WHITE)
            text_rect = text_surf.get_rect(center=(circle_center[0], circle_center[1] + circle_radius + 12))
            # 被りチェック: テキストの下端が deck_rect.top - 6 を超えるならテキストを上に移動
            if text_rect.bottom >= deck_rect.top - 6:
                text_rect.top = deck_rect.top - 6 - text_rect.height
                # さらに余裕を持たせて円も少し上げる
                if circle_center[1] + circle_radius + 6 >= text_rect.bottom:
                    circle_center = (circle_center[0], text_rect.top - circle_radius - 8)
            screen.blit(text_surf, text_rect)

        # クリック領域としても保存
        try:
            battle_state.deck_top_button_rect = circle_rect
        except Exception:
            pass

        # ホバー時にユニークのカード詳細を表示
        if getattr(battle_state, 'hovered_unique', False):
            try:
                cfg = UNIQUE_ABILITIES.get(DEFAULT_UNIQUE_ID, {})
                action_id = cfg.get('action_id')
                effective_id = action_id
                if hasattr(battle_state, 'deck_manager') and hasattr(battle_state.deck_manager, 'get_effective_card_id'):
                    effective_id = battle_state.deck_manager.get_effective_card_id(action_id)
                action = ACTIONS.get(effective_id, ACTIONS.get(action_id, {}))

                title = action.get('name', action_id)
                cost = action.get('cost', 0)
                description = action.get('description', '')
                power = ActionHandler.get_card_display_power(battle_state.player, effective_id)

                lines = []
                lines.append(f"{title}  (消費: {cost})")
                if power is not None:
                    lines.append(f"威力: {power}")
                if description:
                    # 短い説明を一行に切り出す
                    lines.append(description.splitlines()[0])

                # パネルサイズ計算
                padding = 8
                max_w = 0
                rendered = []
                for i, ln in enumerate(lines):
                    f = self.fonts['small'] if i > 0 else self.fonts['medium']
                    surf = f.render(ln, True, settings.WHITE)
                    rendered.append((surf, f))
                    if surf.get_width() > max_w: max_w = surf.get_width()

                panel_w = max_w + padding * 2
                panel_h = sum(surf.get_height() for surf, _ in rendered) + padding * 2

                # 表示位置: ボタンの右上に表示（画面外なら左に回避）
                px = circle_center[0] + circle_radius + 12
                py = circle_center[1] - panel_h // 2
                if px + panel_w > screen.get_width():
                    px = circle_center[0] - circle_radius - 12 - panel_w
                if py < 8:
                    py = 8

                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                panel.fill((30, 30, 40, 220))
                # 枠線
                pygame.draw.rect(panel, settings.WHITE, panel.get_rect(), 1, border_radius=6)

                # テキスト描画
                y = padding
                for surf, f in rendered:
                    panel.blit(surf, (padding, y))
                    y += surf.get_height()

                screen.blit(panel, (px, py))
            except Exception:
                pass
