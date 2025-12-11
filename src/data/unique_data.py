# -*- coding: utf-8 -*-
"""
ユニーク（特技）データ定義
各ユニークはゲーム内で一意のIDを持ち、発動するカード（action_id）とクールダウンを持ちます。
"""

# デフォルトのユニークID（現在は1個）
DEFAULT_UNIQUE_ID = 'unique_blast'

UNIQUE_ABILITIES = {
    'unique_blast': {
        'id': 'unique_blast',
        'name': '天破の一撃',
        'action_id': 'unique_blast',
        'cooldown': 3,  # 使用後に3ターンのクールダウン
    },
    'unique_storm': {
        'id': 'unique_storm',
        'name': '嵐の舞',
        'action_id': 'unique_storm',
        'cooldown': 4,
    },
}
