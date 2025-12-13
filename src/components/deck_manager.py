# -*- coding: utf-8 -*-
import random
from ..data.action_data import ACTIONS

class DeckManager:
    def __init__(self, initial_deck: list[str] | None = None):
        # Allow passing an explicit initial_deck so that caller (e.g. BattleScene)
        # can control the starting collection (for persistence across battles).
        if initial_deck is None:
            initial_deck = (
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
                ["research"] + \
                ["discard_and_random_exhaust"] + \
                ["transmute_deck"]
            )
        self.deck: list[str] = list(initial_deck)
        self.hand: list[str] = []
        self.discard_pile: list[str] = []
        self.exhaust_pile: list[str] = []
        self.temporary_cards = set() # 一時的なカードを記録
        random.shuffle(self.deck)

        # 発見メカニズム用の状態
        self.is_discovering = False
        self.discovered_cards: list[dict] = []
        # デッキ内カードの一時変換ルール: {original_id: new_id}
        self.deck_transform_rules: dict[str, str] = {}
        # 選択系モード: 手札から1枚選んで捨て、その後ランダムで1枚を廃棄する処理用
        # 選択系モードの状態
        self.awaiting_discard_choice: bool = False
        self._discard_config: dict | None = None
        self._discard_selected_indices: list[int] = []
        self.awaiting_exhaust_choice: bool = False
        self._exhaust_selected_indices: list[int] = []
        self._awaiting_exhaust_count: int = 0
        self._choice_callback = None

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
            # 戦闘中の表示は変換後IDを使うが、内部的には常に元のカードIDを保持する
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
            # 変換ルールがある場合、効果は変換先のデータに従うが、保存するIDは元のままにする
            effective_id = self.get_effective_card_id(card_id)
            action_data = ACTIONS.get(effective_id)
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

    def start_discard_choice(self, config: dict, callback=None):
        """Start a select-and-dispose flow.

        config example:
          {"discard": {"mode":"choose"|"random", "count":1},
           "exhaust": {"mode":"choose"|"random", "count":1}}
        """
        # normalize config
        self._discard_config = config or {}
        self._discard_selected_indices = []
        self._exhaust_selected_indices = []
        self._awaiting_exhaust_count = 0
        self._choice_callback = callback

        discard_cfg = self._discard_config.get("discard", {})
        dmode = discard_cfg.get("mode", "choose")
        dcount = int(discard_cfg.get("count", 1))

        # If discard mode is random, immediately perform random discards
        if dmode == "random":
            import random
            for _ in range(min(dcount, len(self.hand))):
                idx = random.randrange(len(self.hand))
                card = self.hand.pop(idx)
                self.discard_pile.append(card)
            # after random discard, proceed to exhaust handling
            self._start_exhaust_phase()
            return

        # Otherwise enter interactive choose mode
        self.awaiting_discard_choice = True

    def resolve_discard_choice(self, hand_index: int):
        """Handle a player's click during discard-choose mode. Accumulate selections until count reached."""
        try:
            if not self.awaiting_discard_choice:
                return False
            if not (0 <= hand_index < len(self.hand)):
                return False

            # prevent duplicate selection of the same current index
            if hand_index in self._discard_selected_indices:
                return False

            self._discard_selected_indices.append(hand_index)

            # if selected enough, perform discard of selected indices
            dcount = int(self._discard_config.get("discard", {}).get("count", 1))
            if len(self._discard_selected_indices) >= dcount:
                # remove selected indices from hand in descending order
                for idx in sorted(self._discard_selected_indices, reverse=True):
                    if 0 <= idx < len(self.hand):
                        card = self.hand.pop(idx)
                        self.discard_pile.append(card)

                # clear discard selection state
                self.awaiting_discard_choice = False
                self._discard_selected_indices = []

                # proceed to exhaust phase
                self._start_exhaust_phase()

            return True
        except Exception:
            self.awaiting_discard_choice = False
            self._discard_selected_indices = []
            return False

    def _start_exhaust_phase(self):
        """Internal: start exhaust phase according to config (random or choose)."""
        exhaust_cfg = self._discard_config.get("exhaust", {})
        emode = exhaust_cfg.get("mode", "random")
        ecount = int(exhaust_cfg.get("count", 0))

        if ecount <= 0:
            # nothing to do, finish
            cb = self._choice_callback
            self._choice_callback = None
            if cb:
                try:
                    cb()
                except Exception:
                    pass
            return

        if emode == "random":
            import random
            for _ in range(min(ecount, len(self.hand))):
                idx = random.randrange(len(self.hand))
                card = self.hand.pop(idx)
                self.exhaust_pile.append(card)
            # finish
            cb = self._choice_callback
            self._choice_callback = None
            if cb:
                try:
                    cb()
                except Exception:
                    pass
            return

        # emode == 'choose'
        self.awaiting_exhaust_choice = True
        self._exhaust_selected_indices = []
        self._awaiting_exhaust_count = ecount

    def resolve_exhaust_choice(self, hand_index: int):
        """Handle player's selection during exhaust-choose phase."""
        try:
            if not self.awaiting_exhaust_choice:
                return False
            if not (0 <= hand_index < len(self.hand)):
                return False
            if hand_index in self._exhaust_selected_indices:
                return False

            self._exhaust_selected_indices.append(hand_index)
            if len(self._exhaust_selected_indices) >= self._awaiting_exhaust_count:
                for idx in sorted(self._exhaust_selected_indices, reverse=True):
                    if 0 <= idx < len(self.hand):
                        card = self.hand.pop(idx)
                        self.exhaust_pile.append(card)
                # finish
                self.awaiting_exhaust_choice = False
                self._exhaust_selected_indices = []
                self._awaiting_exhaust_count = 0
                cb = self._choice_callback
                self._choice_callback = None
                if cb:
                    try:
                        cb()
                    except Exception:
                        pass
            return True
        except Exception:
            self.awaiting_exhaust_choice = False
            self._exhaust_selected_indices = []
            self._awaiting_exhaust_count = 0
            return False

    def remove_temporary_cards(self):
        """戦闘終了時に一時的なカードを全てのデッキエリアから削除する"""
        self.deck = [card for card in self.deck if card not in self.temporary_cards]
        self.hand = [card for card in self.hand if card not in self.temporary_cards]
        self.discard_pile = [card for card in self.discard_pile if card not in self.temporary_cards]
        self.temporary_cards.clear()
        print("DEBUG: Temporary cards have been removed from all piles.")
        # 戦闘終了時にはデッキ変換ルールもクリアして元に戻す
        self.clear_deck_transformations()

    def apply_deck_transformation_rules(self, mappings: list[dict]):
        """Apply transformation rules to the deck for the rest of the battle.

        mappings: list of {"from": original_id, "to": new_id}
        The rule affects current deck content (for display) and future draws.
        """
        for m in mappings:
            frm = m.get("from")
            to = m.get("to")
            if not frm or not to:
                continue
            # 登録
            self.deck_transform_rules[frm] = to

    def get_effective_card_id(self, card_id: str) -> str:
        """Return transformed card id if a rule exists, otherwise original id."""
        return self.deck_transform_rules.get(card_id, card_id)

    def get_effective_deck(self) -> list[str]:
        """Return a view of the deck with transformations applied for display."""
        return [self.get_effective_card_id(c) for c in self.deck]

    def clear_deck_transformations(self):
        """Clear any active deck transformation rules."""
        self.deck_transform_rules.clear()
    def add_card_to_deck(self, card_id: str, to_discard: bool = True):
        """Add a card to the player's collection during reward/shops.

        By default, the card is added to the discard pile so it will be drawn
        in subsequent turns. If `to_discard` is False, it will be added to the
        top of the deck.
        """
        if to_discard:
            self.discard_pile.append(card_id)
        else:
            # add to top of deck
            self.deck.append(card_id)
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