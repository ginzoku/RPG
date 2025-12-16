# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings
import os

class ConversationView:
    def __init__(self, default_background_path: str | None):
        self.font = self._get_japanese_font(24)
        self.speaker_font = self._get_japanese_font(28)
        
        # UIの相対的なサイズと位置を定義
        dialogue_box_height = int(settings.SCREEN_HEIGHT * 0.25)
        dialogue_box_margin_x = int(settings.SCREEN_WIDTH * 0.05)
        dialogue_box_y = settings.SCREEN_HEIGHT - dialogue_box_height - int(settings.SCREEN_HEIGHT * 0.05)

        self.dialogue_box_rect = pygame.Rect(
            dialogue_box_margin_x,
            dialogue_box_y,
            settings.SCREEN_WIDTH - (dialogue_box_margin_x * 2),
            dialogue_box_height
        )

        speaker_box_height = int(settings.SCREEN_HEIGHT * 0.05)
        speaker_box_width = int(settings.SCREEN_WIDTH * 0.2)
        speaker_box_y_offset = int(settings.SCREEN_HEIGHT * 0.01)
        self.speaker_rect = pygame.Rect(
            dialogue_box_margin_x,
            dialogue_box_y - speaker_box_height - speaker_box_y_offset,
            speaker_box_width,
            speaker_box_height
        )

        # 外側に表示するスピーカーボックス（ダイアログボックスの左上外側）
        gap = 10
        outer_x = max(10, dialogue_box_margin_x - speaker_box_width - gap)
        outer_y = dialogue_box_y - speaker_box_height - speaker_box_y_offset
        self.speaker_outer_rect = pygame.Rect(
            outer_x,
            outer_y,
            speaker_box_width,
            speaker_box_height
        )

        self.speaker_name = ""
        self.dialogue_text = ""
        self.choices = []
        self.selected_choice_index = 0
        
        self.background_image = None
        if default_background_path:
            self.set_background(default_background_path)

        # npc画像（老人用）を準備
        self.npc_image = None
        try:
            npc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'npc', 'npc.png'))
            if os.path.exists(npc_path):
                img = pygame.image.load(npc_path).convert_alpha()
                # より大きく表示: 画面高さの最大40%または300pxまで（拡大要求対応）
                desired_h = int(min(settings.SCREEN_HEIGHT * 0.40, 300))
                w = max(1, img.get_width() * desired_h // max(1, img.get_height()))
                self.npc_image = pygame.transform.smoothscale(img, (w, desired_h))
        except Exception:
            self.npc_image = None
    
    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def set_dialogue(self, speaker: str | None, text: str):
        self.speaker_name = speaker if speaker else ""
        self.dialogue_text = text

    def set_choices(self, choices: list[str]):
        self.choices = choices

    def clear_choices(self):
        self.choices = []
        self.selected_choice_index = 0

    def set_selected_choice(self, index: int):
        self.selected_choice_index = index

    def set_background(self, image_path: str | None):
        if image_path is None:
            self.background_image = None
            return

        try:
            full_path = image_path # 仮定: image_pathはすでにフルパスか、または適切に解決されるパス
            self.background_image = pygame.image.load(full_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image {image_path}: {e}")
            self.background_image = None # ロード失敗時は背景なし

    def draw(self, screen):
        # 背景の描画
        if self.background_image:
            screen.blit(self.background_image, (0, 0))

        # 会話中の全画面半透明オーバーレイ（マップの上、会話UIの下に表示される）
        try:
            overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(255 * 0.6)))
            screen.blit(overlay, (0, 0))
        except Exception:
            pass

        # 外側の話者名ボックスを描画（ダイアログボックスの左上の外側）
        if self.speaker_name:
            pygame.draw.rect(screen, (40, 40, 40), self.speaker_outer_rect, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), self.speaker_outer_rect, 2, border_radius=6)
            outer_surf = self.speaker_font.render(self.speaker_name, True, (255, 255, 255))
            # ボックス内で中央寄せして描画
            x_off = self.speaker_outer_rect.x + (self.speaker_outer_rect.width - outer_surf.get_width()) // 2
            y_off = self.speaker_outer_rect.y + (self.speaker_outer_rect.height - outer_surf.get_height()) // 2
            screen.blit(outer_surf, (x_off, y_off))

        # ダイアログボックスの描画
        pygame.draw.rect(screen, (0, 0, 0, 180), self.dialogue_box_rect, border_radius=10) # 半透明の黒
        pygame.draw.rect(screen, (255, 255, 255), self.dialogue_box_rect, 2, border_radius=10) # 枠線

        # 話者が「老人」の場合、右上にNPC画像を表示
        try:
            if self.speaker_name == '老人' and self.npc_image:
                pad = 8
                img_w, img_h = self.npc_image.get_size()
                # 画面を10分割したとき、画像の右端から画面右端まで1/10分の余白を確保する
                margin = settings.SCREEN_WIDTH // 10
                img_x = settings.SCREEN_WIDTH - margin - img_w
                img_y = self.dialogue_box_rect.y - pad - img_h
                # 画面外に出ないように調整
                if img_y < 8:
                    img_y = 8
                if img_x < 8:
                    img_x = 8
                if img_x + img_w > settings.SCREEN_WIDTH - 8:
                    img_x = settings.SCREEN_WIDTH - img_w - 8
                screen.blit(self.npc_image, (img_x, img_y))
        except Exception:
            pass


        # ダイアログテキストの描画（左上に寄せて折返し表示）
        padding = 10
        max_width = self.dialogue_box_rect.width - padding * 2
        words = self.dialogue_text.split(' ')
        lines = []
        cur = ''
        for w in words:
            test = (cur + ' ' + w).strip() if cur else w
            if self.font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        # テキストはダイアログボックスの上寄せで描画（ボックス上端から小さく下がった位置）
        start_x = self.dialogue_box_rect.x + padding
        # 強制的に上寄せ: 上端からの固定オフセットを使う
        start_y = self.dialogue_box_rect.y + 6
        line_height = self.font.get_height() + 6
        for i, line in enumerate(lines[:8]):
            surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(surf, (start_x, start_y + i * line_height))

        # 選択肢の描画（本文の下に続けて表示）
        if self.choices:
            choice_start_x = self.dialogue_box_rect.x + padding
            # 選択肢は本文行の直下から描画
            choice_start_y = start_y + len(lines[:8]) * line_height + 8
            choice_line_height = self.font.get_height() + 10
            for i, choice_text in enumerate(self.choices):
                color = (255, 255, 0) if i == self.selected_choice_index else (255, 255, 255)
                choice_surface = self.font.render(f"> {choice_text}" if i == self.selected_choice_index else choice_text, True, color)
                screen.blit(choice_surface, (choice_start_x, choice_start_y + i * choice_line_height))
