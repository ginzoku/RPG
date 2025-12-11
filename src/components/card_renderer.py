# -*- coding: utf-8 -*-
import os
import pygame
from ..data.action_data import ACTIONS


class CardRenderer:
    """Render a card image with overlays: cost (number only), name and description.

    Usage:
        renderer = CardRenderer()
        surf = renderer.render_card('fire_ball', (400,600))
    """

    def __init__(self, base_image_paths=None):
        # Prefer the user's card base image at this exact path first.
        # This ensures we draw text on top of `src/res/cards/card.png` when available.
        preferred_paths = []
        if base_image_paths is None:
            # try absolute path relative to this module first (safe regardless of CWD)
            mod_based = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'res', 'cards', 'card.png'))
            cwd_based = os.path.normpath(os.path.join(os.getcwd(), 'src', 'res', 'cards', 'card.png'))
            preferred_paths = [
                mod_based,
                cwd_based,
                os.path.join('src', 'res', 'cards', 'card.png'),
                os.path.join('res', 'cards', 'card.png'),
            ]
        else:
            preferred_paths = base_image_paths

        # text position overrides: each may be (x, y) in pixels relative to card top-left.
        # If None, renderer uses default computed positions.
        self.text_positions = {
            'cost': None,    # (x, y)
            'name': None,    # (x, y)
            'effect': None,  # (x, y)
        }
        self.base_image = None
        self.base_path = None
        for p in preferred_paths:
            try:
                exists = os.path.exists(p)
            except Exception:
                exists = False
            if exists:
                try:
                    # load image without forcing conversion (convert_alpha may require a display)
                    self.base_image = pygame.image.load(p)
                    self.base_path = p
                    break
                except Exception as e:
                    # if load fails, continue to next candidate
                    continue

    def _load_font(self, preferred_names, size):
        for n in preferred_names:
            path = pygame.font.match_font(n)
            if path:
                try:
                    return pygame.font.Font(path, size)
                except Exception:
                    continue
        return pygame.font.SysFont(None, size)

    def set_text_positions(self, cost: tuple | None = None, name: tuple | None = None, effect: tuple | None = None):
        """Set override positions for cost, name and effect label.

        Each position may be either:
        - absolute pixel tuple: `(x, y)` (int), interpreted as pixels from card top-left; or
        - ratio tuple: `(rx, ry)` where `0.0 <= rx <= 1.0` and `0.0 <= ry <= 1.0`,
          interpreted as fraction of card width/height.

        Pass `None` to leave a position at its automatic default.

        Example:
            # pixels
            renderer.set_text_positions(cost=(8,8), name=(120,540), effect=(120,500))

            # ratios (centered horizontally, name at 90% down)
            renderer.set_text_positions(cost=(0.02, 0.02), name=(0.5, 0.9), effect=(0.5, 0.86))
        """
        def store(key, val):
            if val is None:
                self.text_positions[key] = None
                return
            if not (isinstance(val, (list, tuple)) and len(val) == 2):
                raise ValueError(f'position for {key} must be (x,y) or (rx,ry)')
            x, y = val
            # keep as-is; resolution (ratio -> pixel) happens in render_card
            self.text_positions[key] = (float(x), float(y))

        store('cost', cost)
        store('name', name)
        store('effect', effect)


    def render_card(self, card_id: str, size: tuple[int, int]) -> pygame.Surface:
        """Return a Surface of given size with card art and overlays drawn.

        - card_id: key in ACTIONS
        - size: (width, height)
        """
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # draw base frame (stretched). If we have the base image, blit it.
        # If not found, do NOT draw decorative rectangles or bars — keep background transparent.
        if self.base_image:
            try:
                img = pygame.transform.smoothscale(self.base_image, (w, h))
                surf.blit(img, (0, 0))
            except Exception:
                # If scaling/blit fails, leave surf transparent (no extra views)
                pass
        else:
            # No base image found. We will still render text on a transparent surface,
            # but inform via console so the user is aware the card base was missing.
            print('Warning: base card image not found; rendering text on transparent surface')

        action = ACTIONS.get(card_id, {})
        name = action.get('name', card_id)
        cost = action.get('cost', '')
        desc = action.get('description', '')

        # Fonts scaled to card width, prefer Japanese-capable fonts when available
        preferred = ['Meiryo', 'Meiryo UI', 'Yu Gothic', 'YuGothic', 'MS Gothic', 'MSPGothic', 'NotoSansCJKJP-Regular']
        title_font = self._load_font(preferred, max(20, w // 20))
        body_font = self._load_font(preferred, max(14, w // 40))
        cost_font = self._load_font(preferred, max(18, w // 24))

        # cost: render surface
        cost_surf = cost_font.render(str(cost), True, (0, 0, 0))

        # name: render surface
        name_surf = title_font.render(name, True, (0, 0, 0))

        # effect label (already created as effect_surf)

        # resolve position helper: accepts stored value which may be None, (rx,ry) floats or (x,y) pixels
        def resolve_pos(stored, default_xy, surf_w=None, surf_h=None):
            # default_xy is (x,y) pixel fallback
            if stored is None:
                return default_xy
            x, y = stored
            # treat as ratio if within 0.0-1.0
            try:
                if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                    rx, ry = x, y
                    px = int(rx * w)
                    py = int(ry * h)
                    # if surf_w provided and rx meant to be centered, caller can supply px adjustment
                    return (px, py)
            except Exception:
                pass
            # otherwise interpret as absolute pixels
            return (int(x), int(y))

        # default computed positions
        default_cost_pos = (12, 12)
        default_name_x = (w - name_surf.get_width()) // 2
        default_name_y = h - name_surf.get_height() - 12
        default_name_pos = (default_name_x, default_name_y)

        cost_pos = resolve_pos(self.text_positions.get('cost'), default_cost_pos)
        name_pos = resolve_pos(self.text_positions.get('name'), default_name_pos)
        # blit cost and name using resolved positions
        surf.blit(cost_surf, (cost_pos[0], cost_pos[1]))
        surf.blit(name_surf, (name_pos[0], name_pos[1]))

        # build a short effect summary (first effect) to display above the name
        effect_label = ''
        if isinstance(action.get('effects'), list) and action.get('effects'):
            e = action['effects'][0]
            et = e.get('type', '')
            if et == 'damage':
                effect_label = f"ダメージ {e.get('power', '')}"
            elif et == 'apply_status':
                effect_label = f"付与: {e.get('status_id', '')}"
            elif et == 'draw_card':
                effect_label = f"ドロー {e.get('power', '')}"
            elif et == 'add_card_to_hand':
                effect_label = f"手札追加: {e.get('card_id', '')} x{e.get('amount', 1)}"
            elif et == 'discover_card':
                effect_label = f"探索: {e.get('rarity', '')} x{e.get('count', 1)}"
            else:
                effect_label = et
        effect_surf = body_font.render(effect_label, True, (0, 0, 0)) if effect_label else None

        # description: wrap text into lines above the name area, black text only
        # reserve space for effect label if present
        effect_height = effect_surf.get_height() + 4 if effect_surf else 0
        # use resolved name y (name_pos) to compute available description area
        name_y_resolved = name_pos[1]
        max_desc_bottom = name_y_resolved - 8 - effect_height
        desc_x = 16
        # build wrapped lines
        words = desc.split()
        lines = []
        cur = ''
        for word in words:
            test = (cur + ' ' + word).strip()
            if body_font.size(test)[0] > (w - 32):
                if cur:
                    lines.append(cur)
                cur = word
            else:
                cur = test
        if cur:
            lines.append(cur)
        # limit lines to fit above name area
        line_height = body_font.get_height() + 2
        max_lines = max(0, (max_desc_bottom - 20) // line_height)
        draw_lines = lines[-max_lines:] if max_lines > 0 else []
        start_y = max(12, max_desc_bottom - len(draw_lines) * line_height)
        for i, line in enumerate(draw_lines):
            line_surf = body_font.render(line, True, (0, 0, 0))
            surf.blit(line_surf, (desc_x, start_y + i * line_height))

        # draw effect label just above the name (if exists)
        if effect_surf:
            eff_x = (w - effect_surf.get_width()) // 2
            eff_y = name_y_resolved - effect_surf.get_height() - 6
            surf.blit(effect_surf, (eff_x, eff_y))

        return surf
