# -*- coding: utf-8 -*-
import random
from ..data.action_data import ACTIONS

class DeckManager:
    def __init__(self):
        initial_deck = \
            (["slash"] * 2) + \
            (["guard"] * 4) + \
            ["fire_ball"] + \
            ["expose_weakness"] + \
            ["healing_light"] + \
            ["draw_card"] + \
            ["obliterate"] + \
            ["multi_slash", "sweep"] + \
            ["rain_of_knives"] + \
            ["forbidden_pact"] + \
            ["research"]
        self.deck: list[str] = list(initial_deck)
        self.hand: list[str] = []
        self.discard_pile: list[str] = []
        self.exhaust_pile: list[str] = []
        self.temporary_cards = set() # 一時的なカードを記録
        random.shuffle(self.deck)

        # 発見メカニズム用の状態
        self.is_discovering = False
        self.discovered_cards: list[dict] = []

    def start_discovery(self, cards: list[dict]):
        """発見プロセスを開始する"""
        self.is_discovering = True
        self.discovered_cards = cards

    def end_discovery(self):
        """発見プロセスを終了する"""
        self.is_discovering = False
        self.discovered_cards = []

    def add_discovered_card_to_hand(self, card_id: str):
        """発見されたカードを手札に加え、一時的なカードとして記録する"""
        self.add_card_to_hand(card_id, temporary=True)
        self.end_discovery()


    def discover_cards(self, rarity: str = "uncommon", count: int = 3) -> list[dict]:
        """
        指定されたレアリティのカードをデッキ外から発見し、指定された枚数だけランダムに返す。
        """
        # 指定されたレアリティのカードをすべて集める
        cards_of_rarity = []
        for card_id, card_data in ACTIONS.items():
            if card_data.get("rarity") == rarity:
                # 'id'フィールドを辞書に追加
                card_info = card_data.copy()
                card_info['id'] = card_id
                cards_of_rarity.append(card_info)

        # 見つかったカードが要求数より少ない場合は、見つかった分だけ返す
        num_to_discover = min(count, len(cards_of_rarity))

        # ランダムにカードを選んで返す
        if num_to_discover > 0:
            return random.sample(cards_of_rarity, num_to_discover)
        return []

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

    def add_card_to_hand(self, card_id: str, temporary: bool = False):
        """指定されたカードを手札に加える"""
        if len(self.hand) < 10: # 手札上限チェック
            self.hand.append(card_id)
        else:
            # 手札が上限に達している場合は捨て札に送る
            self.discard_pile.append(card_id)

        if temporary:
            self.temporary_cards.add(card_id)

    def remove_temporary_cards(self):
        """戦闘終了時に一時的なカードを全てのデッキエリアから削除する"""
        self.deck = [card for card in self.deck if card not in self.temporary_cards]
        self.hand = [card for card in self.hand if card not in self.temporary_cards]
        self.discard_pile = [card for card in self.discard_pile if card not in self.temporary_cards]
        self.temporary_cards.clear()
        print("DEBUG: Temporary cards have been removed from all piles.")

    def apply_hand_end_of_turn_effects(self, player):
        """手札にあるカードの 'on_turn_end' 効果を適用する。

        現状は 'damage' タイプをサポートし、
        'target_scope' が 'player' の場合にプレイヤーへダメージを与える。
        他の効果を追加したい場合はここに拡張してください。
        """
        # 手札をコピーして反復（処理中に手札を変更しても安全）
        for card_id in list(self.hand):
            action_data = ACTIONS.get(card_id, {})
            on_end_effects = action_data.get("on_turn_end", [])
            for effect in on_end_effects:
                etype = effect.get("type")
                if etype == "damage":
                    tgt = effect.get("target_scope")
                    power = effect.get("power", 0)
                    if tgt == "player":
                        # 直接ダメージを適用
                        try:
                            player.take_damage(power)
                        except Exception:
                            # 安全のため例外は無視せずログ出力
                            print(f"ERROR: Failed to apply end-of-turn damage from {card_id}")
                elif etype == "heal":
                    tgt = effect.get("target_scope")
                    power = effect.get("power", 0)
                    if tgt == "player":
                        try:
                            player.heal(power)
                        except Exception:
                            print(f"ERROR: Failed to apply end-of-turn heal from {card_id}")
                else:
                    # 未対応のエフェクトは今は無視（将来の拡張ポイント）
                    print(f"DEBUG: Unsupported on_turn_end effect type '{etype}' on card '{card_id}'")