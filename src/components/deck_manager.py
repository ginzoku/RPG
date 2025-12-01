# -*- coding: utf-8 -*-
import random

class DeckManager:
    def __init__(self, initial_deck: list[str]):
        self.deck: list[str] = initial_deck[:]
        self.hand: list[str] = []
        self.discard_pile: list[str] = []
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
            
            self.hand.append(self.deck.pop())
            drew_any = True
        return drew_any

    def discard_hand(self):
        """手札の全てのカードを捨て札に送る"""
        self.discard_pile.extend(self.hand)
        self.hand = []

    def move_used_card_to_discard(self, card_index: int):
        """使用したカードを手札から捨て札に移動する"""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            self.discard_pile.append(card)