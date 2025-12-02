# -*- coding: utf-8 -*-
from ..data.conversation_data import CONVERSATIONS

class ConversationScene:
    def __init__(self):
        self.conversation_id = None
        self.conversation_data = []
        self.current_line_index = 0
        self.is_finished = False

    def start_conversation(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.conversation_data = CONVERSATIONS.get(conversation_id, [])
        self.current_line_index = 0
        self.is_finished = False

    def advance_conversation(self):
        if self.current_line_index < len(self.conversation_data) - 1:
            self.current_line_index += 1
        else:
            self.is_finished = True