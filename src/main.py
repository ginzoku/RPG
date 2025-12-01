# -*- coding: utf-8 -*-
import pygame
import sys # sysをインポート
from .config import settings
from .components.character import Character
from .scenes.map_scene import MapScene
from .views.map_view import MapView
from .controllers.map_controller import MapController
from .scenes.battle_scene import BattleScene # 修正
from .views.battle_view import BattleView # 修正

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # ゲーム全体で共有するプレイヤーオブジェクトを生成
        self.player = Character("勇者", max_hp=100, max_mp=3, attack_power=0, x=150, y=settings.SCREEN_HEIGHT // 2 - 100, max_sanity=100)

        self.game_state = "map"  # 初期状態をマップに
        
        # シーンとビューの初期化
        self.map_scene = MapScene()
        self.map_view = MapView(self.screen)
        self.map_controller = MapController()
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
                if self.game_state == "battle":
                    self.battle_scene.process_input(event)

            if self.game_state == "map":
                self.map_controller.handle_input(events, self.map_scene)
                self.map_scene.update()
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