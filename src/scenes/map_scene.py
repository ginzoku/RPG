# -*- coding: utf-8 -*-
import pygame
from ..components.enemy_symbol import EnemySymbol # 修正
from ..data.enemy_group_data import ENEMY_GROUPS
import random
from ..config import settings
from ..components.npc import Npc
from ..config import settings
from ..data.map_data import MAP_DATA
from ..data.map_generator import generate as generate_map

class MapScene:
    """マップの状態を管理するクラス"""
    def __init__(self):
        self.map_data = MAP_DATA
        
        # マップデータからマップの次元を決定
        self.map_height = len(self.map_data)
        self.map_width = len(self.map_data[0]) if self.map_height > 0 else 0

        # マップ全体が画面に収まるようにグリッドサイズを計算
        if self.map_width > 0 and self.map_height > 0:
            grid_size_w = settings.SCREEN_WIDTH // self.map_width
            grid_size_h = settings.SCREEN_HEIGHT // self.map_height
            self.grid_size = min(grid_size_w, grid_size_h)
        else:
            self.grid_size = 0 # マップデータがない場合は0に

        self.player_rect = pygame.Rect(12 * self.grid_size, 7 * self.grid_size, self.grid_size, self.grid_size) # プレイヤーの初期位置
        
        # 敵シンボルをグリッド座標で管理
        enemy_positions = [
            (5, 5, "goblin_duo"),
            (10, 8, "spider_duo"),
            (18, 10, "shadow_eye_solo"),
            (10, 10, "conversation_test_group"),
            (12, 6, "test_choice_group")
        ]
        self.enemies = [
            EnemySymbol(gx, gy, self.grid_size, group_id) for gx, gy, group_id in enemy_positions
        ]
        
        # NPCをリストで管理
        self.npcs = [
            Npc(10 * self.grid_size, 6 * self.grid_size, self.grid_size, "npc_1_intro")
        ]
        
        self.collided_enemy = None # 衝突した敵
        # UI フラグ: 右上アイコンで表示する黒いオーバーレイを制御
        # UI フラグ: 右上アイコンで表示する黒いオーバーレイを制御（初期は非表示）
        self.overlay_active = False
        # フェード用アルファ値（0-255）。View 側で毎フレーム補間して更新する
        self.overlay_alpha = 0
        # オーバーレイ上のコンテンツをスクロールさせるためのオフセット（px）
        # 現在のスクロール値（描画で補間される）
        self.overlay_scroll = 0
        # 目標スクロール値（コントローラが操作する）
        self.overlay_scroll_target = 0
        # generate node-based map according to rules for drawing
        try:
            self.map_graph = generate_map()
        except Exception:
            self.map_graph = None
        # track enabled/completed nodes for sequential unlocking
        self.completed_nodes = set()
        self.enabled_nodes = set()
        try:
            if self.map_graph and len(self.map_graph) > 0 and len(self.map_graph[0]) > 0:
                # start from the entire top row (allow selecting any node on level 0)
                for n in self.map_graph[0]:
                    try:
                        self.enabled_nodes.add(n['id'])
                    except Exception:
                        continue
        except Exception:
            pass

    def mark_node_completed(self, node_id: int):
        """Mark a map node as completed and enable its children."""
        try:
            if node_id in self.completed_nodes:
                return
            self.completed_nodes.add(node_id)
            # disable the completed node
            if hasattr(self, 'enabled_nodes'):
                self.enabled_nodes.discard(node_id)
            # enable all direct children (nodes that list this node as a parent)
            if getattr(self, 'map_graph', None):
                for lvl in self.map_graph:
                    for n in lvl:
                        if node_id in n.get('parents', []):
                            self.enabled_nodes.add(n['id'])
        except Exception:
            pass

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

        # If a pending battle was scheduled by click handling, honor it now
        try:
            if getattr(self, '_pending_battle', None):
                self.collided_enemy = self._pending_battle
                self._pending_battle = None
        except Exception:
            pass
    
    def remove_enemy(self, enemy_to_remove: EnemySymbol):
        # if this synthetic/returned enemy carries a map node id, mark that node completed
        try:
            if hasattr(enemy_to_remove, '_map_node_id'):
                self.mark_node_completed(enemy_to_remove._map_node_id)
        except Exception:
            pass
        # attempt to remove any matching EnemySymbol instance from the active list
        try:
            self.enemies.remove(enemy_to_remove)
        except Exception:
            # ignore if not present
            pass