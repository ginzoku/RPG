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
from ..data.enemy_group_data import ENEMY_GROUPS, ENEMY_POSITIONS
from ..config import settings

class BattleScene:
    def __init__(self):
        self.reset()

    def reset(self):
        # プレイヤーと敵の初期化
        
        self.player = Character("勇者", max_hp=100, max_mp=3, attack_power=0, x=150, y=settings.SCREEN_HEIGHT // 2 - 100)
        self.enemies: list[Monster] = []
        
        # --- 敵グループの生成 ---
        group_id = random.choice(list(ENEMY_GROUPS.keys()))
        enemy_group = ENEMY_GROUPS[group_id]
        positions = ENEMY_POSITIONS[len(enemy_group)]

        for enemy_info in enemy_group:
            monster_data = MONSTERS[enemy_info["id"]]
            pos = positions[enemy_info["pos_index"]]
            enemy = Monster(name=monster_data["name"], max_hp=monster_data["max_hp"], attack_power=monster_data["attack_power"],
                            actions=monster_data["actions"], x=pos[0], y=pos[1])
            self.enemies.append(enemy)
        
        # 敵リストをX座標でソートして、左から右の順にする
        self.enemies.sort(key=lambda e: e.x)

        
        # ゲーム状態
        self.turn: str = "player"
        self.battle_log: list[str] = []
        self.max_log_lines: int = 4
        self.game_over: bool = False
        self.winner = None
        self.used_card_indices: set[int] = set()
        self.hovered_card_index: int | None = None
        self.hovered_relic_index: int | None = None
        self.targeted_enemy_index: int | None = None # 現在選択されている敵のインデックス

        # 敵のターン進行管理用
        self.enemy_turn_state: str = "start" # "start", "acting", "finished"
        self.acting_enemy_index: int = 0
        self.animation_duration: int = 400 # 0.4秒

        initial_deck = (["slash"] * 6) + (["guard"] * 5) + (["fire_ball"] * 1) + (["expose_weakness"] * 2) + (["healing_light"] * 1)
        self.deck_manager = DeckManager(initial_deck)
        self.deck_manager.draw_cards(5)
        
        for enemy in self.enemies:
            enemy.decide_next_action()

        # レリックの初期化と効果の適用
        self.player.relics.append("red_stone")
        for relic_id in self.player.relics:
            relic_data = RELICS.get(relic_id)
            if relic_data and "effects" in relic_data:
                for effect in relic_data["effects"]:
                    if effect["type"] == "stat_change" and effect["stat"] == "attack_power":
                        self.player.attack_power += effect["value"]

        # バトル開始時に一番左の敵をデフォルトターゲットに設定
        first_living_enemy_index = next((i for i, e in enumerate(self.enemies) if e.is_alive), None)
        self.targeted_enemy_index = first_living_enemy_index

        self.add_log("戦闘開始！")

    def add_log(self, message: str):
        self.battle_log.append(message)
        if len(self.battle_log) > self.max_log_lines:
            self.battle_log.pop(0)
    
    def _check_game_over(self):
        if all(not enemy.is_alive for enemy in self.enemies):
            self.add_log("敵を全て倒した！")
            self.game_over = True
            self.winner = "player"
        if not self.player.is_alive:
            self.add_log(f"{self.player.name}は倒れた...")
            self.game_over = True
            self.winner = "enemy"

    def _update_target_after_enemy_death(self):
        """
        ターゲット中の敵が倒された場合に、次のターゲットを自動で選択する。
        右隣の敵、いなければ左端の敵をターゲットにする。
        """
        if self.targeted_enemy_index is None:
            return

        # 現在のターゲットがまだ生きているか、そもそも敵が全滅している場合は何もしない
        if self.enemies[self.targeted_enemy_index].is_alive or all(not e.is_alive for e in self.enemies):
            return

        num_enemies = len(self.enemies)
        # 倒された敵の右隣から探し始める
        for i in range(1, num_enemies):
            next_index = (self.targeted_enemy_index + i) % num_enemies
            if self.enemies[next_index].is_alive:
                self.targeted_enemy_index = next_index
                return
        
        # 生きている敵が見つからなかった場合 (全滅)
        self.targeted_enemy_index = None
    
    def end_player_turn(self):
        self.turn = "enemy"
        self.add_log("プレイヤーのターン終了")
        self.player.decrement_status_effects() # プレイヤーのターン終了処理
        self.deck_manager.discard_hand()
        self.used_card_indices.clear() # ターン終了時にリセット
        self.hovered_card_index = None # ホバー状態をリセット
        self.enemy_turn_state = "start" # 敵のターン状態をリセット

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
                
                # 敵のホバー判定
                for i, enemy in enumerate(self.enemies):
                    if not enemy.is_alive: continue
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, 80, 100)
                    enemy.is_targeted = enemy_rect.collidepoint(event.pos)

                # カードのホバー判定 (ターゲット選択中でない場合)
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

                # 敵をクリックしたか判定
                for i, enemy in enumerate(self.enemies):
                    if not enemy.is_alive: continue
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, 80, 100)
                    if enemy_rect.collidepoint(event.pos):
                        self.targeted_enemy_index = i
                        return # 敵をクリックしたら他の処理はしない

                # カードをクリックしたか判定
                if self.hovered_card_index is not None:
                    card_index = self.hovered_card_index
                    action_id = self.deck_manager.hand[card_index]
                    action = ACTIONS[action_id]

                    target_enemy = None
                    if self.targeted_enemy_index is not None and self.enemies[self.targeted_enemy_index].is_alive:
                        target_enemy = self.enemies[self.targeted_enemy_index]

                    # 攻撃カードの場合、ターゲットが必要
                    if action["type"] == "attack":
                        if target_enemy:
                            log_messages = ActionHandler.execute_player_action(self.player, target_enemy, action_id)
                            for msg in log_messages: self.add_log(msg)
                            self.used_card_indices.add(card_index)
                            self._update_target_after_enemy_death() # ターゲット更新処理を呼び出す
                        else:
                            self.add_log("攻撃対象を選択してください。")
                            return
                    # 攻撃以外（スキルなど）なら即時実行
                    else:
                        # ターゲットが不要なスキルでも、execute_player_actionはターゲット引数を必要とする
                        dummy_target = target_enemy or next((e for e in self.enemies if e.is_alive), None)
                        if dummy_target:
                            log_messages = ActionHandler.execute_player_action(self.player, dummy_target, action_id)
                            for msg in log_messages: self.add_log(msg)
                        self.used_card_indices.add(card_index)
                        self._update_target_after_enemy_death() # ターゲット更新処理を呼び出す

                    self._check_game_over()
                    if self.game_over: self.end_player_turn()
                    return

        if event.type == pygame.KEYDOWN:
            key = event.key

    def update_state(self):
        if self.turn == "enemy" and not self.game_over:
            if self.enemy_turn_state == "start":
                self.acting_enemy_index = 0
                self.enemy_turn_state = "acting"

            elif self.enemy_turn_state == "acting":
                if self.acting_enemy_index >= len(self.enemies):
                    self.enemy_turn_state = "finished"
                    return

                enemy = self.enemies[self.acting_enemy_index]

                if not enemy.is_alive:
                    self.acting_enemy_index += 1 # 次の敵へ
                    return

                if not enemy.is_animating:
                    # アニメーション開始
                    enemy.is_animating = True
                    enemy.animation_start_time = pygame.time.get_ticks()
                else:
                    # アニメーション更新
                    elapsed_time = pygame.time.get_ticks() - enemy.animation_start_time
                    half_duration = self.animation_duration / 2

                    if elapsed_time < half_duration:
                        # 左へスライド
                        progress = elapsed_time / half_duration
                        enemy.x = enemy.original_x - 50 * progress
                    elif elapsed_time < self.animation_duration:
                        # 右へスライド（元の位置へ）
                        progress = (elapsed_time - half_duration) / half_duration
                        enemy.x = (enemy.original_x - 50) + 50 * progress
                    else:
                        # アニメーション終了
                        enemy.is_animating = False
                        enemy.x = enemy.original_x
                        self.acting_enemy_index += 1 # 次の敵へ

                    # アニメーションのピークでダメージ処理
                    if half_duration - 20 < elapsed_time < half_duration + 20:
                         if not hasattr(enemy, 'action_executed_this_turn') or not enemy.action_executed_this_turn:
                            action_id = enemy.next_action or enemy.choose_action()
                            log_messages = ActionHandler.execute_monster_action(enemy, self.player, action_id)
                            for msg in log_messages: self.add_log(msg)
                            self._check_game_over()
                            enemy.action_executed_this_turn = True

            elif self.enemy_turn_state == "finished":
                # 全ての敵の行動が終わったらプレイヤーのターンへ
                for enemy in self.enemies:
                    enemy.decide_next_action()
                    enemy.decrement_status_effects()
                    if hasattr(enemy, 'action_executed_this_turn'): del enemy.action_executed_this_turn
                
                self.turn = "player"
                self.player.decrement_status_effects()
                if not self.deck_manager.draw_cards(5): self.add_log("山札がありません！")
                self.used_card_indices.clear()
                self.player.fully_recover_mana()