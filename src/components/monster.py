# -*- coding: utf-8 -*-
import random
from .character import Character

class Monster(Character):
    def __init__(self, name: str, max_hp: int, attack_power: int, actions: list[str], x: int, y: int, gold: int):
        # モンスターはMPを使わない想定なので max_mp=0 で初期化
        super().__init__(name, max_hp, 0, attack_power, x, y, character_type='monster')
        self.actions = actions
        self.gold = gold
        self.next_action: str | None = None
        self.targets: list[Character] = []
        
        # アニメーション用属性
        self.is_animating: bool = False
        self.animation_start_time: int = 0
        self.original_x: int = x
        self.animation_type: str | None = None # 'attack' or 'shake'

    def choose_action(self) -> str:
        """行動パターンからランダムに行動を一つ選択する"""
        if not self.actions:
            return "wait" # 行動がなければ何もしない
        return random.choice(self.actions)
    
    def decide_next_action(self) -> str:
        """次の行動を決定し、保持する"""
        self.next_action = self.choose_action()
        return self.next_action