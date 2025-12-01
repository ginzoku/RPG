# -*- coding: utf-8 -*-
import pygame
import math
import random
from .monster import Monster
from .action_handler import ActionHandler
from ..data.monster_data import MONSTERS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.enemy_group_data import ENEMY_GROUPS, ENEMY_POSITIONS

class EnemyManager:
    def __init__(self, player: "Character"):
        self.player = player
        self.enemies: list[Monster] = []
        self.turn_state: str = "start" # "start", "acting", "finished"
        self.acting_enemy_index: int = 0
        self.animation_duration: int = 400 # 0.4秒

    def setup_enemies(self, group_id: str | None = None):
        """敵グループを生成し、初期化する"""
        self.enemies.clear()
        if group_id is None:
            group_id = random.choice(list(ENEMY_GROUPS.keys()))
        enemy_group = ENEMY_GROUPS[group_id]
        positions = ENEMY_POSITIONS[len(enemy_group)]

        for enemy_info in enemy_group:
            monster_data = MONSTERS[enemy_info["id"]]
            pos = positions[enemy_info["pos_index"]]
            enemy = Monster(name=monster_data["name"], max_hp=monster_data["max_hp"], attack_power=monster_data["attack_power"],
                            actions=monster_data["actions"], x=pos[0], y=pos[1])
            self.enemies.append(enemy)
        
        self.enemies.sort(key=lambda e: e.x)
        for enemy in self.enemies:
            enemy.decide_next_action()

    def update_turn(self) -> list[str]:
        """敵のターンを更新し、ログメッセージを返す"""
        log_messages = []
        if self.turn_state == "start":
            self.acting_enemy_index = 0
            self.turn_state = "acting"

        elif self.turn_state == "acting":
            if self.acting_enemy_index >= len(self.enemies):
                self.turn_state = "finished"
                return log_messages

            enemy = self.enemies[self.acting_enemy_index]

            if not enemy.is_alive:
                self.acting_enemy_index += 1
                return log_messages

            if not enemy.is_animating:
                # 行動の実行とアニメーション開始
                action_id = enemy.next_action or enemy.choose_action()
                action_data = MONSTER_ACTIONS.get(action_id, {})
                intent_type = action_data.get("intent_type", "unknown")

                log_messages.extend(ActionHandler.execute_monster_action(enemy, self.player, action_id))

                enemy.animation_type = "shake"
                if intent_type in ["attack", "attack_debuff"]:
                    enemy.animation_type = "attack"
                
                enemy.is_animating = True
                enemy.animation_start_time = pygame.time.get_ticks()
            else:
                # アニメーション更新
                elapsed_time = pygame.time.get_ticks() - enemy.animation_start_time
                if elapsed_time < self.animation_duration:
                    if enemy.animation_type == "attack":
                        half_duration = self.animation_duration / 2
                        progress = elapsed_time / half_duration if elapsed_time < half_duration else (elapsed_time - half_duration) / half_duration
                        if elapsed_time < half_duration:
                            enemy.x = enemy.original_x - 50 * progress
                        else:
                            enemy.x = (enemy.original_x - 50) + 50 * progress
                    elif enemy.animation_type == "shake":
                        progress = elapsed_time / self.animation_duration
                        shake_offset = math.sin(progress * math.pi * 4) * 10
                        enemy.x = enemy.original_x + shake_offset
                else:
                    enemy.is_animating = False
                    enemy.x = enemy.original_x
                    enemy.animation_type = None
                    self.acting_enemy_index += 1
        
        return log_messages