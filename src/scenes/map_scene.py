# -*- coding: utf-8 -*-
import pygame
from ..components.enemy_symbol import EnemySymbol # 修正
from ..components.npc import Npc
from ..config import settings
from ..data.map_data import MAP_DATA

class MapScene:
    """マップの状態を管理するクラス"""
    def __init__(self):
        self.grid_size = 40 # 1マスのサイズ
        self.map_width = settings.SCREEN_WIDTH // self.grid_size
        self.map_height = settings.SCREEN_HEIGHT // self.grid_size

        self.map_data = MAP_DATA
        self.player_rect = pygame.Rect(12 * self.grid_size, 7 * self.grid_size, self.grid_size, self.grid_size) # プレイヤーの初期位置
        # 敵シンボルをリストで管理
        self.enemies = [
            EnemySymbol(200, 200, "goblin_duo"),
            EnemySymbol(720, 400, "shadow_eye_solo"),
        ]
        # NPCをリストで管理
        self.npcs = [
            Npc(10 * self.grid_size, 6 * self.grid_size, self.grid_size, "npc_1_intro")
        ]
        
        self.collided_enemy = None # 衝突した敵

    def move_player(self, dx: int, dy: int):
        """プレイヤーを移動させる"""
        new_x = self.player_rect.x + dx * self.grid_size
        new_y = self.player_rect.y + dy * self.grid_size

        # グリッド座標に変換
        grid_x = new_x // self.grid_size
        grid_y = new_y // self.grid_size

        # 移動先がマップ範囲内で、かつ移動可能なマスかチェック
        is_valid_move = (0 <= grid_x < self.map_width and 
                        0 <= grid_y < self.map_height and 
                        self.map_data[grid_y][grid_x] == 1)

        if is_valid_move:
            # 移動先にNPCがいないかチェック
            new_rect = pygame.Rect(new_x, new_y, self.grid_size, self.grid_size)
            if any(new_rect.colliderect(npc.rect) for npc in self.npcs):
                return # NPCがいる場合は移動しない

            self.player_rect.x = new_x
            self.player_rect.y = new_y

    def update(self):
        """マップシーンの状態を更新する（衝突判定など）"""
        self.collided_enemy = None
        for enemy in self.enemies:
            if self.player_rect.colliderect(enemy.rect):
                self.collided_enemy = enemy
                break # 最初の衝突でループを抜ける
    
    def remove_enemy(self, enemy_to_remove: EnemySymbol):
        self.enemies.remove(enemy_to_remove)