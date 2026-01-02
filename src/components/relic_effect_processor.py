# -*- coding: utf-8 -*-
from ..data.relic_data import RELICS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

class RelicEffectProcessor:
    def __init__(self):
        pass

    @staticmethod
    def apply_relic_effects(character: "Character", enemies: list["Character"]):
        # stat_changeなど、戦闘開始時に一度だけ適用する効果
        for relic_id in character.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    # 戦闘開始時に敵HPを1にする効果（使用回数を持つ）
                    if effect.get("type") == "reduce_enemies_to_one_on_battle_start":
                        # 残り使用回数を確認（未設定ならeffectのusesを参照）
                        remaining = character.relic_uses_remaining.get(relic_id, effect.get("uses", 1))
                        if remaining > 0:
                            for enemy in enemies:
                                if enemy.is_alive and getattr(enemy, 'current_hp', 0) > 1:
                                    enemy.current_hp = 1
                                    # 敵が倒れないようにis_aliveは維持
                                    enemy.is_alive = True if enemy.current_hp > 0 else False
                            # 使用回数をデクリメントして保存
                            character.relic_uses_remaining[relic_id] = remaining - 1
                        # 他の効果と重複しないよう次のeffectへ
                        continue
                    if effect["type"] == "stat_change":
                        stat_to_change = effect["stat"]
                        value = effect["value"]
                        if hasattr(character, stat_to_change):
                            current_value = getattr(character, stat_to_change)
                            setattr(character, stat_to_change, current_value + value)
                            # max_manaが増えた場合、current_manaも増やす
                            if stat_to_change == "max_mana":
                                character.recover_mana(value)
                    elif effect["type"] == "enemy_stat_change":
                        stat_to_change = effect["stat"]
                        value = effect["value"]
                        for enemy in enemies:
                            if hasattr(enemy, stat_to_change):
                                current_value = getattr(enemy, stat_to_change)
                                setattr(enemy, stat_to_change, current_value + value)

    @staticmethod
    def process_turn_start_effects(character: "Character"):
        # ターン開始時に適用する効果
        for relic_id in character.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "take_damage_on_turn_start":
                        character.take_direct_damage(effect["value"])

    @staticmethod
    def process_turn_end_effects(character: "Character", enemies: list["Character"]):
        # ターン終了時に適用する効果
        for relic_id in character.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "gain_defense_on_turn_end":
                        character.defense_buff += effect["value"]
                    elif effect["type"] == "damage_all_enemies_on_turn_end":
                        for enemy in enemies:
                            if enemy.is_alive:
                                enemy.take_direct_damage(effect["value"])
                    elif effect["type"] == "apply_poison_to_all_enemies_on_turn_end":
                        for enemy in enemies:
                            if enemy.is_alive:
                                enemy.apply_status("poison", effect["value"])

    @staticmethod
    def process_timed_effects(character: "Character", turn_count: int):
        # 特定のターンに発動する効果
        for relic_id in character.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect.get("type") == "gain_defense_on_turn" and effect.get("turn") == turn_count:
                        character.defense_buff += effect["value"]