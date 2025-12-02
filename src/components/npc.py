# -*- coding: utf-8 -*-
import pygame

class Npc:
    def __init__(self, x: int, y: int, grid_size: int, conversation_id: str):
        self.rect = pygame.Rect(x, y, grid_size, grid_size)
        self.conversation_id = conversation_id
        self.color = (255, 255, 0) # 黄色