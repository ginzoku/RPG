# -*- coding: utf-8 -*-

# ゲーム設定
SCREEN_WIDTH: int = 1000
SCREEN_HEIGHT: int = 600
FPS: int = 60

# フォントサイズ
FONT_SIZES: dict[str, int] = {
    "large": 48,
    "medium": 36,
    "small": 24,
    "log": 20,
    "card": 18,
    "name":16,
    "bar": 12,
}

# アニメーション設定
ANIMATION_SETTINGS: dict[str, dict] = {
    "damage_indicator": {
        "duration": 0.5,
        "jump_height": 40,
    },
    "enemy_attack_slide": {
        "duration": 0.2, # seconds
        "distance": 20, # pixels
    },
    "enemy_shake": {
        "duration": 0.2, # seconds
        "amplitude": 10, # pixels
        "frequency_factor": 4, # for math.sin(progress * math.pi * frequency_factor)
    },
    "hit_slide": { # New setting for hit animation
        "duration": 0.1, # seconds
        "distance": 20, # pixels
    }
}


# 色定義
BLACK: tuple[int, int, int] = (0, 0, 0)
WHITE: tuple[int, int, int] = (255, 255, 255)
GRAY: tuple[int, int, int] = (128, 128, 128)
DARK_GRAY: tuple[int, int, int] = (64, 64, 64)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
BLUE: tuple[int, int, int] = (0, 100, 255)
YELLOW: tuple[int, int, int] = (255, 255, 0)
LIGHT_BLUE: tuple[int, int, int] = (100, 200, 255)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (211, 211, 211)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# 新しく追加
DAMAGE_RED = (255, 80, 80)
BUTTON_COLOR = (255, 80, 80)
