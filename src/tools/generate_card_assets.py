# -*- coding: utf-8 -*-
"""
Generate placeholder card art images at multiple sizes using pygame.
Creates: src/res/cards/card_sample_base.png, card_sample_detail.png, card_sample_hires.png
Run: python -m src.tools.generate_card_assets
"""
import os
import pygame
from ..data.action_data import ACTIONS

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'res', 'cards')
SIZES = {
    'base': (400, 600),
    'detail': (800, 1200),
    'hires': (1600, 2400),
}


def draw_placeholder(surface: pygame.Surface, name: str, cost: int | str, description: str):
    w, h = surface.get_size()
    # background gradient
    for y in range(h):
        t = y / h
        r = int(50 + 120 * t)
        g = int(80 + 80 * (1 - t))
        b = int(140 + 80 * (0.5 - abs(t - 0.5)))
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

    # draw rounded rect border
    rect = pygame.Rect(8, 8, w - 16, h - 16)
    pygame.draw.rect(surface, (255, 255, 255), rect, 6, border_radius=20)

    # draw placeholder art (circle + triangle)
    art_rect = pygame.Rect(int(w * 0.12), int(h * 0.14), int(w * 0.76), int(h * 0.56))
    pygame.draw.ellipse(surface, (200, 60, 60), art_rect)
    # simple highlight
    highlight = pygame.Rect(art_rect.x + art_rect.w//6, art_rect.y + art_rect.h//6, art_rect.w//3, art_rect.h//3)
    pygame.draw.ellipse(surface, (255, 200, 200), highlight)

    # draw name bar area
    font = pygame.font.SysFont(None, max(18, w // 20))
    name_surf = font.render(name, True, (255, 255, 255))
    name_bg_rect = pygame.Rect(16, h - 140, w - 32, 84)
    pygame.draw.rect(surface, (20, 20, 20), name_bg_rect, border_radius=8)
    surface.blit(name_surf, (name_bg_rect.x + 12, name_bg_rect.y + 12))

    # draw cost number top-left (no circle)
    cost_font = pygame.font.SysFont(None, max(20, w // 30))
    cost_surf = cost_font.render(str(cost), True, (255, 255, 255))
    # small shadow for readability
    surface.blit(cost_font.render(str(cost), True, (0, 0, 0)), (12 + 1, 12 + 1))
    surface.blit(cost_surf, (12, 12))

    # draw description text near bottom of art area
    desc_font = pygame.font.SysFont(None, max(14, w // 40))
    # wrap description into a couple of lines
    words = description.split()
    lines = []
    cur = ''
    for word in words:
        test = (cur + ' ' + word).strip()
        if desc_font.size(test)[0] > (w - 40):
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines[:3]):
        line_s = desc_font.render(line, True, (220, 220, 220))
        surface.blit(line_s, (16, h - 110 + 18 + i * (desc_font.get_height() + 2)))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pygame.init()

    # Select a few sample cards from ACTIONS to generate assets for
    sample_ids = ["fire_ball", "strong_slash", "research", "hand_burning_curse"]
    for card_id in sample_ids:
        action = ACTIONS.get(card_id, {})
        name = action.get('name', card_id)
        cost = action.get('cost', 0)
        desc = action.get('description', '')
        for key, size in SIZES.items():
            surface = pygame.Surface(size, pygame.SRCALPHA)
            draw_placeholder(surface, name, cost, desc)
            out_path = os.path.join(OUT_DIR, f"card_{card_id}_{key}.png")
            try:
                pygame.image.save(surface, out_path)
                print(f"Wrote: {out_path} ({size[0]}x{size[1]})")
            except Exception as e:
                print(f"Failed to save {out_path}: {e}")

    pygame.quit()


if __name__ == '__main__':
    main()
