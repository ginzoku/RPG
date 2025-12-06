# -*- coding: utf-8 -*-
import pygame
from ..data.conversation_data import CONVERSATIONS
from ..views.conversation_view import ConversationView
from ..components.character import Character
from ..config import settings

class ConversationScene:
    def __init__(self, player: Character, conversation_id: str, callback_on_finish):
        self.player = player
        self.conversation_id = conversation_id
        self.callback_on_finish = callback_on_finish
        self.conversation_data = CONVERSATIONS.get(conversation_id)
        if not self.conversation_data:
            raise ValueError(f"Conversation ID '{conversation_id}' not found in CONVERSATIONS.")

        self.current_event_index = 0
        self.is_finished = False
        self.view = ConversationView(self.conversation_data["default_background"])
        self.current_choices = [] # 現在表示されている選択肢
        self.selected_choice_index = 0 # 選択中の選択肢のインデックス
        self.result_effects = None # 会話終了時に返す効果

        # 会話の最初のイベントを表示
        self._show_current_event()

    def _show_current_event(self):
        event = self.conversation_data["events"][self.current_event_index]
        self.view.set_dialogue(event.get("speaker"), event["text"])

        # eventに'background'キーがあればそれを使い、なければdefault_backgroundを試す
        if 'background' in event:
            self.view.set_background(event['background'])
        else:
            self.view.set_background(self.conversation_data.get('default_background'))

        # 選択肢がある場合
        if "choices" in event:
            self.current_choices = event["choices"]
            self.view.set_choices([choice["text"] for choice in self.current_choices])
            self.view.set_selected_choice(self.selected_choice_index)
        else:
            self.current_choices = []
            self.view.clear_choices()


    def process_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self.current_choices: # 選択肢が表示されている場合
                if event.key == pygame.K_UP:
                    self.selected_choice_index = (self.selected_choice_index - 1) % len(self.current_choices)
                    self.view.set_selected_choice(self.selected_choice_index)
                elif event.key == pygame.K_DOWN:
                    self.selected_choice_index = (self.selected_choice_index + 1) % len(self.current_choices)
                    self.view.set_selected_choice(self.selected_choice_index)
                elif event.key == pygame.K_RETURN:
                    self._process_choice()
            else: # 選択肢がない場合、Enterで次の会話へ
                if event.key == pygame.K_RETURN:
                    self._go_to_next_event()

    def _process_choice(self):
        selected_choice = self.current_choices[self.selected_choice_index]
        self.result_effects = {"effects": selected_choice.get("effects", [])}
        
        # 選択肢にnext_event_indexが指定されていればそこにジャンプ
        if "next_event_index" in selected_choice:
            self.current_event_index = selected_choice["next_event_index"]
            # 選択肢をクリア
            self.current_choices = []
            self.view.clear_choices()
            self._show_current_event()
        else:
            # next_event_indexがなければ会話終了
            self._finish_conversation()

    def _go_to_next_event(self):
        self.current_event_index += 1
        if self.current_event_index < len(self.conversation_data["events"]):
            self._show_current_event()
        else:
            self._finish_conversation()

    def _finish_conversation(self):
        self.is_finished = True
        self.callback_on_finish(self.result_effects) # コールバックを呼び出して終了

    def update_state(self):
        # 会話シーン自体は状態変化が少ないため、現状は特に何もしない
        pass

    def draw(self, screen):
        self.view.draw(screen)
