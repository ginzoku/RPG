# -*- coding: utf-8 -*-
"""
Simple viewer to display generated card assets and overlay name/cost/effect text.
Run: python -m src.tools.card_asset_viewer --mode 1080
Options: --mode {1080,4k,window}
ESC to quit.
"""
import os
import sys
import argparse
import pygame

from ..data.action_data import ACTIONS

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'res', 'cards')
# Display a small selection of real card assets (detail size)
CARD_IDS = ['fire_ball', 'strong_slash', 'research']
FILES = [f'card_{cid}_detail.png' for cid in CARD_IDS]

MODES = {
    '1080': (1920, 1080),
    '4k': (3840, 2160),
    'window': (1280, 720)
}


def load_images():
    imgs = []
    for f in FILES:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            try:
                imgs.append(pygame.image.load(path).convert_alpha())
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                imgs.append(None)
        else:
            print(f"Missing asset: {path}")
            imgs.append(None)
    return imgs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=MODES.keys(), default='1080')
    args = parser.parse_args()

    screen_w, screen_h = MODES[args.mode]
    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption('Card Asset Viewer')

    imgs = load_images()

    fonts = {
        'title': pygame.font.SysFont(None, 36),
        'body': pygame.font.SysFont(None, 22),
        'cost': pygame.font.SysFont(None, 28)
    }

    clock = pygame.time.Clock()
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 30, 40))

        # layout: left/center/right images
        gap = 40
        columns = 3
        col_w = (screen_w - gap * (columns + 1)) // columns
        x = gap
        y = (screen_h - int(col_w * 3/2)) // 2

        for i, surf in enumerate(imgs):
            cid = CARD_IDS[i] if i < len(CARD_IDS) else f"card_{i}"
            action = ACTIONS.get(cid, {})
            name = action.get('name', cid)
            cost = action.get('cost', 0)
            desc = action.get('description', '')

            if surf:
                # scale to column width while preserving aspect ratio
                sw, sh = surf.get_size()
                scale = col_w / sw
                tw = int(sw * scale)
                th = int(sh * scale)
                scaled = pygame.transform.smoothscale(surf, (tw, th))
                screen.blit(scaled, (x, y))

                # overlay name and cost (cost as number only)
                name_s = fonts['title'].render(name, True, (240, 240, 240))
                screen.blit(name_s, (x + 10, y + th - 90))
                cost_s = fonts['cost'].render(str(cost), True, (255, 255, 255))
                # shadow
                screen.blit(fonts['cost'].render(str(cost), True, (0,0,0)), (x + 12 + 1, y + 12 + 1))
                screen.blit(cost_s, (x + 12, y + 12))

                body = desc if desc else "No description"
                body_s = fonts['body'].render(body[:80], True, (220, 220, 220))
                screen.blit(body_s, (x + 10, y + th - 50))

            else:
                placeholder = pygame.Rect(x, y, col_w, int(col_w * 3/2))
                pygame.draw.rect(screen, (60,60,70), placeholder)
                missing = fonts['title'].render('Missing', True, (200,50,50))
                screen.blit(missing, (x + 10, y + 10))

            x += col_w + gap

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
