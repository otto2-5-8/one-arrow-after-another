"""随机生成一定可通关的关卡，供手工挑选后写进 levels.py。

思路：按"消除顺序的逆序"摆放箭头。新摆下的箭头只要不在已摆箭头的射线
上，那么按相反顺序点击就一定都能飞出，因此生成的布局必然有解。
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic import DIRS  # noqa: E402
from solver import solve  # noqa: E402


def reachable(pos, direction, rows, cols):
    dr, dc = DIRS[direction]
    r, c = pos[0] + dr, pos[1] + dc
    cells = []
    while 0 <= r < rows and 0 <= c < cols:
        cells.append((r, c))
        r += dr
        c += dc
    return cells


def generate(rows, cols, count, seed):
    rng = random.Random(seed)
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    placed = {}
    for _ in range(count):
        rng.shuffle(cells)
        ok = False
        for pos in cells:
            if pos in placed:
                continue
            for direction in rng.sample("^v<>", 4):
                ray = reachable(pos, direction, rows, cols)
                if any(p in placed for p in ray):
                    continue
                placed[pos] = direction
                ok = True
                break
            if ok:
                break
        if not ok:
            break
    order = solve(placed, rows, cols)
    assert order and len(order) == len(placed), "生成结果不可解"
    return placed


def to_grid(placed, rows, cols):
    rows_txt = []
    for r in range(rows):
        rows_txt.append("".join(placed.get((r, c), ".") for c in range(cols)))
    return rows_txt


if __name__ == "__main__":
    spec = [(5, 5, 7, 11), (5, 5, 9, 23), (6, 6, 12, 37), (6, 6, 15, 51), (7, 7, 18, 77)]
    for rows, cols, count, seed in spec:
        placed = generate(rows, cols, count, seed)
        print(f"# {rows}x{cols}, {count} 箭头, seed={seed}")
        for line in to_grid(placed, rows, cols):
            print(f'        "{line}",')
        print()
