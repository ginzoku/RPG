# -*- coding: utf-8 -*-
"""
Display a single card in a Pygame window with cost, name and effect description.

Usage:
    python -m src.tools.show_card_full [card_id]

If no card_id is given, defaults to `fire_ball`.
"""
import sys
import os
import pygame

from ..components.card_renderer import CardRenderer
from ..data.action_data import ACTIONS


def main():
    card_id = 'fire_ball'
    if len(sys.argv) > 1:
        card_id = sys.argv[1]

    action = ACTIONS.get(card_id)
    if action is None:
        print('Unknown card id:', card_id)
        return

    pygame.init()
    screen_w, screen_h = 800, 900
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption(f'Card Preview: {card_id}')

    renderer = CardRenderer()
    # Choose a card render size that fits the window
    card_w = int(screen_w * 0.66)
    card_h = int(screen_h * 0.75)
    card_surf = renderer.render_card(card_id, (card_w, card_h))

    x = (screen_w - card_w) // 2
    y = (screen_h - card_h) // 2

    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((60, 60, 60))
        screen.blit(card_surf, (x, y))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
