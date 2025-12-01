# -*- coding: utf-8 -*-
import pygame
import random
from ..components.character import Character
from ..components.monster import Monster
from ..data.action_data import ACTIONS
from ..components.deck_manager import DeckManager
from ..components.action_handler import ActionHandler
from ..data.monster_data import MONSTERS
from ..data.relic_data import RELICS
from ..config import settings

class BattleScene:
    def __init__(self):
        self.reset()

    def reset(self):
        # プレイヤーと敵の初期化
        
        # --- モンスターの生成 ---
        monster_id = random.choice(list(MONSTERS.keys())) # 今回はランダムにモンスターを選ぶ
        monster_data = MONSTERS[monster_id]
        
        self.player = Character("勇者", max_hp=100, max_mp=3, attack_power=0, x=150, y=settings.SCREEN_HEIGHT // 2 - 100)
        self.enemy = Monster(name=monster_data["name"], max_hp=monster_data["max_hp"], attack_power=monster_data["attack_power"],
                             actions=monster_data["actions"], x=settings.SCREEN_WIDTH - 200, y=settings.SCREEN_HEIGHT // 2 - 100)
        
        # ゲーム状態
        self.turn: str = "player"
        self.battle_log: list[str] = []
        self.max_log_lines: int = 4
        self.game_over: bool = False
        self.winner = None
        self.used_card_indices: set[int] = set()
        self.hovered_card_index: int | None = None
        self.hovered_relic_index: int | None = None

        initial_deck = (["slash"] * 6) + (["guard"] * 5) + (["fire_ball"] * 1) + (["expose_weakness"] * 2) + (["healing_light"] * 1)
        self.deck_manager = DeckManager(initial_deck)
        self.deck_manager.draw_cards(5)
        self.enemy.decide_next_action() # 最初のインテントを決定

        # レリックの初期化と効果の適用
        self.player.relics.append("red_stone")
        for relic_id in self.player.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "stat_change" and effect["stat"] == "attack_power":
                        self.player.attack_power += effect["value"]

        self.add_log("戦闘開始！")

    def add_log(self, message: str):
        self.battle_log.append(message)
        if len(self.battle_log) > self.max_log_lines:
            self.battle_log.pop(0)
    
    def _check_game_over(self):
        if not self.enemy.is_alive:
            self.add_log(f"{self.enemy.name}は倒れた！")
            self.game_over = True
            self.winner = "player"
        elif not self.player.is_alive:
            self.add_log(f"{self.player.name}は倒れた...")
            self.game_over = True
            self.winner = "enemy"
    
    def end_player_turn(self):
        self.turn = "enemy"
        self.add_log("プレイヤーのターン終了")
        self.player.decrement_status_effects() # プレイヤーのターン終了処理
        self.deck_manager.discard_hand()
        self.used_card_indices.clear() # ターン終了時にリセット
        self.hovered_card_index = None

    def process_input(self, event: pygame.event.Event):
        # ゲームオーバー時のリスタート処理
        if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
            return

        # プレイヤーのターン中の入力処理
        if self.turn == "player" and not self.game_over:
            # マウスクリック処理
            log_area_height = int(settings.SCREEN_HEIGHT / 4)
            log_area_y = settings.SCREEN_HEIGHT - log_area_height

            # --- MOUSEMOTIONでホバー状態を更新 ---
            if event.type == pygame.MOUSEMOTION:
                self.hovered_card_index = None # いったんリセット
                self.hovered_relic_index = None # レリックもリセット

                # レリックのホバー判定
                from ..views.drawers.relic_drawer import RelicDrawer # 循環インポートを避けるためここでインポート
                relic_drawer = RelicDrawer({}) # フォントは不要なので空辞書
                for i, relic_id in enumerate(self.player.relics):
                    relic_rect = relic_drawer.get_relic_rect(i)
                    if relic_rect.collidepoint(event.pos):
                        self.hovered_relic_index = i
                        break

                
                num_commands = len(self.deck_manager.hand)
                if num_commands > 0:
                    card_width = 120
                    card_height = 170
                    overlap_x = 80
                    total_width = (num_commands - 1) * overlap_x + card_width
                    start_x = (settings.SCREEN_WIDTH - total_width) / 2
                    card_y = settings.SCREEN_HEIGHT - card_height - 10

                    # マウスカーソルがどのカードの上にあるか逆順でチェック（手前のカードを優先）
                    for i in range(num_commands - 1, -1, -1):
                        current_card_x = start_x + i * overlap_x
                        card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)
                        # ホバーされているカードは少し上にずれるので、その分も考慮
                        if self.hovered_card_index == i:
                            card_rect.y -= 30

                        if card_rect.collidepoint(event.pos):
                            action_id = self.deck_manager.hand[i]
                            action = ACTIONS[action_id]
                            can_afford = self.player.current_mana >= action.get("cost", 0)

                            if i not in self.used_card_indices and can_afford:
                                self.hovered_card_index = i
                            break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ターン終了ボタンの判定
                button_width = 120
                button_height = 40
                button_x = settings.SCREEN_WIDTH - button_width - 150 # 捨て札表示と被らないように左にずらす
                button_y = log_area_y - button_height - 10
                end_turn_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                if end_turn_button_rect.collidepoint(event.pos):
                    self.end_player_turn()
                    return # 他のクリック処理は行わない

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ログエリアがコマンド選択エリアになる
                # クリックされたのがコマンドカード上か判定
                # ホバーされているカードがクリックされたか判定
                if self.hovered_card_index is not None:
                    i = self.hovered_card_index
                    num_commands = len(self.deck_manager.hand)
                    card_width = 120
                    card_height = 170
                    overlap_x = 80
                    total_width = (num_commands - 1) * overlap_x + card_width
                    start_x = (settings.SCREEN_WIDTH - total_width) / 2
                    card_y = settings.SCREEN_HEIGHT - card_height - 10 - 30 # ホバー時のY座標
                    
                    current_card_x = start_x + i * overlap_x
                    card_rect = pygame.Rect(current_card_x, card_y, card_width, card_height)

                    if card_rect.collidepoint(event.pos):
                        # ホバーされているカードがクリックされたのでアクション実行
                        action_id = self.deck_manager.hand[i]
                        log_messages = ActionHandler.execute_player_action(self.player, self.enemy, action_id)
                        for msg in log_messages:
                            self.add_log(msg)
                        
                        self.used_card_indices.add(i)
                        self._check_game_over()
                        if self.game_over:
                            self.end_player_turn()
                        return # カードクリック処理はここで終了

        if event.type == pygame.KEYDOWN:
            key = event.key

    def update_state(self):
        if self.turn == "enemy" and not self.game_over:
            if not hasattr(self, 'enemy_action_time'):
                self.enemy_action_time = pygame.time.get_ticks()

            if pygame.time.get_ticks() - self.enemy_action_time > 1000: # 1秒待機
                action_id = self.enemy.next_action or self.enemy.choose_action()
                log_messages = ActionHandler.execute_monster_action(self.enemy, self.player, action_id)
                for msg in log_messages:
                    self.add_log(msg)
                
                self._check_game_over()
                
                self.enemy.decide_next_action() # 次のインテントを決定
                # 敵のターン終了処理
                self.enemy.decrement_status_effects()
                # プレイヤーのターンへ移行準備
                self.turn = "player"
                if not self.deck_manager.draw_cards(5):
                    self.add_log("山札がありません！")
                self.used_card_indices.clear()
                self.player.fully_recover_mana()

                del self.enemy_action_time