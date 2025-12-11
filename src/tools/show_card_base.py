# -*- coding: utf-8 -*-
"""
Simple utility: display the base card image `src/res/cards/card.png` unmodified (or scaled to fit window).

Run:
    python -m src.tools.show_card_base

Press ESC or close window to exit.
"""
import os
import pygame


def main():
    pygame.init()
    screen_w, screen_h = 1200, 800
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption('Show Base Card')

    # prefer src/res/cards/card.png
    candidates = [os.path.join('src', 'res', 'cards', 'card.png'), os.path.join('res', 'cards', 'card.png')]
    img = None
    img_path = None
    for p in candidates:
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                img_path = p
                break
            except Exception as e:
                print(f"Failed to load {p}: {e}")

    if img is None:
        print('Base card image not found at expected locations.')
        pygame.quit()
        return

    iw, ih = img.get_size()

    # Determine scale to fit within window while preserving aspect ratio, but don't modify if it already fits
    scale = 1.0
    if iw > screen_w or ih > screen_h:
        scale = min(screen_w / iw, screen_h / ih)

    if scale != 1.0:
        tw = int(iw * scale)
        th = int(ih * scale)
        img = pygame.transform.smoothscale(img, (tw, th))
        iw, ih = img.get_size()

    x = (screen_w - iw) // 2
    y = (screen_h - ih) // 2

    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 30, 30))
        screen.blit(img, (x, y))
        # small caption
        font = pygame.font.SysFont(None, 18)
        caption = font.render(img_path or '', True, (200, 200, 200))
        screen.blit(caption, (8, 8))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
