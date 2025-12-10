# -*- coding: utf-8 -*-
import pygame
import math
import random
from typing import TYPE_CHECKING

from .character import Character # 修正: Characterクラスを相対インポート
from .monster import Monster # 既存の行
from ..config import settings # Added import
from .action_handler import ActionHandler
from ..data.monster_data import MONSTERS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.enemy_group_data import ENEMY_GROUPS, ENEMY_POSITIONS

if TYPE_CHECKING:
    from ..scenes.battle_scene import BattleScene

class EnemyManager:
    def __init__(self, player: "Character", battle_scene: "BattleScene"):
        self.player = player
        self.battle_scene = battle_scene
        self.enemies: list[Monster] = []
        self.turn_state: str = "start" # "start", "acting", "finished"
        self.acting_enemy_index: int = 0

    def setup_enemies(self, group_id: str | None = None):
        """敵グループを生成し、初期化する"""
        self.enemies.clear()
        if group_id is None:
            group_id = random.choice(list(ENEMY_GROUPS.keys()))
        
        enemy_group_data = ENEMY_GROUPS[group_id]
        enemy_list = enemy_group_data["enemies"]
        positions = ENEMY_POSITIONS[len(enemy_list)]

        for enemy_info in enemy_list:
            monster_data = MONSTERS[enemy_info["id"]]
            pos = positions[enemy_info["pos_index"]]
            enemy = Monster(name=monster_data["name"], max_hp=monster_data["max_hp"], attack_power=monster_data["attack_power"],
                            actions=monster_data["actions"], x=pos[0], y=pos[1], gold=monster_data.get("gold", 0),
                            image_path=monster_data.get("image"))
            self.enemies.append(enemy)
        
        self.enemies.sort(key=lambda e: e.x)
        for enemy in self.enemies:
            # 敵の行動決定とターゲット設定
            action_id = enemy.decide_next_action()
            action_data = MONSTER_ACTIONS.get(action_id, {})
            first_effect = action_data.get("effects", [{}])[0]
            target_scope = first_effect.get("target_scope")
            if target_scope == "all":
                enemy.targets = [self.player]
            else: # single, self
                enemy.targets = [self.player]

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
                # 行動の決定
                action_id = enemy.next_action or enemy.choose_action()
                action_data = MONSTER_ACTIONS.get(action_id, {})
                effects = action_data.get("effects", [])
                is_conversation = effects and effects[0].get("type") == "conversation_event"

                # アニメーションタイプを決定
                enemy.animation_type = "shake"  # デフォルトはシェイク
                enemy.animation_duration = settings.ANIMATION_SETTINGS["enemy_shake"]["duration"]
                if not is_conversation:
                    intent_type = action_data.get("intent_type", "unknown")
                    if intent_type in ["attack", "attack_debuff"]:
                        enemy.animation_type = "attack"
                        enemy.animation_duration = settings.ANIMATION_SETTINGS["enemy_attack_slide"]["duration"]

                # アニメーション開始
                enemy.is_animating = True
                enemy.animation_start_time = pygame.time.get_ticks()

                if is_conversation:
                    # 会話の場合は、IDを保持して実際のアクションは保留
                    enemy.pending_conversation_id = effects[0]["conversation_id"]
                else:
                    # 通常のアクションは即時実行（DeckManagerを渡す）
                    ActionHandler.execute_monster_action(enemy, enemy.targets, action_id, self.battle_scene.deck_manager)
            else:
                # アニメーション更新
                elapsed_time = pygame.time.get_ticks() - enemy.animation_start_time
                if elapsed_time < enemy.animation_duration * 1000:
                    if enemy.animation_type == "attack":
                        duration_ms = enemy.animation_duration * 1000
                        half_duration_ms = duration_ms / 2
                        progress = elapsed_time / half_duration_ms if elapsed_time < half_duration_ms else (elapsed_time - half_duration_ms) / half_duration_ms
                        
                        slide_distance = settings.ANIMATION_SETTINGS["enemy_attack_slide"]["distance"]
                        if elapsed_time < half_duration_ms:
                            enemy.x = enemy.original_x - slide_distance * progress
                        else:
                            enemy.x = (enemy.original_x - slide_distance) + slide_distance * progress
                    elif enemy.animation_type == "shake":
                        duration_ms = enemy.animation_duration * 1000
                        progress = elapsed_time / duration_ms
                        amplitude = settings.ANIMATION_SETTINGS["enemy_shake"]["amplitude"]
                        frequency_factor = settings.ANIMATION_SETTINGS["enemy_shake"]["frequency_factor"]
                        shake_offset = math.sin(progress * math.pi * frequency_factor) * amplitude
                        enemy.x = enemy.original_x + shake_offset
                else:
                    # アニメーション終了処理
                    enemy.is_animating = False
                    enemy.x = enemy.original_x
                    enemy.animation_type = None

                    if enemy.pending_conversation_id:
                        # 保留されていた会話を開始
                        self.battle_scene.start_conversation(enemy.pending_conversation_id)
                        enemy.pending_conversation_id = None
                        # 次の敵へは進めない（会話から戻ってきたときに進む）
                    else:
                        # 通常のアクションの場合は次の敵へ
                        self.acting_enemy_index += 1
        
        return log_messages

    def advance_to_next_enemy(self):
        """現在行動中の敵のターンを終了し、次の敵に進める"""
        self.acting_enemy_index += 1