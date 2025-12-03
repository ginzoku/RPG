# -*- coding: utf-8 -*-
import math
from ..data.relic_data import RELICS
from .status_effect_processor import StatusEffectProcessor

class Character:
    def __init__(self, name: str, max_hp: int, max_mp: int, attack_power: int, x: int, y: int, max_sanity: int | None = None):
        self.name: str = name
        self.max_hp: int = max_hp
        self.current_hp: int = max_hp
        self.max_mana: int = max_mp
        self.current_mana: int = max_mp
        self.max_sanity: int | None = max_sanity
        self.current_sanity: int | None = max_sanity
        self.attack_power: int = attack_power
        self.defense_power: int = 0
        self.x: int = x
        self.y: int = y
        self.is_alive: bool = True
        self.defense_buff: int = 0 # 防御によるダメージ減少量
        self.status_effects: dict[str, int] = {} # key: status_id, value: turns
        self.relics: list[str] = ["red_stone"] # 初期レリック
        self.is_targeted: bool = False # ターゲット選択時にハイライトするためのフラグ
        self.gold: int = 0 # 所持ゴールド

        # レリックの効果を初期適用
        self._apply_initial_relic_effects()

    def _apply_initial_relic_effects(self):
        for relic_id in self.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "stat_change" and effect["stat"] == "attack_power":
                        self.attack_power += effect["value"]
    
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

    def get_hp_percentage(self) -> float:
        return (self.current_hp / self.max_hp) * 100
    
    def get_mp_percentage(self) -> float:
        if self.max_mana == 0: return 0
        return (self.current_mana / self.max_mana) * 100

    def get_sanity_percentage(self) -> float:
        if self.max_sanity is None or self.max_sanity == 0: return 0
        return (self.current_sanity / self.max_sanity) * 100

    def reset_for_battle(self):
        """戦闘開始時にプレイヤーの状態をリセットする"""
        self.fully_recover_mana()
        self.defense_buff = 0
        self.status_effects.clear()