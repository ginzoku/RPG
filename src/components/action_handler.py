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
        log = []

        if not player.use_mana(action["cost"]):
            log.append("マナが足りない！")
            return log

        log.append(f"{player.name}は「{action['name']}」を使った！")

        action_type = action["type"]
        if action_type == "attack":
            damage_type = action.get("damage_type", "physical")
            if damage_type == "physical":
                base_damage = action["power"] + player.attack_power
                
                # ステータス効果によるダメージ修飾
                modified_damage = StatusEffectProcessor.modify_outgoing_damage(player, base_damage)
                
                damage_variance = random.randint(-int(modified_damage * 0.1), int(modified_damage * 0.1))
                final_damage = max(1, modified_damage + damage_variance)
                
                actual_damage = enemy.take_damage(final_damage)
                log.append(f"{enemy.name}に{actual_damage}ダメージ！")
            elif damage_type == "magical":
                damage = action["power"]
                actual_damage = enemy.take_damage(damage)
                log.append(f"{enemy.name}に{actual_damage}ダメージ！")
        
        elif action_type == "skill":
            if action_id == "guard":
                gained_defense = action["power"] + player.defense_power
                player.defense_buff += gained_defense
                log.append(f"{player.name}は{gained_defense}防御を得た！")
            elif "effect" in action:
                # スキルの対象を決定 (デフォルトは敵)
                if action.get("target") == "self":
                    target_character = player
                    target_name = player.name
                else:
                    target_character = enemy
                    target_name = enemy.name

                status_id = action["effect"]
                turns = action.get("power", 1)
                target_character.apply_status(status_id, turns)
                status_name = STATUS_EFFECTS[status_id]["name"]
                log.append(f"{target_name}は{status_name}になった！")
            elif action_id == "draw_card":
                num_to_draw = action.get("power", 1)
                deck_manager.draw_cards(num_to_draw)

        return log

    @staticmethod
    def execute_monster_action(monster: Character, player: Character, action_id: str) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]
        log = [action_data["message"].format(monster_name=monster.name, action_name=action_data["name"])]

        action_type = action_data["type"]
        if action_type == "attack" or action_type == "attack_debuff":
            base_damage = int(monster.attack_power * action_data["power"])

            # モンスターの攻撃にも衰弱などの効果を適用
            modified_damage = StatusEffectProcessor.modify_outgoing_damage(monster, base_damage)

            actual_damage = player.take_damage(modified_damage)
            log.append(f"{player.name}に{actual_damage}ダメージ！")

            if "effect" in action_data:
                player.apply_status(action_data["effect"], action_data.get("effect_power", 1))
                log.append(f"{player.name}は{STATUS_EFFECTS[action_data['effect']]['name']}になった！")
        
        elif action_type == "sanity_attack":
            damage = action_data.get("power", 0)
            actual_damage = player.take_sanity_damage(damage)
            log.append(f"{player.name}の正気度が{actual_damage}削られた！")

        return log

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