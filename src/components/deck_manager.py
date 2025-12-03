# -*- coding: utf-8 -*-
import random
from ..data.action_data import ACTIONS

class DeckManager:
    def __init__(self):
        initial_deck = (["slash"] * 2) + (["guard"] * 5) + (["fire_ball"] * 1) + (["expose_weakness"] * 1) + (["healing_light"] * 1) + (["draw_card"] * 1) + ["obliterate"] + ["multi_slash", "sweep"]+["forbidden_pact"]
        self.deck: list[str] = list(initial_deck)
        self.hand: list[str] = []
        self.discard_pile: list[str] = []
        self.exhaust_pile: list[str] = []
        random.shuffle(self.deck)

    def draw_cards(self, num_to_draw: int) -> bool:
        """
        デッキから指定枚数のカードを手札に引く。
        引けた場合はTrue、引けなかった場合はFalseを返す。
        """
        drew_any = False
        for _ in range(num_to_draw):
            if not self.deck:
                if not self.discard_pile:
                    # 引くカードがどこにもない
                    break
                # 捨て札をシャッフルして新しいデッキにする
                self.deck = self.discard_pile
                self.discard_pile = []
                random.shuffle(self.deck)
            
            drawn_card = self.deck.pop()
            if len(self.hand) < 10: # 手札上限チェック
                self.hand.append(drawn_card)
                drew_any = True
            else:
                # 手札が上限に達している場合は捨て札に送る
                self.discard_pile.append(drawn_card)
        return drew_any

    def discard_hand(self):
        """手札の全てのカードを捨て札に送る"""
        self.discard_pile.extend(self.hand)
        self.hand = []

    def move_used_card(self, card_index: int):
        """使用したカードを手札から適切な場所に移動する（捨て札 or 廃棄）"""
        if 0 <= card_index < len(self.hand):
            card_id = self.hand.pop(card_index)
            action_data = ACTIONS.get(card_id)
            if action_data and action_data.get("exhaust", False):
                self.exhaust_pile.append(card_id)
            else:
                self.discard_pile.append(card_id)