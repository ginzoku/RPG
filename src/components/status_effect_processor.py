# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import TYPE_CHECKING
import math

from ..data.status_effect_data import STATUS_EFFECTS
from ..data.permanent_effect_data import PERMANENT_EFFECTS

if TYPE_CHECKING:
    from .character import Character

class StatusEffectProcessor:
    """状態異常の処理を専門に行うクラス"""

    @staticmethod
    def apply_status(character: Character, status_id: str, turns: int):
        """キャラクターに状態異常を適用する"""
        new_status_data = STATUS_EFFECTS.get(status_id, {})
        
        # 新しい効果がデバフの場合、特定のバフを解除する
        if new_status_data.get("is_debuff", False):
            for existing_status_id in list(character.status_effects.keys()):
                existing_status_data = STATUS_EFFECTS.get(existing_status_id, {})
                if existing_status_data.get("removal_condition") == "on_debuff_received":
                    StatusEffectProcessor._remove_status(character, existing_status_id)

        # 状態異常を付与（効果は加算）
        character.status_effects[status_id] = character.status_effects.get(status_id, 0) + turns

        # 防御バフ効果を適用
        if new_status_data.get("type") == "defense_buff":
            character.defense_buff += new_status_data.get("value", 0)

    @staticmethod
    def _remove_status(character: Character, status_id: str):
        """状態異常を解除し、関連する効果も元に戻す"""
        if status_id in character.status_effects:
            status_data = STATUS_EFFECTS.get(status_id, {})
            # 防御バフ効果を解除
            if status_data.get("type") == "defense_buff":
                character.defense_buff = max(0, character.defense_buff - status_data.get("value", 0))
            
            del character.status_effects[status_id]

    @staticmethod
    def process_end_of_turn(character: Character):
        """ターン終了時の効果を処理し、ターン数を減少させる"""
        # 永続効果の処理
        for effect_id in character.permanent_effects:
            effect_data = PERMANENT_EFFECTS.get(effect_id, {})
            if effect_data.get("type") == "end_of_turn_direct_damage":
                damage = effect_data.get("value", 0)
                character.take_direct_damage(damage)

        # 状態異常の処理
        for status_id in list(character.status_effects.keys()):
            status_data = STATUS_EFFECTS.get(status_id, {})
            
            # ターン終了時効果の発動
            if status_data.get("type") == "end_of_turn_heal":
                character.heal(status_data.get("value", 0))
            elif status_data.get("type") == "end_of_turn_damage":
                # 毒のダメージは現在のターン数と同じ
                damage = character.status_effects[status_id]
                character.take_damage(damage)
            
            # ターン数の減少 (永続効果でない場合)
            if character.status_effects.get(status_id, 0) != -1:
                character.status_effects[status_id] -= 1
                if character.status_effects[status_id] <= 0:
                    StatusEffectProcessor._remove_status(character, status_id)
    
    @staticmethod
    def modify_outgoing_damage(character: Character, damage: int) -> int:
        """攻撃ダメージを修飾する（衰弱など）"""
        modified_damage = damage
        if "weak" in character.status_effects:
            modifier = STATUS_EFFECTS["weak"]["value"]
            modified_damage = math.ceil(modified_damage * modifier)
        if "focus" in character.status_effects:
            modifier = STATUS_EFFECTS["focus"]["value"]
            modified_damage = math.ceil(modified_damage * modifier)
            # 「集中」は一度使ったら消える
            StatusEffectProcessor._remove_status(character, "focus")
        return modified_damage

    @staticmethod
    def modify_incoming_damage(character: Character, damage: int) -> int:
        """被ダメージを修飾する（無防備など）"""
        modified_damage = damage
        if "vulnerable" in character.status_effects:
            modifier = STATUS_EFFECTS["vulnerable"]["value"]
            modified_damage = math.ceil(modified_damage * modifier)
        return modified_damage

    @staticmethod
    def process_damage_taken(character: Character, actual_damage: int):
        """実際にダメージを受けた後の処理（バリア解除など）"""
        if actual_damage > 0:
            for status_id in list(character.status_effects.keys()):
                status_data = STATUS_EFFECTS.get(status_id, {})
                if status_data.get("removal_condition") == "on_damage_taken":
                    StatusEffectProcessor._remove_status(character, status_id)
