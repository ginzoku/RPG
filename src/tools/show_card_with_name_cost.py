# -*- coding: utf-8 -*-
"""
Show base card with only mana cost and card name overlaid.

Run:
    python -m src.tools.show_card_with_name_cost [card_id]

If card_id is omitted, defaults to 'fire_ball'.
"""
import sys
import os
import pygame
from ..data.action_data import ACTIONS


def main():
    card_id = 'fire_ball'
    if len(sys.argv) > 1:
        card_id = sys.argv[1]

    action = ACTIONS.get(card_id, {})
    name = action.get('name', card_id)
    cost = action.get('cost', '')

    pygame.init()
    screen_w, screen_h = 1200, 800
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption(f'Show {card_id} with name+cost')

    base_paths = [os.path.join('src', 'res', 'cards', 'card.png'), os.path.join('res', 'cards', 'card.png')]
    img = None
    img_path = None
    for p in base_paths:
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                img_path = p
                break
            except Exception as e:
                print(f'Failed to load {p}: {e}')

    if img is None:
        print('Base card image not found.')
        pygame.quit()
        return

    # scale to a comfortable display size (e.g., 800x1200 ratio fit)
    target_h = 600
    iw, ih = img.get_size()
    scale = target_h / ih
    tw = int(iw * scale)
    th = int(ih * scale)
    img = pygame.transform.smoothscale(img, (tw, th))

    # helper: try to find a Japanese-capable font, fallback to default
    def load_font(preferred_names, size):
        for n in preferred_names:
            path = pygame.font.match_font(n)
            if path:
                try:
                    return pygame.font.Font(path, size)
                except Exception:
                    continue
        return pygame.font.SysFont(None, size)

    preferred = ['Meiryo', 'Meiryo UI', 'Yu Gothic', 'YuGothic', 'MS Gothic', 'MSPGothic', 'NotoSansCJKJP-Regular']
    cost_font = load_font(preferred, max(20, tw // 18))
    name_font = load_font(preferred, max(26, tw // 14))

    # create a working surface and blit only the base image
    surf = pygame.Surface((tw, th), pygame.SRCALPHA)
    surf.blit(img, (0, 0))

    # cost: top-left, number only in black (text-only; no shadows or shapes)
    cost_text = str(cost)
    cost_surf = cost_font.render(cost_text, True, (0, 0, 0))
    surf.blit(cost_surf, (8, 8))

    # name: draw text directly on the image (centered near bottom). Black text only.
    name_s = name_font.render(name, True, (0, 0, 0))
    name_x = (tw - name_s.get_width()) // 2
    name_y = th - name_s.get_height() - 12
    surf.blit(name_s, (name_x, name_y))

    # place surf centered on screen
    x = (screen_w - tw) // 2
    y = (screen_h - th) // 2

    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((40, 40, 40))
        screen.blit(surf, (x, y))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
