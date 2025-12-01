# -*- coding: utf-8 -*-
import pygame

class EnemySymbol:
    """マップ上の敵シンボルを表すクラス"""
    def __init__(self, x: int, y: int, enemy_group_id: str):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 40, 40)
        self.enemy_group_id = enemy_group_id # 戦闘で出現する敵グループのID