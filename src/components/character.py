# -*- coding: utf-8 -*-
import math
from ..data.relic_data import RELICS
from ..data.status_effect_data import STATUS_EFFECTS

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
        # 被ダメージ修飾子を持つ状態異常を適用
        if "vulnerable" in self.status_effects:
            modifier = STATUS_EFFECTS["vulnerable"]["value"]
            damage = math.ceil(damage * modifier)

        # 防御バフを適用
        absorbed_damage = min(self.defense_buff, damage)
        actual_damage = damage - absorbed_damage
        
        self.defense_buff -= absorbed_damage

        self.current_hp -= actual_damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
        
        # ダメージを受けたら解除される効果を処理
        if actual_damage > 0:
            for status_id in list(self.status_effects.keys()):
                status_data = STATUS_EFFECTS.get(status_id, {})
                if status_data.get("removal_condition") == "on_damage_taken":
                    self._remove_status(status_id)

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
        """状態異常を付与する"""
        new_status_data = STATUS_EFFECTS.get(status_id, {})
        
        # 新しい効果がデバフの場合、特定のバフを解除する
        if new_status_data.get("is_debuff", False):
            for existing_status_id in list(self.status_effects.keys()):
                existing_status_data = STATUS_EFFECTS.get(existing_status_id, {})
                if existing_status_data.get("removal_condition") == "on_debuff_received":
                    self._remove_status(existing_status_id)

        # 状態異常を付与（効果は上書きせず、大きい方を採用）
        self.status_effects[status_id] = max(self.status_effects.get(status_id, 0), turns)

        # 防御バフ効果を適用
        if new_status_data.get("type") == "defense_buff":
            self.defense_buff += new_status_data.get("value", 0)

    def _remove_status(self, status_id: str):
        """状態異常を解除し、関連する効果も元に戻す"""
        if status_id in self.status_effects:
            status_data = STATUS_EFFECTS.get(status_id, {})
            # 防御バフ効果を解除
            if status_data.get("type") == "defense_buff":
                self.defense_buff = max(0, self.defense_buff - status_data.get("value", 0))
            
            del self.status_effects[status_id]

    def decrement_status_effects(self):
        """ターン終了時に状態異常の効果を発動し、ターン数を1減らす"""
        for status_id in list(self.status_effects.keys()):
            # ターン終了時効果の発動
            status_data = STATUS_EFFECTS[status_id]
            if status_data["type"] == "end_of_turn_heal":
                self.heal(status_data["value"])
            elif status_data["type"] == "end_of_turn_damage":
                self.current_hp = max(0, self.current_hp - status_data["value"])
                if self.current_hp == 0:
                    self.is_alive = False
            
            # ターン数の減少 (永続効果でない場合)
            if self.status_effects[status_id] != -1:
                self.status_effects[status_id] -= 1
                if self.status_effects[status_id] <= 0:
                    self._remove_status(status_id)

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