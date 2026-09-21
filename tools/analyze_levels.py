"""统计每个关卡的难度指标：初始可飞出数、通关顺序总数、求解搜索过的局面数。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from levels import LEVELS  # noqa: E402
from logic import GameState  # noqa: E402
from solver import analyze  # noqa: E402


def main():
    print("| 关卡 | 棋盘 | 箭头数 | 初始可飞出 | 通关顺序总数 | 搜索过的局面数 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for level in LEVELS:
        game = GameState(level)
        info = analyze(game.arrows, game.rows, game.cols)
        print(
            f"| {level['name']} | {game.rows} × {game.cols} | {info['arrows']} "
            f"| {info['first_free']} | {info['orders']} | {info['states']} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
