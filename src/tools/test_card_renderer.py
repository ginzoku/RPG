# -*- coding: utf-8 -*-
"""
Test script to render real card assets using CardRenderer and display them.
Run: python -m src.tools.test_card_renderer
"""
import pygame
from ..components.card_renderer import CardRenderer
from ..data.action_data import ACTIONS


def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption('Test Card Renderer')
    clock = pygame.time.Clock()

    renderer = CardRenderer()

    # choose a few card ids to render
    sample = ['fire_ball', 'strong_slash', 'research', 'hand_burning_curse']
    sizes = [(280, 420), (280, 420), (280, 420), (280, 420)]

    surfaces = [renderer.render_card(cid, sizes[i]) for i, cid in enumerate(sample)]

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 30, 40))

        gap = 40
        x = 60
        y = (800 - sizes[0][1]) // 2
        for s in surfaces:
            screen.blit(s, (x, y))
            x += s.get_width() + gap

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
