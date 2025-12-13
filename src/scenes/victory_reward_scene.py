# -*- coding: utf-8 -*-
import random
import pygame
from ..views.victory_reward_view import VictoryRewardView
from ..data.action_data import ACTIONS
from ..data.monster_action_data import MONSTER_ACTIONS


class VictoryRewardScene:
    def __init__(self, battle_scene):
        self.battle_scene = battle_scene
        # ランダムにユニーク以外のカードを3枚選ぶ
        # exclude uniques, unplayable cards, and any card IDs that are defined as monster actions
        monster_action_ids = set(MONSTER_ACTIONS.keys())
        candidates = [
            cid for cid, data in ACTIONS.items()
            if data.get('rarity') != 'unique'
            and not data.get('unplayable', False)
            and cid not in monster_action_ids
        ]
        # 重複を避けるため sample を使うが、候補が少ない場合は可能な数だけ
        take = min(3, len(candidates))
        self.cards = random.sample(candidates, take) if take > 0 else []
        # VictoryRewardView に battle_scene を渡して描画でプレイヤー情報を参照できるようにする
        self.view = VictoryRewardView(self.cards, battle_scene)
        self.resolved = False

    def process_input(self, event: pygame.event.Event):
        sel = self.view.handle_event(event)
        if sel:
            # 選択またはスキップ
            if sel == 'skip':
                self.finish(None)
            else:
                self.finish(sel)

    def update_state(self):
        pass

    def draw(self, screen: pygame.Surface):
        self.view.draw(screen)

    def finish(self, chosen_card_id: str | None):
        """報酬選択を完了し、カードをデッキに追加してバトルシーンへ戻る"""
        try:
            if chosen_card_id:
                # デッキに追加（捨て札に追加して以後引けるようにする）
                self.battle_scene.deck_manager.add_card_to_deck(chosen_card_id, to_discard=True)
                # Persist to player's master_deck so the reward survives future resets
                try:
                    player = getattr(self.battle_scene, 'player', None)
                    if player is not None:
                        if not hasattr(player, 'master_deck') or player.master_deck is None:
                            player.master_deck = []
                        player.master_deck.append(chosen_card_id)
                except Exception:
                    pass
            # 戻る: マップに戻る要求を GameController に伝えるために
            # Pygame のユーザーイベントを投げる。GameController 側で
            # このイベントを受けて `game_state='map'` に切替えます。
            try:
                import pygame
                ev = pygame.event.Event(pygame.USEREVENT, { 'action': 'RETURN_TO_MAP' })
                pygame.event.post(ev)
            except Exception:
                # イベント送信できない場合は従来の挙動にフォールバック
                self.battle_scene.current_scene = self.battle_scene
            # Also set a flag on the battle_scene as a reliable fallback so the
            # GameController can detect it even if event posting is delayed.
            try:
                setattr(self.battle_scene, 'return_to_map_requested', True)
            except Exception:
                pass
            self.resolved = True
        except Exception as e:
            print(f"ERROR: finishing victory reward: {e}")
            try:
                import pygame
                ev = pygame.event.Event(pygame.USEREVENT, { 'action': 'RETURN_TO_MAP' })
                pygame.event.post(ev)
            except Exception:
                self.battle_scene.current_scene = self.battle_scene
            try:
                setattr(self.battle_scene, 'return_to_map_requested', True)
            except Exception:
                pass
            self.resolved = True
