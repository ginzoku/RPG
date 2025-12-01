# -*- coding: utf-8 -*-
import pygame
from ..components.enemy_symbol import EnemySymbol

class MapScene:
    """マップの状態を管理するクラス"""
    def __init__(self):
        self.player_rect = pygame.Rect(480, 280, 40, 40) # プレイヤーの位置とサイズ
        self.player_speed = 5

        # 敵シンボルをリストで管理
        self.enemies = [
            EnemySymbol(200, 200, "goblin_duo"),
            EnemySymbol(700, 400, "slime_trio"),
        ]
        
        self.collided_enemy = None # 衝突した敵

    def move_player(self, dx: int, dy: int):
        """プレイヤーを移動させる"""
        self.player_rect.x += dx * self.player_speed
        self.player_rect.y += dy * self.player_speed

    def update(self):
        """マップシーンの状態を更新する（衝突判定など）"""
        self.collided_enemy = None
        for enemy in self.enemies:
            if self.player_rect.colliderect(enemy.rect):
                self.collided_enemy = enemy
                break # 最初の衝突でループを抜ける
    
    def remove_enemy(self, enemy_to_remove: EnemySymbol):
        self.enemies.remove(enemy_to_remove)