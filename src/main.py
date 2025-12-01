# -*- coding: utf-8 -*-
import pygame
import sys
from .scenes.battle_scene import BattleScene
from .views.battle_view import BattleView
from .config import settings

class BattleGame:
    def __init__(self) -> None:
        pygame.init()
        self.battle_scene = BattleScene()
        self.battle_view = BattleView()
        self.clock: pygame.time.Clock = pygame.time.Clock()

    def run(self) -> None:
        running = True
        while running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # イベント全体をシーンに渡すことで、より柔軟な入力処理が可能になります
                self.battle_scene.process_input(event)
            
            self.battle_scene.update_state()
            self.battle_view.draw(self.battle_scene)

            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_controller = BattleGame()
    game_controller.run()