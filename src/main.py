# -*- coding: utf-8 -*-
import pygame
import sys # sysをインポート
from .config import settings
from .components.character import Character
from .scenes.map_scene import MapScene
from .views.map_view import MapView
from .controllers.map_controller import MapController
from .scenes.battle_scene import BattleScene # 修正
from .views.battle_view import BattleView
from .scenes.title_scene import TitleScene

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # ゲーム全体で共有するプレイヤーオブジェクトを生成
        self.player = Character("勇者", max_hp=100, max_mp=3, attack_power=0, x=150, y=settings.SCREEN_HEIGHT // 2 - 100, character_type='player', max_sanity=100, image_path="src/res/player/player.png")

        self.game_state = "title"  # 初期状態をタイトルに

        # シーンとビューの初期化
        self.map_scene = MapScene()
        self.map_view = MapView(self.screen)
        self.map_controller = MapController()
        self.title_scene = TitleScene()
        self.battle_scene = BattleScene(self.player) # プレイヤーオブジェクトを渡す
        self.battle_view = BattleView() # 修正: 重複していた行を削除
        self.running = True

    def run(self):
        while self.running: # 修正: ゲームループを追加
            self.clock.tick(settings.FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    # Custom event: return to map after reward selection
                    if event.type == pygame.USEREVENT and getattr(event, 'action', None) == 'RETURN_TO_MAP':
                        try:
                            # remove the collided enemy from the map so it doesn't respawn
                            if getattr(self.map_scene, 'collided_enemy', None):
                                self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                        except Exception:
                            pass
                        # switch to map state and reset battle flags
                        self.game_state = 'map'
                        try:
                            self.battle_scene.game_over = False
                            self.battle_scene.winner = None
                            self.battle_scene.current_scene = self.battle_scene
                        except Exception:
                            pass
                # Also handle explicit flag set by VictoryRewardScene.finish as a
                # fallback for platforms/timings where posted events might not
                # be processed immediately.
                try:
                    if self.game_state == 'battle' and getattr(self.battle_scene, 'return_to_map_requested', False):
                        # remove collided enemy on the map
                        try:
                            if getattr(self.map_scene, 'collided_enemy', None):
                                self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                        except Exception:
                            pass
                        self.game_state = 'map'
                        # clear the flag and reset battle scene state
                        try:
                            setattr(self.battle_scene, 'return_to_map_requested', False)
                            self.battle_scene.game_over = False
                            self.battle_scene.winner = None
                            self.battle_scene.current_scene = self.battle_scene
                        except Exception:
                            pass
                except Exception:
                    pass
                if self.game_state == "battle":
                    self.battle_scene.process_input(event)
                elif self.game_state == "title":
                    # タイトル画面の入力処理
                    self.title_scene.process_input(event)

            if self.game_state == "map":
                interaction_target = self.map_controller.handle_input(events, self.map_scene)
                self.map_scene.update()

                # interaction_target は現時点ではNPCの会話を想定しているが、
                # 今回はバトル中の会話に焦点を当てているため、この部分はコメントアウトまたは削除
                # if interaction_target:
                #     self.game_state = "conversation"
                #     self.conversation_scene.start_conversation(interaction_target.conversation_id)
                #     continue

                self.map_view.draw(self.map_scene)

                # 敵との衝突判定
                if self.map_scene.collided_enemy:
                    # 戦闘開始
                    self.game_state = "battle"
                    # どの敵グループと戦うか設定してバトルシーンをリセット
                    self.battle_scene.reset(self.map_scene.collided_enemy.enemy_group_id)

            elif self.game_state == "battle":
                self.battle_scene.update_state()
                self.battle_view.draw(self.battle_scene)

            elif self.game_state == "title":
                # タイトル描画
                self.title_scene.draw(self.screen)
                # タイトルで選択されたオプションに応じて遷移
                if getattr(self.title_scene, 'selected_option', None) == 'start':
                    # ゲーム開始 -> マップへ
                    self.game_state = 'map'
                    # 必要ならマップシーンを初期化する
                    self.map_scene = MapScene()
                    # クリア選択をリセット
                    self.title_scene.selected_option = None
                elif getattr(self.title_scene, 'selected_option', None) == 'quit':
                    self.running = False
                    break

                # 戦闘終了判定
                if self.battle_scene.game_over:
                    # Rキーでリスタートする代わりにマップに戻る
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        if self.battle_scene.winner == "player":
                            # 勝利した場合、マップから敵を削除
                            self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                        
                        self.game_state = "map" # マップに戻る
                        self.battle_scene.game_over = False # ゲームオーバー状態をリセット

        
        pygame.quit()
        sys.exit() # 修正: ループの外に移動

if __name__ == "__main__":
    # 修正: 実行ブロックを追加
    game_controller = GameController()
    game_controller.run()