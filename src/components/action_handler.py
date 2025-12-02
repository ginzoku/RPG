# -*- coding: utf-8 -*-
import math
from .character import Character
from .deck_manager import DeckManager
from ..data.action_data import ACTIONS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.status_effect_data import STATUS_EFFECTS

class ActionHandler:
    @staticmethod
    def get_card_display_power(player: Character, action_id: str) -> int:
        """カードに表示する最終的なダメージ量を計算する"""
        action = ACTIONS.get(action_id)
        if not action or action.get("type") != "attack":
            return 0

        damage = player.attack_power + action.get("damage", 0)
        if "weak" in player.status_effects:
            damage = math.ceil(damage * STATUS_EFFECTS["weak"]["value"])
        
        return damage

    @staticmethod
    def execute_player_action(player: Character, target: Character, action_id: str, deck_manager: DeckManager) -> list[str]:
        action = ACTIONS[action_id]
        cost = action.get("cost", 0)
        
        if not player.use_mana(cost):
            return ["マナが足りません！"]

        log_messages = [f"プレイヤーは「{action['name']}」を使った！"]

        if action["type"] == "attack":
            damage = player.attack_power + action.get("damage", 0)
            actual_damage = target.take_damage(ActionHandler.get_card_display_power(player, action_id))
            log_messages.append(f"{target.name}に{actual_damage}のダメージ！")
        
        if action["type"] == "skill":
            if "effects" in action:
                for effect in action["effects"]:
                    if effect["type"] == "draw_card":
                        if not deck_manager.draw_cards(effect["value"]):
                            log_messages.append("しかし山札がなかった！")
                        else:
                            log_messages.append(f"カードを{effect['value']}枚引いた。")
                    elif effect["type"] == "gain_defense":
                        player.defense_buff += effect["value"]
                        log_messages.append(f"防御を{effect['value']}得た。")
                    elif effect["type"] == "apply_status_to_self":
                        player.apply_status(effect["status_id"], effect["turns"])
                        status_name = STATUS_EFFECTS[effect["status_id"]]["name"]
                        log_messages.append(f"プレイヤーは{status_name}状態になった。")
                    elif effect["type"] == "apply_status_to_target":
                        target.apply_status(effect["status_id"], effect["turns"])
                        status_name = STATUS_EFFECTS[effect["status_id"]]["name"]
                        log_messages.append(f"{target.name}は{status_name}状態になった。")

        return log_messages

    @staticmethod
    def execute_monster_action(monster: Character, player: Character, action_id: str) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]
        log = [action_data["message"].format(monster_name=monster.name, action_name=action_data["name"])]

        action_type = action_data.get("type", "attack")

        if action_type in ["attack", "attack_debuff"]:
            power = action_data.get("power", 1.0)
            damage = math.ceil(monster.attack_power * power)
            
            # 衰弱効果の適用
            if "weak" in monster.status_effects:
                damage = math.ceil(damage * STATUS_EFFECTS["weak"]["value"])

            actual_damage = player.take_damage(damage)
            log.append(f"{player.name}に{actual_damage}のダメージ！")

        if "effects" in action_data:
            for effect in action_data["effects"]:
                if effect["type"] == "apply_status":
                    target = player # 今はプレイヤーにしか付与しない
                    status_id = effect["status_id"]
                    turns = effect["turns"]
                    
                    target.apply_status(status_id, turns)
                    
                    status_name = STATUS_EFFECTS[status_id]["name"]
                    log.append(f"{target.name}は{status_name}状態になった！")

        return log