# -*- coding: utf-8 -*-
import pygame
from ..scenes.conversation_scene import ConversationScene

class ConversationController:
    def handle_input(self, events: list[pygame.event.Event], conversation_scene: ConversationScene):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    conversation_scene.advance_conversation()