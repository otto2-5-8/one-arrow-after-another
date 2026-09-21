"""检查每个关卡是否可通关，并统计难度信息。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from levels import LEVELS  # noqa: E402
from logic import GameState  # noqa: E402
from solver import free_in, solve  # noqa: E402


def main():
    ok = True
    for i, level in enumerate(LEVELS):
        game = GameState(level)
        order = solve(game.arrows, game.rows, game.cols)
        free = game.free_arrows()
        safe = 0
        for pos in free:
            rest = {p: d for p, d in game.arrows.items() if p != pos}
            if solve(rest, game.rows, game.cols) is not None:
                safe += 1
        mark = "OK " if order and len(order) == game.total else "BAD"
        if not order or len(order) != game.total:
            ok = False
        print(
            f"{mark} {level['name']} {game.rows}x{game.cols} 箭头={game.total} "
            f"初始可飞出={len(free)} 安全着法={safe} 解长度={len(order) if order else 0}"
        )
        if order:
            print("     解法:", " ".join(f"({r},{c})" for r, c in order))
    print("全部关卡检查", "通过" if ok else "存在问题")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
