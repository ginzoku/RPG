# -*- coding: utf-8 -*-
import math
import random
from .character import Character
from .deck_manager import DeckManager
from ..data.action_data import ACTIONS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.status_effect_data import STATUS_EFFECTS
from .status_effect_processor import StatusEffectProcessor

class ActionHandler:
    @staticmethod
    def execute_player_action(player: Character, enemy: Character, action_id: str, deck_manager: DeckManager) -> list[str]:
        action = ACTIONS[action_id]

        if not player.use_mana(action["cost"]):
            return [] # マナが足りない場合は何もせずに終了

        for effect in action.get("effects", []):
            effect_type = effect["type"]
            target_char_name = effect.get("target", "enemy")
            target_character = None
            if target_char_name == "self":
                target_character = player
            elif target_char_name == "enemy":
                if enemy is None: # 敵が指定されていない場合、敵を対象とする効果はスキップ
                    continue
                target_character = enemy
            else: # 未知のターゲットタイプ
                continue

            if effect_type == "damage":
                damage_type = effect.get("damage_type", "physical")
                if damage_type == "physical":
                    base_damage = effect["power"] + player.attack_power
                    modified_damage = StatusEffectProcessor.modify_outgoing_damage(player, base_damage)
                    damage_variance = random.randint(-int(modified_damage * 0.1), int(modified_damage * 0.1))
                    final_damage = max(1, modified_damage + damage_variance)
                    target_character.take_damage(final_damage)
                elif damage_type == "magical":
                    damage = effect["power"]
                    target_character.take_damage(damage)
            
            elif effect_type == "gain_defense":
                gained_defense = effect["power"] + player.defense_power
                target_character.defense_buff += gained_defense

            elif effect_type == "apply_status":
                status_id = effect["status_id"]
                turns = effect.get("turns", 1)
                target_character.apply_status(status_id, turns)

            elif effect_type == "draw_card":
                num_to_draw = effect.get("power", 1)
                deck_manager.draw_cards(num_to_draw)

        return []

    @staticmethod
    def execute_monster_action(monster: Character, player: Character, action_id: str) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]

        for effect in action_data.get("effects", []):
            effect_type = effect["type"]
            target_character = player if effect.get("target") == "player" else monster

            if effect_type == "damage":
                damage_type = effect.get("damage_type", "physical")
                if damage_type == "physical":
                    base_damage = int(monster.attack_power * effect["power"])
                    modified_damage = StatusEffectProcessor.modify_outgoing_damage(monster, base_damage)
                    target_character.take_damage(modified_damage)
                elif damage_type == "magical":
                    target_character.take_damage(effect["power"])
            elif effect_type == "apply_status":
                target_character.apply_status(effect["status_id"], effect.get("turns", 1))
            elif effect_type == "sanity_damage":
                target_character.take_sanity_damage(effect.get("power", 0))

        return []

    @staticmethod
    def get_card_display_power(player: Character, action_id: str) -> int | None:
        """
        カードに表示するための最終的な威力/防御値を計算する。
        表示する値がない場合はNoneを返す。
        """
        action = ACTIONS.get(action_id)
        if not action:
            return None

        # 主な効果（ダメージや防御）の威力を表示する
        for effect in action.get("effects", []):
            effect_type = effect["type"]
            power = effect.get("power")

            if effect_type == "damage":
                base_power = power
                if effect.get("damage_type") == "physical":
                    base_power += player.attack_power
                
                # ステータス効果で修飾された最終的なダメージを計算
                final_power = StatusEffectProcessor.modify_outgoing_damage(player, base_power)
                return final_power

            elif effect_type == "gain_defense":
                return power + player.defense_power
        
        return None