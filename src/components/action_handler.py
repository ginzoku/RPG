# -*- coding: utf-8 -*-
import math
import random
from .character import Character
from ..data.action_data import ACTIONS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.status_effect_data import STATUS_EFFECTS

class ActionHandler:
    @staticmethod
    def execute_player_action(player: Character, enemy: Character, action_id: str) -> list[str]:
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
                base_power = action["power"]
                if "weak" in player.status_effects:
                    base_power = math.ceil(base_power * STATUS_EFFECTS["weak"]["value"])
                base_damage = base_power
                damage_variance = random.randint(-int(base_damage * 0.1), int(base_damage * 0.1))
                damage = max(1, base_damage + damage_variance)
                actual_damage = enemy.take_damage(damage)
                log.append(f"{enemy.name}に{actual_damage}ダメージ！")
            elif damage_type == "magical":
                damage = action["power"]
                actual_damage = enemy.take_damage(damage)
                log.append(f"{enemy.name}に{actual_damage}ダメージ！")
        
        elif action_type == "skill":
            if action_id == "guard":
                player.defense_buff = action["power"]
                log.append(f"{player.name}は防御の構えをとった！")
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

        return log

    @staticmethod
    def execute_monster_action(monster: Character, player: Character, action_id: str) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]
        log = [action_data["message"].format(monster_name=monster.name, action_name=action_data["name"])]

        action_type = action_data["type"]
        if action_type == "attack" or action_type == "attack_debuff":
            power = action_data["power"]
            base_damage = int(monster.attack_power * power)
            actual_damage = player.take_damage(base_damage)
            log.append(f"{player.name}に{actual_damage}ダメージ！")
            if "effect" in action_data:
                player.apply_status(action_data["effect"], action_data.get("effect_power", 1))
                log.append(f"{player.name}は{STATUS_EFFECTS[action_data['effect']]['name']}になった！")
        
        return log