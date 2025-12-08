# -*- coding: utf-8 -*-
import pygame

class EnemySymbol:
    """マップ上の敵シンボルを表すクラス"""
    def __init__(self, grid_x: int, grid_y: int, grid_size: int, enemy_group_id: str):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * grid_size
        self.y = grid_y * grid_size
        self.rect = pygame.Rect(self.x, self.y, grid_size, grid_size)
        self.enemy_group_id = enemy_group_id # 戦闘で出現する敵グループのID