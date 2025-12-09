# -*- coding: utf-8 -*-
from ..data.relic_data import RELICS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

class RelicEffectProcessor:
    def __init__(self):
        pass

    @staticmethod
    def apply_relic_effects(character: "Character"):
        # stat_changeなど、戦闘開始時に一度だけ適用する効果
        for relic_id in character.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "stat_change" and effect["stat"] == "attack_power":
                        character.attack_power += effect["value"]

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