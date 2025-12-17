# -*- coding: utf-8 -*-
import pygame
import os
from ..config import settings
import os


class MapConversationView:
    def __init__(self, default_background_path: str | None):
        # 日本語フォント探索
        self.font = self._get_japanese_font(26)
        self.speaker_font = self._get_japanese_font(30)
        self.background_image = None
        if default_background_path:
            try:
                self.background_image = pygame.image.load(default_background_path).convert()
                self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            except Exception:
                self.background_image = None

        self.dialogue_text = ""
        self.speaker_name = ""
        self.choices = []
        self.selected_choice_index = 0

        # スピーカー画像群
        self.speaker_images: dict[str, pygame.Surface] = {}
        # 互換で npc.png があれば自動割り当て
        try:
            npc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'npc', 'npc.png'))
            if os.path.exists(npc_path):
                self.set_speaker_image('老人', npc_path)
        except Exception:
            pass

        # アニメーション用状態
        self.npc_animating = False
        self.npc_anim_start_x = 0
        self.npc_anim_target_x = 0
        self.npc_anim_start_time = 0
        self.npc_anim_duration = 400  # ms
        self.npc_anim_completed = False
        # フェード用
        self.npc_alpha = 0
        self.npc_fade_start_time = 0
        self.npc_fade_duration = 200  # ms
        self.npc_desired_visible = False

    def _get_japanese_font(self, size: int) -> pygame.font.Font:
        font_paths = [
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\YuGothM.ttc",
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return pygame.font.Font(p, size)
                except Exception:
                    continue
        return pygame.font.Font(None, size)

    def set_dialogue(self, speaker: str | None, text: str):
        prev_speaker = self.speaker_name
        new_speaker = speaker if speaker else ""
        self.speaker_name = new_speaker
        self.dialogue_text = text
        # NPC画像のスライドイン開始（発言者が変わったときのみアニメーション）
        try:
            img_for_speaker = self.speaker_images.get(new_speaker)
            if img_for_speaker:
                now = pygame.time.get_ticks()
                if prev_speaker != new_speaker:
                    img_w, img_h = img_for_speaker.get_size()
                    margin = settings.SCREEN_WIDTH // 10
                    target_x = settings.SCREEN_WIDTH - margin - img_w
                    # 開始位置をより遠くに設定して完全に画面外からスライドしてくる印象を強める
                    start_x = settings.SCREEN_WIDTH + img_w * 2 + (settings.SCREEN_WIDTH // 5)
                    self.npc_anim_start_x = start_x
                    self.npc_anim_target_x = target_x
                    self.npc_anim_start_time = now
                    self.npc_animating = True
                    self.npc_anim_completed = False
                    # フェードインを開始する
                    self.npc_desired_visible = True
                    self.npc_fade_start_time = now
                    self.npc_alpha = 0
                else:
                    # 同一発言者の継続: アニメーションは再生せず、表示フラグだけ維持
                    self.npc_desired_visible = True
            else:
                now = pygame.time.get_ticks()
                self.npc_desired_visible = False
                self.npc_fade_start_time = now
                self.npc_animating = False
        except Exception:
            self.npc_animating = False

    def set_speaker_image(self, speaker: str, image_path: str):
        try:
            if not os.path.isabs(image_path):
                candidate = os.path.abspath(os.path.join(os.getcwd(), image_path))
            else:
                candidate = image_path
            if not os.path.exists(candidate):
                return
            img = pygame.image.load(candidate).convert_alpha()
            desired_h = int(min(settings.SCREEN_HEIGHT * 0.40, 300))
            w = max(1, img.get_width() * desired_h // max(1, img.get_height()))
            surf = pygame.transform.smoothscale(img, (w, desired_h))
            self.speaker_images[speaker] = surf
        except Exception:
            pass

    def set_choices(self, choices: list[str]):
        self.choices = choices

    def clear_choices(self):
        self.choices = []
        self.selected_choice_index = 0

    def set_selected_choice(self, index: int):
        self.selected_choice_index = index

    def set_background(self, image_path: str | None):
        if not image_path:
            self.background_image = None
            return
        try:
            self.background_image = pygame.image.load(image_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except Exception:
            self.background_image = None

    def draw(self, screen: pygame.Surface):
        # マップの背景をそのままにして、画面下部にログ風パネルを描画する
        try:
            # 全画面半透明オーバーレイ（マップの上、会話UIの下）
            try:
                overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, int(255 * 0.6)))
                screen.blit(overlay, (0, 0))
            except Exception:
                pass
            log_height = int(settings.SCREEN_HEIGHT * 0.28)
            log_rect = pygame.Rect(0, settings.SCREEN_HEIGHT - log_height, settings.SCREEN_WIDTH, log_height)

            panel = pygame.Surface((log_rect.width, log_rect.height), pygame.SRCALPHA)
            panel.fill((12, 12, 16, 220))
            screen.blit(panel, log_rect.topleft)
            pygame.draw.rect(screen, settings.WHITE, log_rect, 1)

            padding = 14
            max_width = log_rect.width - padding * 2

            # 話者を左上に表示
            # 外側に配置する話者名ボックス（ログの左上外側）
            if self.speaker_name:
                speaker_box_width = int(settings.SCREEN_WIDTH * 0.18)
                speaker_box_height = int(settings.SCREEN_HEIGHT * 0.06)
                gap = 8
                outer_x = max(10, log_rect.x + padding - speaker_box_width - gap)
                outer_y = log_rect.y - speaker_box_height - gap
                outer_rect = pygame.Rect(outer_x, outer_y, speaker_box_width, speaker_box_height)
                pygame.draw.rect(screen, (40, 40, 40), outer_rect, border_radius=6)
                pygame.draw.rect(screen, settings.WHITE, outer_rect, 2, border_radius=6)
                s_surf = self.speaker_font.render(self.speaker_name, True, settings.WHITE)
                sx = outer_rect.x + (outer_rect.width - s_surf.get_width()) // 2
                sy = outer_rect.y + (outer_rect.height - s_surf.get_height()) // 2
                screen.blit(s_surf, (sx, sy))

            # 話者が「老人」の場合はログパネルの外側に画像を表示（スライドイン）
            # 表示はアニメーション中か完了している場合のみ行う
            img_for_speaker = self.speaker_images.get(self.speaker_name)
            if img_for_speaker and (self.npc_animating or getattr(self, 'npc_anim_completed', False)):
                img_w, img_h = img_for_speaker.get_size()
                img_y = log_rect.y - 8 - img_h
                if img_y < 8:
                    img_y = 8
                # フェード処理を計算
                try:
                    now_f = pygame.time.get_ticks()
                    if self.npc_fade_start_time:
                        ft = (now_f - self.npc_fade_start_time) / max(1, self.npc_fade_duration)
                        ft = max(0.0, min(1.0, ft))
                        if self.npc_desired_visible:
                            self.npc_alpha = int(255 * ft)
                        else:
                            self.npc_alpha = int(255 * (1.0 - ft))
                except Exception:
                    pass

                # アニメーション中は位置を補間
                if self.npc_animating:
                    now = pygame.time.get_ticks()
                    t = (now - self.npc_anim_start_time) / max(1, self.npc_anim_duration)
                    if t >= 1.0:
                        t = 1.0
                        self.npc_animating = False
                        self.npc_anim_completed = True
                    ease = 1 - pow(1 - t, 3)
                    img_x = int(self.npc_anim_start_x + (self.npc_anim_target_x - self.npc_anim_start_x) * ease)
                else:
                    margin = settings.SCREEN_WIDTH // 10
                    img_x = settings.SCREEN_WIDTH - margin - img_w
                # フェード時はアルファを適用して描画（alpha=0なら描画しない）
                if self.npc_alpha <= 0:
                    pass
                else:
                    try:
                        temp = img_for_speaker.copy()
                        temp.set_alpha(self.npc_alpha)
                        screen.blit(temp, (img_x, img_y))
                    except Exception:
                        screen.blit(img_for_speaker, (img_x, img_y))
                # 画面端補正
                if img_x < 8:
                    img_x = 8
                if img_x + img_w > settings.SCREEN_WIDTH - 8:
                    img_x = settings.SCREEN_WIDTH - img_w - 8

            # テキストを折り返して表示（簡易実装）
            words = self.dialogue_text.split(' ')
            lines = []
            cur = ''
            for w0 in words:
                test = (cur + ' ' + w0).strip() if cur else w0
                if self.font.size(test)[0] <= max_width:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = w0
            if cur:
                lines.append(cur)

            # テキストはログパネルの上寄せで描画（パネル上端から小さく下がった位置）
            start_x = log_rect.x + padding
            # 強制的に上寄せ: 上端からの固定オフセットを使う
            start_y = log_rect.y + 6
            line_height = self.font.get_height() + 6
            for i, line in enumerate(lines[:8]):
                surf = self.font.render(line, True, settings.WHITE)
                screen.blit(surf, (start_x, start_y + i * line_height))

        except Exception:
            pass

        # マップ会話ではここで表示更新を行わない（メインループで1回だけ行う）
