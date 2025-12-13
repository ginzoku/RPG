# -*- coding: utf-8 -*-
import pygame
from ..views.title_view import TitleView
from ..config import settings


class TitleScene:
    """シンプルなタイトル画面のシーンクラス。

    - `selected_option` は 'start' / 'quit' / None を持つ。
    - 外部（GameController）がこの値を見て遷移を行う。
    """
    def __init__(self):
        self.view = TitleView()
        self.selected_option: str | None = None

    def process_input(self, event: pygame.event.Event):
        # View にイベント処理を委譲し、選択結果を受け取る
        result = self.view.handle_event(event)
        if result:
            self.selected_option = result

    def update_state(self):
        # タイトル画面では定期更新は不要だが、アニメーション等を入れる余地あり
        pass

    def draw(self, screen: pygame.Surface):
        self.view.draw(screen)
