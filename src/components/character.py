# -*- coding: utf-8 -*-
import math
import pygame

from .relic_effect_processor import RelicEffectProcessor
from ..data.relic_data import RELICS
from .status_effect_processor import StatusEffectProcessor

class Character:
    def __init__(self, name: str, max_hp: int, max_mp: int, attack_power: int, x: int, y: int, character_type: str, max_sanity: int | None = None, image_path: str | None = None):
        self.name: str = name
        self.character_type: str = character_type
        self.max_hp: int = max_hp
        self.current_hp: int = max_hp
        self.max_mana: int = max_mp
        self.current_mana: int = max_mp
        self.base_max_mana: int = max_mp
        self.max_sanity: int | None = max_sanity
        self.current_sanity: int | None = max_sanity
        self.attack_power: int = attack_power
        self.defense_power: int = 0
        self.x: int = x
        self.y: int = y
        self.original_x: int = x # Added this line
        self.base_attack_power: int = attack_power
        self.base_defense_power: int = 0
        self.is_alive: bool = True
        self.defense_buff: int = 0 # 防御によるダメージ減少量
        self.status_effects: dict[str, int] = {} # key: status_id, value: turns
        self.permanent_effects: list[str] = [] # 消去不可の永続効果
        self.relics: list[str] = [] # まず空で初期化
        self.is_targeted: bool = False # ターゲット選択時にハイライトするためのフラグ
        self.gold: int = 0 # 所持ゴールド

        # Hit Animation attributes
        self.is_hit_animating: bool = False
        self.hit_animation_start_time: int = 0
        self.hit_animation_duration: float = 0.0
        self.hit_animation_direction: int = 0 # 1 for right, -1 for left

        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                print(f"Failed to load image: {image_path}. Error: {e}")

        # プレイヤーの場合のみ初期レリックを適用
        if self.character_type == 'player':
            self.relics = ["red_stone", "cursed_armor", "poison_orb", "shield_of_timing", "mana_exchange_amulet"] # 初期レリック
            # レリックの効果はBattleScene.resetで適用されるため、ここでは呼び出さない
            # self._apply_relic_effects()

    def _apply_relic_effects(self, enemies: list["Character"]):
        RelicEffectProcessor.apply_relic_effects(self, enemies)
    
    def take_damage(self, damage: int):
        # ステータス効果による被ダメージ修飾
        modified_damage = StatusEffectProcessor.modify_incoming_damage(self, damage)

        # 防御バフを適用
        absorbed_damage = min(self.defense_buff, modified_damage)
        actual_damage = modified_damage - absorbed_damage
        
        self.defense_buff -= absorbed_damage

        self.current_hp -= actual_damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
        
        # ダメージを受けた後の効果を処理
        StatusEffectProcessor.process_damage_taken(self, actual_damage)

        return actual_damage # 実際に与えたダメージ量を返す
    
    def take_direct_damage(self, damage: int):
        """防御や効果を無視して直接HPにダメージを受ける"""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
        
        # ダメージを受けた後の効果を処理（バリア解除など）
        StatusEffectProcessor.process_damage_taken(self, damage)

    def take_sanity_damage(self, damage: int) -> int:
        """正気度にダメージを受ける。正気度が0になったら死亡する。"""
        if self.current_sanity is None:
            return 0 # 正気度を持たないキャラクター

        self.current_sanity -= damage
        if self.current_sanity <= 0:
            self.current_sanity = 0
            self.is_alive = False # 正気度が0になったら死亡

        return damage # 実際に受けたダメージ量を返す

    def heal(self, amount: int):
        self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def use_mana(self, amount: int) -> bool:
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
    
    def recover_mana(self, amount: int):
        self.current_mana = min(self.current_mana + amount, self.max_mana)

    def fully_recover_mana(self):
        """マナを最大値まで全回復する"""
        self.current_mana = self.max_mana

    def apply_status(self, status_id: str, turns: int):
        """状態異常を付与する（処理はプロセッサに委譲）"""
        StatusEffectProcessor.apply_status(self, status_id, turns)

    def decrement_status_effects(self):
        """ターン終了時の状態異常処理（処理はプロセッサに委譲）"""
        StatusEffectProcessor.process_end_of_turn(self)

    def process_turn_start_relic_effects(self):
        RelicEffectProcessor.process_turn_start_effects(self)

    def process_turn_end_relic_effects(self, enemies: list["Character"]):
        RelicEffectProcessor.process_turn_end_effects(self, enemies)

    def process_timed_relic_effects(self, turn_count: int):
        RelicEffectProcessor.process_timed_effects(self, turn_count)

    def get_hp_percentage(self) -> float:
        return (self.current_hp / self.max_hp) * 100
    
    def get_mp_percentage(self) -> float:
        if self.max_mana == 0: return 0
        return (self.current_mana / self.max_mana) * 100

    def get_sanity_percentage(self) -> float:
        if self.max_sanity is None or self.max_sanity == 0: return 0
        return (self.current_sanity / self.max_sanity) * 100

    def reset_for_battle(self, enemies: list["Character"]):
        """戦闘開始時にプレイヤーの状態をリセットする"""
        self.attack_power = self.base_attack_power
        self.defense_power = self.base_defense_power
        self.max_mana = self.base_max_mana
        self.fully_recover_mana()
        self.defense_buff = 0
        self.status_effects.clear()
        self.permanent_effects.clear()
        self._apply_relic_effects(enemies)