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

        action_type = action["type"]
        if action_type == "attack":
            damage_type = action.get("damage_type", "physical")
            if damage_type == "physical":
                base_damage = action["power"] + player.attack_power
                modified_damage = StatusEffectProcessor.modify_outgoing_damage(player, base_damage)
                damage_variance = random.randint(-int(modified_damage * 0.1), int(modified_damage * 0.1))
                final_damage = max(1, modified_damage + damage_variance)
                enemy.take_damage(final_damage)
            elif damage_type == "magical":
                damage = action["power"]
                enemy.take_damage(damage)
        
        elif action_type == "skill":
            if action_id == "guard":
                gained_defense = action["power"] + player.defense_power
                player.defense_buff += gained_defense
            elif "effect" in action:
                target_character = player if action.get("target") == "self" else enemy
                status_id = action["effect"]
                turns = action.get("power", 1)
                target_character.apply_status(status_id, turns)
            elif action_id == "draw_card":
                num_to_draw = action.get("power", 1)
                deck_manager.draw_cards(num_to_draw)

        return []

    @staticmethod
    def execute_monster_action(monster: Character, player: Character, action_id: str) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]
        action_type = action_data["type"]

        if action_type == "attack" or action_type == "attack_debuff":
            base_damage = int(monster.attack_power * action_data["power"])
            modified_damage = StatusEffectProcessor.modify_outgoing_damage(monster, base_damage)
            player.take_damage(modified_damage)
            if "effect" in action_data:
                player.apply_status(action_data["effect"], action_data.get("effect_power", 1))
        
        elif action_type == "sanity_attack":
            damage = action_data.get("power", 0)
            player.take_sanity_damage(damage)

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

        action_type = action.get("type")
        power = action.get("power")

        if action_type == "attack":
            base_power = power
            if action.get("damage_type") == "physical":
                base_power += player.attack_power
            
            # ステータス効果で修飾された最終的なダメージを計算
            final_power = StatusEffectProcessor.modify_outgoing_damage(player, base_power)
            return final_power

        elif action_id == "guard": # "防御"カード
            return power + player.defense_power
        
        return None