# -*- coding: utf-8 -*-
import pygame
from ..views.bestiary_view import BestiaryView
from ..data.monster_data import MONSTERS

class BestiaryScene:
    def __init__(self):
        self.view = BestiaryView({})
        self.monster_keys = list(MONSTERS.keys())
        self.selected_key = self.monster_keys[0] if self.monster_keys else None
        self.requested_exit = False

    def process_input(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Left panel list area: assume same layout as view
            list_rect = pygame.Rect(30, 80, 300,  pygame.display.get_surface().get_height() - 120)
            if list_rect.collidepoint(pos):
                rel_y = pos[1] - (list_rect.top + 6)
                idx = int((rel_y + self.view.scroll_offset) / self.view.item_height)
                if 0 <= idx < len(self.monster_keys):
                    self.selected_key = self.monster_keys[idx]
        # support mouse wheel (pygame.MOUSEWHEEL) and older button 4/5 events
        elif event.type == pygame.MOUSEWHEEL:
            # event.y: positive when scrolling up
            list_h = pygame.display.get_surface().get_height() - 120
            max_offset = max(0, len(self.monster_keys) * self.view.item_height - list_h)
            # scroll by one item per wheel step
            self.view.scroll_offset = max(0, min(max_offset, self.view.scroll_offset - event.y * self.view.item_height))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            # wheel emulation: 4 = up, 5 = down
            delta = -1 if event.button == 4 else 1
            list_h = pygame.display.get_surface().get_height() - 120
            max_offset = max(0, len(self.monster_keys) * self.view.item_height - list_h)
            self.view.scroll_offset = max(0, min(max_offset, self.view.scroll_offset + delta * self.view.item_height))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.requested_exit = True
            elif event.key == pygame.K_UP:
                try:
                    idx = self.monster_keys.index(self.selected_key)
                    idx = max(0, idx - 1)
                    self.selected_key = self.monster_keys[idx]
                except Exception:
                    pass
            elif event.key == pygame.K_DOWN:
                try:
                    idx = self.monster_keys.index(self.selected_key)
                    idx = min(len(self.monster_keys) - 1, idx + 1)
                    self.selected_key = self.monster_keys[idx]
                except Exception:
                    pass

    def update_state(self):
        # ensure selected item is visible in the left list by adjusting scroll_offset
        if not self.selected_key or not self.monster_keys:
            return
        try:
            idx = self.monster_keys.index(self.selected_key)
        except ValueError:
            return

        list_h = pygame.display.get_surface().get_height() - 120
        visible_count = max(1, list_h // self.view.item_height)

        top_px = idx * self.view.item_height
        bottom_px = top_px + self.view.item_height

        # if selected is above the visible window, scroll up
        if top_px < self.view.scroll_offset:
            # try to center selected item a bit (put at top)
            self.view.scroll_offset = top_px
        # if selected is below the visible window, scroll down
        elif bottom_px > self.view.scroll_offset + list_h:
            self.view.scroll_offset = bottom_px - list_h

        # clamp
        max_offset = max(0, len(self.monster_keys) * self.view.item_height - list_h)
        if self.view.scroll_offset < 0:
            self.view.scroll_offset = 0
        if self.view.scroll_offset > max_offset:
            self.view.scroll_offset = max_offset

    def draw(self, screen: pygame.Surface):
        self.view.draw(screen, self.monster_keys, self.selected_key)
