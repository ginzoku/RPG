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
from .scenes.bestiary_scene import BestiaryScene

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
        self.bestiary_scene = BestiaryScene()
        self.battle_scene = BattleScene(self.player) # プレイヤーオブジェクトを渡す
        self.battle_view = BattleView() # 修正: 重複していた行を削除
        self.running = True
        # フラグ: 会話終了直後に同じ入力で再度会話が始まらないよう一度だけインタラクションを無視する
        self._skip_next_map_interaction = False

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            events = pygame.event.get()
            for event in events:
                # standard quit
                if event.type == pygame.QUIT:
                    self.running = False

                # custom posted event for return to map
                if event.type == pygame.USEREVENT and getattr(event, 'action', None) == 'RETURN_TO_MAP':
                    try:
                        if getattr(self.map_scene, 'collided_enemy', None):
                            self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                    except Exception:
                        pass
                    self.game_state = 'map'
                    try:
                        self.battle_scene.game_over = False
                        self.battle_scene.winner = None
                        self.battle_scene.current_scene = self.battle_scene
                    except Exception:
                        pass

                # dispatch to current scene input handlers
                if self.game_state == "battle":
                    self.battle_scene.process_input(event)
                elif self.game_state == "title":
                    self.title_scene.process_input(event)
                elif self.game_state == "bestiary":
                    self.bestiary_scene.process_input(event)
                elif self.game_state == "conversation" and getattr(self, 'conversation_scene', None):
                    try:
                        self.conversation_scene.process_input(event)
                    except Exception:
                        pass

            # fallback flag: VictoryRewardScene may set return_to_map_requested on the battle_scene
            try:
                if self.game_state == 'battle' and getattr(self.battle_scene, 'return_to_map_requested', False):
                    try:
                        if getattr(self.map_scene, 'collided_enemy', None):
                            self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                    except Exception:
                        pass
                    self.game_state = 'map'
                    try:
                        setattr(self.battle_scene, 'return_to_map_requested', False)
                        self.battle_scene.game_over = False
                        self.battle_scene.winner = None
                        self.battle_scene.current_scene = self.battle_scene
                    except Exception:
                        pass
            except Exception:
                pass

            # state updates / drawing
            if self.game_state == "map":
                # if we just finished a conversation this frame, skip map interaction once
                if getattr(self, '_skip_next_map_interaction', False):
                    interaction_target = None
                else:
                    interaction_target = self.map_controller.handle_input(events, self.map_scene)
                if interaction_target:
                    # start map conversation
                    def _conv_finished(result=None):
                        try:
                            # mark to skip next map interaction (same-frame Enter press)
                            self._skip_next_map_interaction = True
                        finally:
                            self.game_state = 'map'
                            self.conversation_scene = None

                    try:
                        from .scenes.conversation_scene import ConversationScene
                        from .views.map_conversation_view import MapConversationView
                        print(f"DEBUG: Map interaction -> creating ConversationScene for {interaction_target.conversation_id}", flush=True)
                        self.conversation_scene = ConversationScene(self.player, interaction_target.conversation_id, _conv_finished)
                        # replace view with map-specific view (ensures flip and UI choice)
                        try:
                            bg = self.conversation_scene.conversation_data.get('default_background')
                            self.conversation_scene.view = MapConversationView(bg)
                            # repopulate the new view with the current event's text/choices
                            try:
                                # call internal helper to apply current event to the (new) view
                                self.conversation_scene._show_current_event()
                            except Exception:
                                # fallback: manually set dialogue if available
                                ev = self.conversation_scene.conversation_data['events'][self.conversation_scene.current_event_index]
                                try:
                                    self.conversation_scene.view.set_dialogue(ev.get('speaker'), ev.get('text', ''))
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        self.game_state = 'conversation'
                    except Exception as e:
                        print(f"ERROR: Failed to create map conversation: {e}", flush=True)
                        self.conversation_scene = None
                else:
                    self.map_scene.update()
                    self.map_view.draw(self.map_scene)
                    if self.map_scene.collided_enemy:
                        self.game_state = "battle"
                        self.battle_scene.reset(self.map_scene.collided_enemy.enemy_group_id)

                # reset the skip flag after handling this map frame so next frames allow interactions
                if getattr(self, '_skip_next_map_interaction', False):
                    # we've skipped one map interaction cycle, clear the flag
                    self._skip_next_map_interaction = False

            elif self.game_state == 'conversation' and getattr(self, 'conversation_scene', None):
                try:
                    self.conversation_scene.update_state()
                except Exception:
                    pass
                try:
                    self.conversation_scene.draw(self.screen)
                except Exception as e:
                    print(f"ERROR: Exception during ConversationScene.draw: {e}", flush=True)

            elif self.game_state == "battle":
                self.battle_scene.update_state()
                self.battle_view.draw(self.battle_scene)

            elif self.game_state == "title":
                self.title_scene.draw(self.screen)
                # transitions from title
                sel = getattr(self.title_scene, 'selected_option', None)
                if sel == 'start':
                    self.game_state = 'map'
                    self.map_scene = MapScene()
                    self.title_scene.selected_option = None
                elif sel == 'quit':
                    self.running = False
                    break
                elif sel == 'bestiary':
                    self.game_state = 'bestiary'
                    self.title_scene.selected_option = None

            elif self.game_state == 'bestiary':
                # allow the scene to update (e.g. scrolling / selection logic)
                try:
                    self.bestiary_scene.update_state()
                except Exception:
                    pass
                self.bestiary_scene.draw(self.screen)
                if getattr(self.bestiary_scene, 'requested_exit', False):
                    self.bestiary_scene.requested_exit = False
                    self.game_state = 'title'

            # battle end handling (kept from original)
            try:
                if self.battle_scene.game_over:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        if self.battle_scene.winner == "player":
                            try:
                                self.map_scene.remove_enemy(self.map_scene.collided_enemy)
                            except Exception:
                                pass
                        self.game_state = "map"
                        self.battle_scene.game_over = False
            except Exception:
                pass

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # 修正: 実行ブロックを追加
    game_controller = GameController()
    game_controller.run()