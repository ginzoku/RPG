# -*- coding: utf-8 -*-
import math
import random
import pygame # Added pygame import
from .character import Character
from .deck_manager import DeckManager
from ..config import settings # Added settings import
from ..data.action_data import ACTIONS
from ..data.monster_action_data import MONSTER_ACTIONS
from ..data.permanent_effect_data import PERMANENT_EFFECTS
from ..data.status_effect_data import STATUS_EFFECTS
from .status_effect_processor import StatusEffectProcessor

class ActionHandler:
    @staticmethod
    def execute_player_action(player: Character, targets: list[Character], action_id: str, deck_manager: DeckManager) -> list[str]:
        action = ACTIONS[action_id]

        if not player.use_mana(action["cost"]):
            return [] # マナが足りない場合は何もせずに終了

        for effect in action.get("effects", []):
            ActionHandler._process_effect(player, targets, effect, deck_manager)

        return []

    @staticmethod
    def execute_monster_action(monster: Character, targets: list[Character], action_id: str, deck_manager=None) -> list[str]:
        action_data = MONSTER_ACTIONS[action_id]
        for effect in action_data.get("effects", []):
            ActionHandler._process_effect(monster, targets, effect, deck_manager)

        return []

    @staticmethod
    def _process_effect(source: Character, targets: list[Character], effect: dict, deck_manager=None):
        effect_type = effect.get("type")
        if effect_type == "pass": return

        hits = effect.get("hits", 1)

        for _ in range(hits):
            # 毎ヒットごとにターゲットが生きているか確認
            # targets が空の場合でも（例: discover_card, transform_deck 等の非ターゲット効果）
            # 効果を実行するために source をダミーターゲットとして1回処理する
            if not targets:
                ActionHandler._apply_single_effect(source, source, effect, deck_manager)
                continue

            alive_targets = [t for t in targets if t.is_alive]
            if not alive_targets:
                break

            for target_character in alive_targets:
                ActionHandler._apply_single_effect(source, target_character, effect, deck_manager)

    @staticmethod
    def _apply_single_effect(source: Character, target_character: Character, effect: dict, deck_manager=None):
        from ..components.monster import Monster
        effect_type = effect.get("type")

        if effect_type == "damage":
            power = effect.get("power", 0)
            # プレイヤーとモンスターのダメージ計算を統一
            base_damage = power + source.attack_power
            modified_damage = StatusEffectProcessor.modify_outgoing_damage(source, base_damage)
            final_damage = max(1, modified_damage)
            target_character.take_damage(final_damage)

            # ヒットアニメーションをトリガー
            target_character.is_hit_animating = True
            target_character.hit_animation_start_time = pygame.time.get_ticks()
            target_character.hit_animation_duration = settings.ANIMATION_SETTINGS["hit_slide"]["duration"]
            # 攻撃元がターゲットの左にいる場合、ターゲットは右にスライド
            if source.x < target_character.x:
                target_character.hit_animation_direction = 1
            else:
                target_character.hit_animation_direction = -1

        elif effect_type == "heal":
            power = effect.get("power", 0)
            target_character.heal(power)
        
        elif effect_type == "gain_defense":
            gained_defense = effect.get("power", 0) + source.defense_power
            target_character.defense_buff += gained_defense

        elif effect_type == "apply_status":
            status_id = effect["status_id"]
            turns = effect.get("turns", 1)
            target_character.apply_status(status_id, turns)

        elif effect_type == "draw_card" and deck_manager:
            num_to_draw = effect.get("power", 1)
            deck_manager.draw_cards(num_to_draw)
        
        elif effect_type == "add_card_to_hand" and deck_manager:
            card_id = effect["card_id"]
            amount = effect.get("amount", 1)
            is_temporary = effect.get("temporary", False) # temporaryフラグを取得
            for _ in range(amount):
                deck_manager.add_card_to_hand(card_id, temporary=is_temporary)
        
        elif effect_type == "sanity_damage":
            target_character.take_sanity_damage(effect.get("power", 0))

        elif effect_type == "stat_change":
            stat_to_change = effect.get("stat")
            value = effect.get("value", 0)
            if hasattr(target_character, stat_to_change):
                current_value = getattr(target_character, stat_to_change)
                setattr(target_character, stat_to_change, current_value + value)
                # 最大マナが増えた場合、現在マナも増やす
                if stat_to_change == "max_mana":
                    target_character.recover_mana(value)

        elif effect_type == "apply_permanent_effect":
            effect_id = effect.get("effect_id")
            if effect_id and effect_id not in target_character.permanent_effects:
                target_character.permanent_effects.append(effect_id)

        elif effect_type == "discover_card" and deck_manager:
            rarity = effect.get("rarity", "uncommon")
            num_choices = effect.get("count", 3)
            discovered_cards = deck_manager.discover_cards(rarity, num_choices)
            print(f"DEBUG: Discovered cards: {discovered_cards}") # デバッグ用
            if discovered_cards:
                deck_manager.start_discovery(discovered_cards)

        elif effect_type == "transform_deck" and deck_manager:
            # mappings: list of {from: original_id, to: new_id}
            mappings = effect.get("mappings", [])
            deck_manager.apply_deck_transformation_rules(mappings)
        
        elif effect_type == "select_and_dispose" and deck_manager:
            # effect contains 'discard' and 'exhaust' sub-configs
            config = {
                'discard': effect.get('discard', {}),
                'exhaust': effect.get('exhaust', {})
            }
            try:
                deck_manager.start_discard_choice(config)
            except Exception:
                pass


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
                base_power += player.attack_power
                # ステータス効果で修飾された最終的なダメージを計算
                final_power = StatusEffectProcessor.modify_outgoing_damage(player, base_power)
                return final_power

            elif effect_type == "gain_defense":
                return power + player.defense_power
        
        return None